import chromadb
from math import ceil
import numpy as np
import shutil


shutil.rmtree("database", ignore_errors=True)

spell_importance_lookup = ["very weak", "weak", "average", "strong", "very strong"]
damage_params = ['fire_damage', 'frost_damage', 'damage', 'poison_damage', 'shame_spell']
healing_params = ['heal', 'gold']


def aggregate_spells(metadatas, normed_distances, type):
    res = {}
    length = len(normed_distances)

    if type == 'heal':
        params = healing_params.copy()
    elif type == 'spell':
        params = damage_params.copy()

    for param in params:
        value = 0
        for i in range(length):
            value += normed_distances[i] * float(metadatas[i][param])

        res[param] = value
    return res


def get_spell(input_text, k_spells):
    chroma_client = chromadb.PersistentClient(path="database/")
    collection = chroma_client.get_collection("spells_collection")

    results = collection.query(
        query_texts=[input_text],
        n_results=k_spells
    )

    ids = results['ids'][0]
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = np.array(results['distances'][0])

    if len(distances) == 1:
        normed_importances = [1.]
    else:
        normed_importances = (np.exp(distances) / np.sum(np.exp(distances)))[::-1].copy()  # softmax

    resulting_damage = aggregate_spells(metadatas, normed_importances, 'spell')
    resulting_prompt = "A spell was cast on the target with the following characteristics or description of its parts: "

    for i in range(len(documents)):
        importance_idx = min(int(normed_importance / 0.2), 4) # немного изменена функция подсчета важности
        importance = spell_importance_lookup[importance_idx]
        resulting_prompt += f'\n\n Magnitude of the spell part - {importance}. The spell part itself: ' + documents[i]

    return resulting_prompt, resulting_damage


def get_healing_spell(input_text, k_spells):
    chroma_client = chromadb.PersistentClient(path="database/")
    collection = chroma_client.get_collection("healing_spells_collection")

    results = collection.query(
        query_texts=[input_text],
        n_results=k_spells
    )

    ids = results['ids'][0]
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = np.array(results['distances'][0])

    if len(distances) == 1:
        normed_importances = [1.]
    else:
        normed_importances = (np.exp(distances) / np.sum(np.exp(distances)))[::-1].copy()  # softmax

    resulting_heal = aggregate_spells(metadatas, normed_importances, 'heal')
    resulting_prompt = "A healing spell was cast on the target with the following characteristics or description of its parts: "

    for i in range(len(documents)):
        importance_idx = min(int(normed_importance / 0.2), 4) # немного изменена функция подсчета важности
        importance = spell_importance_lookup[importance_idx]
        resulting_prompt += f'\n\n Magnitude of the healing spell part - {importance}. The healing spell part itself: ' + \
                            documents[i]

    return resulting_prompt, resulting_heal



chroma_client = chromadb.PersistentClient(path="database/")
collection = chroma_client.get_or_create_collection(
    name="healing_spells_collection",
)

spell_collection = chroma_client.get_or_create_collection(
    name="spells_collection",
)


collection.add(
    documents=["The big healing spell heals alot and greatly raises the vitality and health of the recipient",
               "The small healing spell heals a little bit and raises the vitality and health of the recipient by a small amount"],
    metadatas=[{"name":"big_heal", "heal": "10", "gold": "9"}, {"name":"small_heal", "heal": "3", "gold": "4"}],
    ids=["id1", "id2"]
)

collection.add( # Среднее и Гигантское заклинание хила
    documents=["An average healing spell heals normally and normally increases the recipient's vitality and health",
               "The mega healing spell heals a lot and greatly increases the recipient's vitality and health"],
    metadatas=[{"name":"average_heal", "heal": "6", "gold": "6"}, {"name":"mega_heal", "heal": "20", "gold": "17"}],
    ids=["id3", "id4"]
)


spell_collection.add(
    documents=["The fire ball spell casts a circular ball of fire that explodes on contact",
               "The freezing rain spell casts a rain of ice that rains down and freezes anything beneath it"],
    metadatas=[{"name":"fireball", "fire_damage": "10", "frost_damage": "0", "gold": "10"}, {"name":"freezing_rain", "fire_damage": "0", "frost_damage": "10", "gold": "10"}],
    ids=["id1", "id2"]
)

spell_collection.add( # Витя и кислотный дождь
    documents=["The spell summons Vitya Shamonin, who destroys everything in his path",
               "The acid rain spell causes acid rain to fall and corrode everything underneath it"],
    metadatas=[{"name":"Vitya", "damage": "25", "gold": "30"}, {"name":"acid_rain", "poison_damage": "15", 'gold': '15'}],
    ids=["id3", "id4"]
)

spell_collection.add( # Кудж и трансформация в сосиску
    documents=["The spell summons Kudzh, who expels you from Mirea",
               "The spell briefly turns you into a sausage and you crawl right between the opponent's buttocks, causing him pain, but also giving him a little joy"],
    metadatas=[{"name":"Kudzh", "shame_spell": "20", "gold": "22"}, {"name":"sausage_transformation", "damage": "5", 'gold': '5'}],
    ids=["id5", "id6"]
)

spell_collection.add( # поцелуйчик и звонок Путину
    documents=["You kiss your opponent hard, and as a result of the kiss he becomes infected with gonorrhea",
               "You call Vladimir Vladimirovich Putin on the phone, your opponent has to leave Russia"],
    metadatas=[{"name":"kiss", "poison_damage": "8", "gold": "8"}, {"name":"Volodya", "damage": "50", 'gold': '70'}],
    ids=["id7", "id8"]
)

spell_collection.add( # Феечки Винкс и оживление Ленина
    documents=["You have summoned the Winx fairies, magic spells kill your opponent",
               "You have revived Lenin, the enemy is shaken, long live the new communist revolution"],
    metadatas=[{"name":"winx", "poison_damage": "20", "damage": "5", "frost_damage": "8", "gold": "40"}, {"name":"Lenin", "shame_spell": "20", 'gold': '23'}],
    ids=["id9", "id10"]
)

spell_collection.add( # Ежик и превращение в Китайца
    documents=["You threw a hedgehog at your opponent, now his whole face is covered in needles",
               "You turn your opponent into a Chinese and start talking about Taiwan"],
    metadatas=[{"name":"hedgehog", "damage": "5", "gold": "5"}, {"name":"chinese_spell", "shame_spell": "15", 'gold': '15'}],
    ids=["id11", "id12"]
)

# Лечение с элементами магии природы
collection.add(
    documents=[
        "Druid's Bloom causes flowers to sprout around the target, slowly healing wounds through natural magic",
        "Phoenix Tears instantly restore health but leave a burning sensation that slightly damages the caster"
    ],
    metadatas=[
        {"name":"druid_bloom", "heal": "8", "gold": "7"},
        {"name":"phoenix_tears", "heal": "15", "gold": "18"}
    ],
    ids=["id5", "id6"]
)

# Массовое лечение и щиты
collection.add(
    documents=[
        "Circle of Serenity creates a healing aura that affects all allies in range",
        "Crystal Barrier converts damage taken into health for a short duration"
    ],
    metadatas=[
        {"name":"serenity_circle", "heal": "5", "gold": "12"},
        {"name":"crystal_barrier", "heal": "12", "gold": "14"}
    ],
    ids=["id7", "id8"]
)

# Стихийная магия
spell_collection.add(
    documents=[
        "Thunderstorm Call summons lightning bolts that chain between wet targets",
        "Earthquake Fist shatters the ground, sending sharp rock fragments in all directions"
    ],
    metadatas=[
        {"name":"lightning_storm", "damage": "18", "gold": "25"},
        {"name":"earthquake_fist", "damage": "22", "gold": "28"}
    ],
    ids=["id13", "id14"]
)

# Манипуляция сознанием
spell_collection.add(
    documents=[
        "Brainwave Overload forces target to relive their most cringe memories repeatedly",
        "Mime Prison traps enemy in an invisible box they can't escape for 10 seconds"
    ],
    metadatas=[
        {"name":"cringe_overload", "shame_spell": "25", "gold": "20"},
        {"name":"mime_prison", "damage": "8", "gold": "12"}
    ],
    ids=["id15", "id16"]
)

# Нестандартные атаки
spell_collection.add(
    documents=[
        "Tax Audit summons IRS agents who distract enemy with financial paperwork",
        "Uno Reverse Card reflects last received damage back to the attacker"
    ],
    metadatas=[
        {"name":"irs_audit", "shame_spell": "15", "gold": "18"},
        {"name":"uno_reverse", "damage": "30", "gold": "35"}
    ],
    ids=["id17", "id18"]
)

# Комбинированные элементы
spell_collection.add(
    documents=[
        "Meteor Shower rains burning space rocks infused with cosmic radiation",
        "Quantum Entanglement links two enemies, making them share damage"
    ],
    metadatas=[
        {"name":"cosmic_meteor", "fire_damage": "18", "poison_damage": "7", "gold": "32"},
        {"name":"quantum_link", "damage": "25", "shame_spell": "10", "gold": "27"}
    ],
    ids=["id19", "id20"]
)

collection.add(
    documents=[
        "Pho Ga Blessing - healing broth with vietnamese herbs restores health gradually",
        "Gym Rat's Protein Shake - muscle-building mix temporarily increases max HP"
    ],
    metadatas=[
        {"name":"viet_pho_heal", "heal": "12", "gold": "15"},
        {"name":"protein_shake", "heal": "8", "gold": "12"}
    ],
    ids=["id9", "id10"]
)

collection.add(
    documents=[
        "Vietnamese Coffee Rush - triple caffeine dose grants healing through hyper-activity",
        "Sauna Session - extreme sweating detoxifies and regenerates cells"
    ],
    metadatas=[
        {"name":"coffee_rush", "heal": "18", "gold": "22"},
        {"name":"sauna_heal", "heal": "6", "gold": "9"}
    ],
    ids=["id11", "id12"]
)

spell_collection.add(
    documents=[
        "Gargamel's Revenge - summons evil cat Azrael who claws enemies randomly",
        "Spider-Sense Overload - makes target paranoid about danger from all directions"
    ],
    metadatas=[
        {"name":"azrael_claw", "damage": "15", "shame_spell": "5", "gold": "20"},
        {"name":"spider_paranoia", "shame_spell": "25", "gold": "28"}
    ],
    ids=["id21", "id22"]
)


spell_collection.add(
    documents=[
        "Gym Bro Roar - sonic attack using amplified pre-workout aggression",
        "Dumbbell Avalanche - drops 100kg worth of plates on target"
    ],
    metadatas=[
        {"name":"gym_roar", "damage": "20", "shame_spell": "10", "gold": "24"},
        {"name":"dumbbell_crash", "damage": "35", "gold": "40"}
    ],
    ids=["id23", "id24"]
)

spell_collection.add(
    documents=[
        "Vietnamese Traffic Spell - summons chaotic motorbike swarm",
        "Rice Paddy Trap - creates sticky mud field slowing movement"
    ],
    metadatas=[
        {"name":"moto_swarm", "damage": "8", "poison_damage": "7", "gold": "19"},
        {"name":"paddy_trap", "shame_spell": "15", "gold": "16"}
    ],
    ids=["id25", "id26"]
)


spell_collection.add(
    documents=[
        "Smurfberry Storm - poisonous blue berries rain down causing confusion",
        "Web Swing Fail - sticks enemy to accidentally created concrete wall"
    ],
    metadatas=[
        {"name":"toxic_berries", "poison_damage": "18", "gold": "25"},
        {"name":"concrete_web", "damage": "12", "gold": "18"}
    ],
    ids=["id27", "id28"]
)

collection.add(
    documents=[
        "Academic Mirage - temporarily restores motivation but causes burnout when effect expires",
        "Dean's Golden Handshake - instantly reinstates student status at enormous gold cost"
    ],
    metadatas=[
        {"name":"academic_mirage", "heal": "15", "gold": "10"},
        {"name":"deans_bribe", "heal": "30", "gold": "50"}
    ],
    ids=["id13", "id14"]
)

collection.add(
    documents=[
        "Library All-Nighter - heals through caffeine overdose but reduces subsequent spell effectiveness",
        "Diploma Shield - creates protective barrier using official graduation documents"
    ],
    metadatas=[
        {"name":"caffeine_overdose", "heal": "12", "gold": "14"},
        {"name":"diploma_shield", "heal": "20", "gold": "25"}
    ],
    ids=["id15", "id16"]
)

spell_collection.add(
    documents=[
        "Expulsion Notice - official parchment dealing psychological damage and lowering INT stats",
        "Student Debt Swarm - endless payment demands circling target like angry bees"
    ],
    metadatas=[
        {"name":"expulsion_notice", "shame_spell": "28", "damage": "12", "gold": "32"},
        {"name":"debt_swarm", "poison_damage": "6", "gold": "20"}
    ],
    ids=["id29", "id30"]
)

spell_collection.add(
    documents=[
        "Conscription Summon - materializes military draft papers with 99% evasion resistance",
        "Plagiarism Tornado - whirlwind of mismatched citations and broken bibliography"
    ],
    metadatas=[
        {"name":"draft_papers", "damage": "42", "gold": "48"},
        {"name":"citation_storm", "shame_spell": "38", "gold": "30"}
    ],
    ids=["id31", "id32"]
)

spell_collection.add(
    documents=[
        "Lecture Hypnosis - forces target to watch 10hrs of monotone PowerPoint presentations",
        "Gas Mask Drill - military-style PT session in toxic environment"
    ],
    metadatas=[
        {"name":"ppt_marathon", "poison_damage": "4", "shame_spell": "12", "gold": "17"},
        {"name":"gas_mask_pt", "damage": "20", "gold": "24"}
    ],
    ids=["id33", "id34"]
)

spell_collection.add(
    documents=[
        "Student Loan Curse - steals 1 gold per second while active",
        "Peer Review Paradox - trap that infinitely generates 'revise and resubmit' requests"
    ],
    metadatas=[
        {"name":"loan_curse", "gold_drain": "1", "damage": "8", "gold_cost": "12"},
        {"name":"peer_review", "shame_spell": "45", "gold": "38"}
    ],
    ids=["id35", "id36"]
)

spell_collection.add(
    documents=[
        "Barracks Hazing Ritual - summons spectral drill sergeant for psychological warfare",
        "Tuition Fee Meteor - colossal golden coin crushing enemies under educational debt"
    ],
    metadatas=[
        {"name":"drill_ghost", "shame_spell": "30", "damage": "15", "gold": "35"},
        {"name":"tuition_meteor", "damage": "55", "gold": "60"}
    ],
    ids=["id37", "id38"]
)

results = spell_collection.query(
    query_texts=["Show Powerpoint"],
    n_results=12
)

print(results)

