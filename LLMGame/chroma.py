import chromadb
from math import ceil
import numpy as np


spell_importance_lookup = ["very weak", "weak", "average", "strong", "very strong"]
damage_params = ['fire_damage', 'frost_damage']
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
        normed_importances = (np.exp(distances)/np.sum(np.exp(distances)))[::-1].copy() # softmax

    resulting_damage = aggregate_spells(metadatas, normed_importances, 'spell')
    resulting_prompt = "A spell was cast on the target with the following characteristics or description of its parts: "

    for i in range(len(documents)):
        importance = spell_importance_lookup[ceil((normed_importances[i] / 0.2) - 1.01)]
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
        normed_importances = (np.exp(distances)/np.sum(np.exp(distances)))[::-1].copy() # softmax

    resulting_heal = aggregate_spells(metadatas, normed_importances, 'heal')
    resulting_prompt = "A healing spell was cast on the target with the following characteristics or description of its parts: "

    for i in range(len(documents)):
        importance = spell_importance_lookup[ceil((normed_importances[i] / 0.2) - 1.01)]
        resulting_prompt += f'\n\n Magnitude of the healing spell part - {importance}. The healing spell part itself: ' + documents[i]

    return resulting_prompt, resulting_heal


chroma_client = chromadb.PersistentClient(path="database/")

'''
collection = chroma_client.get_or_create_collection("healing_spells_collection")

collection.add(
    documents=["The big healing spell heals alot and greatly raises the vitality and health of the recipient", 
               "The small healing spell heals a little bit and raises the vitality and health of the recipient by a small amount"],
    metadatas=[{"name":"big_heal", "heal": "10", "gold": "10"}, {"name":"small_heal", "heal": "3", "gold": "3"}],
    ids=["id1", "id2"]
)

battle_collection = chroma_client.get_or_create_collection("spells_collection")

battle_collection.add(
    documents=["The fire ball spell casts a circular ball of fire that explodes on contact", 
               "The freezing rain spell casts a rain of ice that rains down and freezes anything beneath it"],
    metadatas=[{"name":"fireball", "fire_damage": "10", "frost_damage": "0"}, {"name":"freezing_rain", "fire_damage": "0", "frost_damage": "10"}],
    ids=["id1", "id2"]
)

results = battle_collection.query(
    query_texts=["Rain ice on the enemies!"],
    n_results=2
)

print(results)'''
