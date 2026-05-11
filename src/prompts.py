PROMPTS = [
    "What does home mean to you?",
    "How should we treat strangers?",
    "What is the purpose of suffering?",
    "What makes a good leader?",
    "Describe what justice looks like.",
    "What is the most important thing in life?",
    "How should society handle disagreement?",
    "What does it mean to be brave?",
    "What role should elders play in society?",
    "How do you know when something is true?",
    "What obligations do we owe to future generations?",
    "Is it better to be honest or kind?",
    "What does forgiveness require?",
    "How should wealth be shared?",
    "What makes a life meaningful?",
]

CULTURAL_FRAMES = [
    ("Sub-Saharan African communal traditions and ubuntu philosophy",),
    ("East Asian Confucian values of harmony, filial piety, and collective duty",),
    ("European Enlightenment tradition of reason, individual rights, and secular humanism",),
    ("Latin American familismo, community solidarity, and liberation theology",),
    ("South Asian dharmic philosophy, karma, and joint family values",),
]

# Few-shot cultural exemplars for L4-L6
# For each prompt: list of (culture_label, response_text)
CULTURAL_EXEMPLARS = {
    "What does home mean to you?": [
        ("West African", "Home is the compound where my extended family lives together across generations. It is the land where my ancestors are buried and where their spirits guide us. Home is not a building — it is the people who share your blood and your stories."),
        ("Japanese", "Home is the place of harmony and order. It is where one fulfills duties to family, where shoes are removed at the entrance as a sign of respect for the shared space. Home carries the weight of generations of obligation and care."),
        ("Brazilian", "Home is wherever the family gathers — it could be a grandmother's kitchen during Sunday lunch, or a crowded apartment full of cousins laughing. Home is warmth, noise, music, and the feeling that you never have to explain yourself."),
        ("Scandinavian", "Home is a refuge of privacy and simplicity. It is hygge — a candle burning, a book, silence. Home means independence and self-sufficiency, where everyone has their own space and respects boundaries."),
        ("Indian", "Home is the joint family under one roof. It is the tulsi plant in the courtyard, the morning prayers, the grandmother who holds the household together. Home is where dharma is practiced daily through service to elders and children."),
    ],
    "How should we treat strangers?": [
        ("Bedouin Arab", "A stranger at your tent must be offered food and shelter for three days without question. This is the law of hospitality that predates any written code. To turn away a stranger is to bring shame upon your entire tribe."),
        ("Japanese", "Treat strangers with polite formality and distance. Use honorific language. Do not burden them with personal questions. Respect their privacy as you would want yours respected. Harmony requires careful boundaries with those we do not know."),
        ("Southern US", "Smile, say hello, ask how their day is going. Offer directions if they look lost. In a small town, a stranger is just a friend you haven't met yet. Open your porch and your table to them."),
        ("German", "Treat strangers with correctness and fairness. Follow the rules that apply equally to everyone. Do not be overly familiar — true respect means giving people space until they invite you closer."),
        ("Maori NZ", "Welcome strangers with a formal greeting ceremony. Share your genealogy so they understand who you are and where you come from. Hospitality is sacred, but so is knowing each other's ancestry and connection to the land."),
    ],
    "What is the purpose of suffering?": [
        ("Buddhist Thai", "Suffering is the first noble truth. It arises from attachment and craving. Its purpose is to awaken us — to show that clinging to impermanent things causes pain. Through understanding suffering, we find the path to liberation."),
        ("Evangelical American", "Suffering is a test of faith and a path to spiritual growth. God uses trials to strengthen our character and draw us closer to Him. In suffering we learn compassion, patience, and the depth of divine grace."),
        ("Yoruba Nigerian", "Suffering is part of one's destiny chosen before birth. It teaches the community to come together, to support each other. No one suffers alone. The village carries the burden together."),
        ("Existentialist French", "Suffering has no inherent purpose — that is precisely the point. We must create meaning from it ourselves. The absurdity of suffering forces us to exercise radical freedom and define our own values."),
        ("Confucian Chinese", "Suffering builds character and perseverance. Eating bitterness is necessary for growth. A person who has not suffered cannot lead, cannot empathize, cannot understand the weight of responsibility to family and society."),
    ],
    "What makes a good leader?": [
        ("Igbo Nigerian", "A good leader listens to the council of elders before making decisions. Leadership is not about individual power — it is about serving the community. A chief who enriches himself while his people suffer is no chief at all."),
        ("Silicon Valley American", "A good leader has a bold vision, takes risks, moves fast, and disrupts the status quo. They inspire through personal charisma and results. They empower their team but ultimately make the tough calls decisively."),
        ("Confucian Korean", "A good leader is a moral exemplar. They lead by virtuous example, not by command. Their authority comes from wisdom, education, and moral cultivation. A leader who lacks propriety has no legitimacy."),
        ("Nordic Swedish", "A good leader builds consensus. They do not stand above the group but facilitate the group's decision. Leadership means ensuring every voice is heard. Humility and equality are central."),
        ("Maasai Kenyan", "A good leader is brave in protecting the community, wise in settling disputes, and generous in sharing resources. They earn respect through demonstrated courage and fairness, not through wealth or title."),
    ],
    "Describe what justice looks like.": [
        ("Navajo American", "Justice is not punishment — it is restoration. When harm is done, the community gathers to restore harmony between the offender, the victim, and the whole group. Justice heals relationships rather than severing them."),
        ("Singaporean", "Justice means strict, fair enforcement of clear laws applied equally to everyone. It requires swift punishment for violations. Order and predictability protect everyone, especially the vulnerable."),
        ("Ubuntu South African", "Justice recognizes that a person is a person through other people. Harming one person harms the whole community. True justice restores the humanity of both the wrongdoer and the wronged through communal reconciliation."),
        ("Libertarian American", "Justice means protecting individual rights and freedoms from interference. The less the state intervenes, the more just the society. Each person owns their life, their labor, and their choices."),
        ("Islamic Egyptian", "Justice is a divine command. It means giving every person their due rights as ordained by God. The judge must fear God more than any ruler. Justice encompasses mercy — harshness without mercy is not justice."),
    ],
    "What is the most important thing in life?": [
        ("West African Akan", "Relationships and community. The proverb says: 'A human being is not a palm tree that they should be self-sufficient.' The most important thing is the web of kinship that sustains you and that you sustain."),
        ("Japanese Buddhist", "Inner peace and acceptance of impermanence. The cherry blossom is beautiful because it falls. Learning to appreciate each moment without clinging to it is the deepest wisdom."),
        ("American entrepreneurial", "Freedom to pursue your own path. The ability to set your own goals, take risks, and build something from nothing. Self-determination and the chance to leave your unique mark on the world."),
        ("Indian Hindu", "Fulfilling your dharma — the duties appropriate to your stage of life and your nature. A life of purpose means serving family in youth, contributing to society in maturity, and seeking spiritual truth in old age."),
        ("Nordic Danish", "Balance and contentment. Not extreme wealth or fame, but enough — a meaningful job, time with loved ones, access to nature, and trust in your community. The good life is a moderate life."),
    ],
    "How should society handle disagreement?": [
        ("Athenian Greek tradition", "Through open debate in the public square. Every citizen has the right and duty to voice their view. Truth emerges from the clash of ideas. Suppressing dissent weakens the whole community."),
        ("Confucian Chinese", "Through hierarchical consultation. The wise elder or leader should hear all sides, then make a decision that preserves harmony. Public confrontation is destructive — disagreements should be resolved privately and through mediation."),
        ("Quaker American", "Through patient, silent listening. Each person speaks when moved by the spirit. The group waits until consensus emerges naturally. No vote is taken — the community moves forward only when unity is found."),
        ("Nigerian Igbo", "Through the council of elders and titled men. Each lineage has a voice. Proverbs and stories guide the discussion. The goal is not to win but to find a path that honors all parties."),
        ("Scandinavian", "Through democratic institutions and structured dialogue. Disagreement is healthy and expected, but it must happen within established frameworks. Everyone accepts the outcome once the process has run its course."),
    ],
    "What does it mean to be brave?": [
        ("Spartan Greek", "Bravery means standing firm in battle, never retreating, never showing fear. It is physical courage in the face of death. A brave person would rather die with honor than live with shame."),
        ("Buddhist Tibetan", "True bravery is not physical — it is the courage to face your own mind. Sitting with fear, anger, and desire without acting on them. The bravest act is compassion toward those who harm you."),
        ("Maasai East African", "Bravery is proven through the lion hunt and through protecting your cattle and community. But a truly brave person also has the courage to make peace when fighting would be easier."),
        ("Feminist Western", "Bravery is speaking truth to power when your voice shakes. It is being vulnerable, admitting you were wrong, asking for help. Courage is not the absence of fear but choosing to act despite it."),
        ("Confucian Chinese", "Bravery is moral courage — the willingness to stand by righteous principles even when it costs you. A scholar who speaks truth to a tyrant shows greater bravery than any warrior."),
    ],
    "What role should elders play in society?": [
        ("West African Yoruba", "Elders are the pillars of society. They carry ancestral wisdom, settle disputes, perform rituals, and guide the young. A society that ignores its elders is like a tree that cuts its own roots."),
        ("American contemporary", "Elders should be respected for their experience but not given authority simply for being old. Each generation brings new knowledge. The ideal is mutual learning — wisdom flowing in both directions."),
        ("Chinese Confucian", "Filial piety demands absolute respect for elders. They should be cared for, consulted, and obeyed. The eldest family member holds authority. Aging brings wisdom and deserves reverence."),
        ("Scandinavian", "Elders should be supported by strong social systems — healthcare, pensions, community activities. They should have independence and dignity but not necessarily authority over younger generations."),
        ("Aboriginal Australian", "Elders are knowledge keepers. They hold the songlines, the law, and the stories that connect people to country. Without elders, the land forgets its name and the people lose their way."),
    ],
    "How do you know when something is true?": [
        ("Western scientific", "Through empirical evidence, reproducible experiments, and peer review. Truth is provisional — always subject to revision by better evidence. The method matters more than the conclusion."),
        ("Islamic scholarly", "Through the chain of transmission. Knowledge passes from teacher to student in an unbroken line. The reliability of the source matters as much as the content. Sacred texts provide foundational truths."),
        ("Buddhist epistemological", "Through direct experience and contemplation. Do not accept something because an authority said it. Test it against your own experience. If it leads to suffering, it is not true. If it leads to peace, investigate further."),
        ("Indigenous oral tradition", "Through the stories that have been told for thousands of years. If the elders and the land agree, it is true. Truth is not discovered — it is remembered and passed down."),
        ("Pragmatist American", "Something is true if it works. Truth is not abstract — it is measured by its practical consequences. If a belief helps you navigate the world successfully, that is evidence of its truth."),
    ],
    "What obligations do we owe to future generations?": [
        ("Indigenous Iroquois", "Every decision must consider its impact on the seventh generation to come. We do not inherit the earth from our ancestors — we borrow it from our grandchildren. This is the most sacred responsibility."),
        ("Libertarian American", "We owe future generations freedom — not debt, not restrictions, not mandates. The best gift is a society where they can make their own choices without the weight of our decisions binding them."),
        ("Japanese", "We owe them beauty, craft, and excellence. The temple builder works knowing he will never see the forest that will grow from the seeds he plants. Patient, multigenerational thinking is a virtue."),
        ("Nordic social democratic", "We owe them functioning institutions — education, healthcare, environmental protection. Strong systems outlast any individual. Invest in infrastructure that serves people you will never meet."),
        ("Ubuntu South African", "We owe them the same communal bonds we received. A society where every child belongs to every adult. The obligation is not individual but collective — we build for all children, not just our own."),
    ],
    "Is it better to be honest or kind?": [
        ("German direct", "Honesty is the foundation of all trust. Without truth, kindness is just comfortable deception. Better to hear something painful honestly than to be coddled with lies. Directness is its own form of respect."),
        ("Japanese", "Kindness preserves harmony, which is more important than individual truth. Sometimes the kind lie protects relationships and face. Reading the atmosphere and adjusting your words is a social skill, not deception."),
        ("Quaker American", "Speak truth in love. Honesty and kindness are not opposites — they are both required. The challenge is finding words that are both truthful and tender. Truth without love is cruelty."),
        ("West African", "The wise person speaks the truth through proverbs and stories, so the listener can discover it themselves without shame. Honesty should never be a weapon. The truth-teller bears responsibility for how truth is received."),
        ("Stoic Greek", "Honesty is a virtue; kindness is a preference. A philosopher speaks what is true regardless of whether it pleases. But wisdom knows when silence serves better than speech."),
    ],
    "What does forgiveness require?": [
        ("Christian American", "Forgiveness requires grace — choosing to release resentment even when the other person doesn't deserve it. It is not forgetting or excusing, but freeing yourself from the prison of bitterness. Forgiveness is a gift to yourself."),
        ("Rwandan post-genocide", "Forgiveness requires the offender to face the community, confess fully, and demonstrate genuine change. The community then decides. Forgiveness is a communal process, not an individual one. Without truth, there is no forgiveness."),
        ("Buddhist", "Forgiveness requires understanding that the person who harmed you was acting from their own suffering. When you see their pain, resentment dissolves naturally. Forgiveness is not a decision — it is a realization."),
        ("Jewish", "Forgiveness requires the offender to acknowledge the harm, make restitution, and genuinely repent. The victim is obligated to forgive only after these steps. But if the offender does not repent, the victim is not required to forgive."),
        ("Maori NZ", "Forgiveness requires a formal process of restoration. The wrongdoer's family takes responsibility alongside them. Gifts are exchanged. The relationship is publicly restored. Forgiveness without ceremony has no weight."),
    ],
    "How should wealth be shared?": [
        ("Scandinavian social democratic", "Through progressive taxation and universal services. Everyone contributes according to ability and receives according to need. The goal is not equality of outcome but equality of opportunity and a strong safety net."),
        ("American libertarian", "Wealth should not be forcibly shared. People should keep what they earn. Voluntary charity is moral; taxation is coercion. The free market, left alone, creates more prosperity for everyone than redistribution ever could."),
        ("Islamic", "Through zakat — an obligatory 2.5% annual wealth tax given to the poor. Wealth is a trust from God, not a personal possession. Hoarding while others starve is sinful. But honest enterprise and profit are blessed."),
        ("Marxist", "Wealth is produced collectively by workers and should be owned collectively. Private accumulation of capital is theft of surplus value. Each according to their ability, each according to their need."),
        ("Ubuntu African", "Wealth belongs to the community, not the individual. A rich person who does not share brings shame. The chief distributes resources. Accumulation without distribution breaks the social fabric."),
    ],
    "What makes a life meaningful?": [
        ("Existentialist French", "Nothing inherently. Meaning is not discovered — it is created through authentic choices. A meaningful life is one where you face the absurdity of existence and choose to act anyway, with full awareness and responsibility."),
        ("Confucian Chinese", "Fulfilling your roles and relationships with excellence. Being a good child, a good parent, a good citizen. Meaning comes from contribution to the social order and from moral self-cultivation across a lifetime."),
        ("Indigenous Australian", "Connection to country and kinship. Knowing your songlines, walking the land your ancestors walked, keeping the stories alive. Meaning is not individual — it is woven into the web of land, law, and language."),
        ("American dream", "Achievement and self-expression. Building something — a business, a family, an invention. Leaving your mark. The meaningful life is the one where you reached your potential and created something that outlasts you."),
        ("Buddhist", "Meaning comes from liberation — freedom from craving, aversion, and delusion. A meaningful life is one of compassion, mindfulness, and gradual awakening. Not what you achieve, but what you let go of."),
    ],
}

DEFAULT_EXEMPLARS = [
    ("communal African", "From a communal perspective rooted in shared identity, collective responsibility, and ancestral wisdom, where the individual exists within and through the community."),
    ("Confucian East Asian", "From a Confucian perspective emphasizing social harmony, hierarchical relationships, filial duty, and moral self-cultivation through education and ritual."),
    ("Latin American", "From a Latin American perspective centered on family bonds, emotional warmth, community solidarity, spiritual faith, and the richness of lived experience over abstract principles."),
    ("Nordic European", "From a Nordic perspective valuing equality, democratic consensus, individual autonomy within a strong social safety net, pragmatism, and understated modesty."),
    ("South Asian dharmic", "From a South Asian perspective rooted in dharmic duty, cyclical time, karma, the joint family system, spiritual liberation, and the interdependence of all beings."),
]
