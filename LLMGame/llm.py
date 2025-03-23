from openai import OpenAI
import chromadb
from chroma import get_spell, get_healing_spell
import re
import os
from math import ceil
import numpy as np
from pydantic import BaseModel, Field
import json


#будет обновляться во время игры
# target_context = {"possible_targets":[]}


class Target(BaseModel):
    name: str = Field(description="The name of the target of the users action based on the users description of the target")


def get_target(user_prompt, target_context):
    system_prompt = "Extract the name of the target of the action based on the users description of the target. If there is no perfect match, pick the most similar target from the possible targets."
    possible_targets = json.dumps(target_context)
    completion = client.beta.chat.completions.parse(
    model=model_type,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "system", "content": possible_targets},
        {
            "role": "user",
            "content": user_prompt,
        },
    ],
    response_format=Target,
    temperature=temperature
    )

    target = completion.choices[0].message.parsed.name

    return target


def search_spellbook(input_text, target_context):
    #todo: извлечь количество заклинаний из запроса
    k_spells = 1
    possible_targets = target_context.copy()
    target = get_target(input_text, possible_targets)
    prompt, damage = get_spell(input_text, k_spells)
    prompt = f"The target of the spell is {target}" + prompt
    return prompt, damage, target

def search_healbook(input_text, target_context):
    #todo: извлечь количество заклинаний из запроса
    k_spells = 1
    possible_targets = target_context.copy()
    target = get_target(input_text, possible_targets)
    prompt, heal = get_healing_spell(input_text, k_spells)
    prompt = f"The target of the healing spell is {target}" + prompt
    return prompt, heal, target


def call_function(name, args):
    if name == "search_spellbook":
        return search_spellbook(**args)
    if name == "search_healbook":
        return search_healbook(**args)


def cast_spell(user_prompt):
    system_prompt = "You are powerful wizard, who obeys the user and casts spells based on what the user tells you."
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    ]

    completion = client.chat.completions.create(
    model=model_type,
    messages=messages,
    tools=wizard_tools,
    temperature=temperature,
    )

    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)

        result_prompt, misc_info, target = call_function(name, args)

        if name == 'search_spellbook':
            damage = misc_info.copy()

    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result_prompt)}
    )

    completion_2 = client.chat.completions.create(
    model=model_type,
    messages=messages,
    tools=wizard_tools,
    temperature=temperature,
    )

    final_response = completion_2.choices[0].message

    return final_response.content, damage, target


def cast_heal(user_prompt):
    system_prompt = "You are a great healer, who obeys the user and casts healing spells based on what the user tells you."
    messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_prompt},
    ]

    completion = client.chat.completions.create(
    model=model_type,
    messages=messages,
    tools=healer_tools,
    temperature=temperature,
    )

    for tool_call in completion.choices[0].message.tool_calls:
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)
        messages.append(completion.choices[0].message)

        result_prompt, misc_info, target = call_function(name, args)

        if name == 'search_healbook':
            heal = misc_info.copy()

    messages.append(
        {"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result_prompt)}
    )

    completion_2 = client.chat.completions.create(
    model=model_type,
    messages=messages,
    tools=healer_tools,
    temperature=temperature,
    )

    final_response = completion_2.choices[0].message

    return final_response.content, heal, target

model_type = "qwen2.5-7b-instruct-1m"
temperature = 0.7
client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

wizard_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_spellbook",
            "description": "Search the spellbook for the spell type and damage from the user's description of the spell they want to cast",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {"type": "string"},
                },
                "required": ["input_text"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]

healer_tools = [
    {
        "type": "function",
        "function": {
            "name": "search_healbook",
            "description": "Search the book of healing spells for the spell type and healing amount from the user's description of the healing spell they want to cast",
            "parameters": {
                "type": "object",
                "properties": {
                    "input_text": {"type": "string"},
                },
                "required": ["input_text"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    }
]




if  __name__ == '__main__':
    target_context = {"possible_targets":[]}
    target_context['possible_targets'].append({'id':1, 'name':'Glorb', 'description':'Glorb is a small, green, dirty goblin, who is holding a stick, wearing scraps of clothing and a blue hat.'})

    target_context['possible_targets'].append({'id':2, 'name':'Apolonius', 'description':'Apolonius is a big knight in plate armor, who is holding a big sword and a shield with a cross on it'})

    target_context['possible_targets'].append({'id':3, 'name':'Albert', 'description':'Albert is a purple slime who is part of the users team'})

    print(cast_heal("Heal my slime a lot!"))








