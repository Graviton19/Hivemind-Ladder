import os
import time
import logging
import threading
from typing import Optional
from openai import OpenAI, RateLimitError, APIConnectionError, APITimeoutError, InternalServerError
from tenacity import (
    retry, stop_after_attempt,
    retry_if_exception_type, before_sleep_log,
)
from tenacity.wait import wait_base

logger = logging.getLogger(__name__)

_RETRYABLE = (RateLimitError, APIConnectionError, APITimeoutError, InternalServerError)

_MIN_BACKOFF_S = 15.0


class _WaitRateLimitAware(wait_base):
    def __call__(self, retry_state) -> float:
        exc = retry_state.outcome.exception()
        if isinstance(exc, RateLimitError):
            retry_after = float(getattr(exc, "retry_after", None) or _MIN_BACKOFF_S)
            wait = max(retry_after, _MIN_BACKOFF_S)
            logger.warning(f"429 rate limit — waiting {wait:.0f}s before retry")
            return wait
        
        return min(5 * 2 ** (retry_state.attempt_number - 1), 120)


class AdaptiveRateLimiter:
    _INITIAL_RPM = 20.0
    _MIN_RPM = 3.0
    _SUCCESS_THRESHOLD = 50
    _SCALE_UP = 1.2
    _SCALE_DOWN = 0.5

    def __init__(self):
        self._lock = threading.Lock()
        self.current_rpm = self._INITIAL_RPM
        self._consecutive_successes = 0
        self._last_request_time = 0.0
        self._request_count = 0
        self._window_start = time.time()

    @property
    def _interval(self) -> float:
        return 60.0 / self.current_rpm

    def wait(self):
        with self._lock:
            now = time.time()

            if now - self._window_start >= 60.0:
                self._request_count = 0
                self._window_start = now

            if self._request_count >= self.current_rpm:
                sleep_time = 60.0 - (now - self._window_start) + 1.0
                if sleep_time > 0:
                    logger.debug(f"Rate window full — sleeping {sleep_time:.1f}s")
                    time.sleep(sleep_time)
                self._request_count = 0
                self._window_start = time.time()

            now = time.time()
            elapsed = now - self._last_request_time
            if elapsed < self._interval:
                time.sleep(self._interval - elapsed)

            self._last_request_time = time.time()
            self._request_count += 1

    def on_success(self):
        with self._lock:
            self._consecutive_successes += 1
            if self._consecutive_successes >= self._SUCCESS_THRESHOLD:
                self.current_rpm = self.current_rpm * self._SCALE_UP
                self._consecutive_successes = 0
                logger.info(f"Adaptive limiter: ramping up to {self.current_rpm:.1f} RPM")

    def on_rate_limit(self):
        with self._lock:
            old = self.current_rpm
            self.current_rpm = max(old * self._SCALE_DOWN, self._MIN_RPM)
            self._consecutive_successes = 0
            logger.warning(f"Adaptive limiter: 429 — dropping {old:.1f} → {self.current_rpm:.1f} RPM")


class FireworksClient:

    def __init__(self, config):
        api_key = os.environ.get("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError(
                "FIREWORKS_API_KEY not set. "
                "Get one at https://fireworks.ai and run: "
                "export FIREWORKS_API_KEY='your-key'"
            )

        self.client = OpenAI(
            api_key=api_key,
            base_url=config.base_url,
        )
        self.config = config
        self.rate_limiter = AdaptiveRateLimiter()

        self.total_requests = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
        self.total_errors = 0
        self.start_time = time.time()

    @retry(
        retry=retry_if_exception_type(_RETRYABLE),
        stop=stop_after_attempt(7),
        wait=_WaitRateLimitAware(),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True,
    )
    def _call_api(
        self,
        messages: list,
        temperature: float,
        max_tokens: int,
    ) -> str:
        self.rate_limiter.wait()

        try:
            response = self.client.chat.completions.create(
                model=self.config.model_id,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=self.config.top_p,
            )

            self.total_requests += 1
            if response.usage:
                self.total_input_tokens += response.usage.prompt_tokens
                self.total_output_tokens += response.usage.completion_tokens

            text = response.choices[0].message.content
            self.rate_limiter.on_success()
            return text.strip() if text else ""

        except RateLimitError as e:
            self.total_errors += 1
            self.rate_limiter.on_rate_limit()
            logger.error(f"API error (will retry): {e}")
            raise
        except _RETRYABLE as e:
            self.total_errors += 1
            logger.error(f"API error (will retry): {e}")
            raise
        except Exception as e:
            self.total_errors += 1
            logger.error(f"Non-retryable API error: {e}")
            raise

    def generate(
        self,
        user_content: str,
        system_content: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        messages = []
        if system_content:
            messages.append({"role": "system", "content": system_content})
        messages.append({"role": "user", "content": user_content})

        return self._call_api(
            messages=messages,
            temperature=temperature or self.config.temperature,
            max_tokens=max_tokens or self.config.max_tokens,
        )

    def get_stats(self) -> dict:
        elapsed = time.time() - self.start_time
        input_cost = self.total_input_tokens * 0.20 / 1_000_000
        output_cost = self.total_output_tokens * 0.20 / 1_000_000

        return {
            "total_requests": self.total_requests,
            "total_errors": self.total_errors,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "estimated_cost_usd": round(input_cost + output_cost, 4),
            "elapsed_seconds": round(elapsed, 1),
            "requests_per_minute": round(self.total_requests / (elapsed / 60), 1) if elapsed > 0 else 0,
            "current_rpm_limit": round(self.rate_limiter.current_rpm, 1),
        }

    def print_stats(self):
        s = self.get_stats()
        print(f"\n{'='*50}")
        print(f"API Usage Summary")
        print(f"{'='*50}")
        print(f"  Requests:      {s['total_requests']} ({s['total_errors']} errors)")
        print(f"  Input tokens:  {s['total_input_tokens']:,}")
        print(f"  Output tokens: {s['total_output_tokens']:,}")
        print(f"  Est. cost:     ${s['estimated_cost_usd']:.4f}")
        print(f"  Time:          {s['elapsed_seconds']:.0f}s ({s['requests_per_minute']:.0f} req/min)")
        print(f"  Final RPM cap: {s['current_rpm_limit']:.1f} RPM")
        print(f"{'='*50}")
