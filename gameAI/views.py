from django.http import JsonResponse
from django.shortcuts import render, redirect
from .game_models import GameState, Player, Lobby, Unit
from .bots import SimpleBot
from random import randrange
from llm_code import llm

default_damages = {"fire_damage": 1, "frost_damage": 1}
default_damage_resistances = {"fire_damage": 0, "frost_damage": 0}
default_damage_multipliers = {"fire_damage": 1, "frost_damage": 1}

def index(request):
    
    if request.method == 'POST':

        print('****************POST_INFO*********\n',request.POST)

        bot_message = 'none'
        player_message = 'none'
        damage_info = 'none'
        heal_info = 'none'
        target = 'none'
        promt = None 
        cur_lobby = request.session['CUR_LOBBY']
        cur_lobby = Lobby(restore=True, serialized_data=cur_lobby)
        if 'promt' in request.POST:

            promt = request.POST.get('promt')
            print('PROMT:', promt)
            target_context = {'possible_targets': []}
            # можно случайно ударить юнита своей команды
            for i, unit in enumerate(cur_lobby.players[1].team + cur_lobby.players[0].team):
                target_context['possible_targets'].append({
                                                         'id': i,
                                                         'name': unit.name,
                                                         'description': unit.desc
                                                        })
            selected_unit = cur_lobby.get_unit_by_name(cur_lobby.game_state.selected_unit)

            if selected_unit.name == 'wizard':
                response_text, damage_info, target = llm.cast_spell(promt, target_context)
                if damage_info != 'none' and target != 'none':
                    target_unit = cur_lobby.get_unit_by_name(target)

                    player_damage_dealt = selected_unit.deal_damage(target_unit, damage_info)
                    player_message = f'Wizard says: {response_text}. The spell did {player_damage_dealt} damage to {target}'
                else: 
                    player_message = f'Wizard says: {response_text}.'

            elif selected_unit.name == 'healer':
                response_text, heal_info, target = llm.cast_heal(promt, target_context)
                if heal_info != 'none' and target != 'none':
                    target_unit = cur_lobby.get_unit_by_name(target)

                    heal = heal_info['heal']
                    target_unit.hp += heal
                    player_message = f'Healer says: {response_text}. The spell healed {heal} hp of {target}'
                else:
                    player_message = f'Healer says: {response_text}.'
            else:
                response_text, target = llm.basic_attack(selected_unit.desc, promt, target_context)
                target_unit = cur_lobby.get_unit_by_name(target)

                player_damage_dealt = selected_unit.deal_damage(target_unit, selected_unit.damages)
                player_message = f'{response_text} {selected_unit.name} did {player_damage_dealt} damage to {target}'

  
            if cur_lobby.players[1].is_bot:
                # This bot attacks random units
                attacked = cur_lobby.players[0].team[randrange(0, 3)]
                attacker_index = randrange(0, 3)

                bot_damage_dealt = cur_lobby.players[1].team[attacker_index].deal_damage(attacked, cur_lobby.players[1].team[attacker_index].damages)
                bot_message = f"Bot attacked {attacked.name} with {cur_lobby.players[1].team[attacker_index].name} and dealt {bot_damage_dealt} damage."

            game_is_end = cur_lobby.delete_dead_from_field()
            
            cur_lobby.game_state.next_stage()


            lobby_data = cur_lobby.serialize()
            request.session['CUR_LOBBY'] = lobby_data
            return JsonResponse({
                'status': 'success',
                'message': player_message,
                'bot_message': bot_message,
                'lobby': lobby_data,  # Передаем как объект, а не как строку
                'game_is_end': game_is_end

            })


        
        elif 'unit_name' in request.POST:
        
            unit_name = request.POST.get('unit_name')
            cur_lobby = request.session['CUR_LOBBY']

            cur_lobby = Lobby(restore=True, serialized_data=cur_lobby)
            cur_lobby.game_state.next_stage()
            cur_lobby.game_state.selected_unit = unit_name

            # Сериализуем lobby в словарь, а не в строку
            
            lobby_data = cur_lobby.serialize()
            request.session['CUR_LOBBY'] = lobby_data
            game_is_end = cur_lobby.delete_dead_from_field()
            
            return JsonResponse({
                'status': 'success',
                'message': f'Selected unit: {unit_name}.',
                'lobby': lobby_data,  # Передаем как объект, а не как строку
                'game_is_end': game_is_end,
                'promt': promt

            })

    if 'CUR_LOBBY' in request.session:
        del request.session['CUR_LOBBY']
    if 'CUR_LOBBY' not in request.session or 'restart' in request.POST:
        player1 = Player('Player', request.session.session_key, 
                         [
                             Unit(name='wizard',desc='A powerful wizard, who can cast spells with magic', hp=5, damages=default_damages, id=1, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                             Unit(name='healer',desc='A healer, who can heal team members and restore their health', hp=5, damages=default_damages, id=2, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                             Unit(name='knight',desc='A really strong knight without armor but with big sword', hp=5, damages=default_damages, id=3, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances)  
                         ])
        
        bot = SimpleBot([Unit(name='goblin1',desc='Small goblin with a pighead on his head', hp=5, damages=default_damages, id=4, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                         Unit(name='goblin2',desc='A goblin with an old knife. He lost his eye a long time ago', hp=5, damages=default_damages, id=5, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                         Unit(name='goblin3',desc='A goblin warrior. He is a way bigger than the usual goblin', hp=5, damages=default_damages, id=6, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances)])
        
        state = GameState(player1.session_id, bot.session_id)
        state.turn_stage = 'SELECT-UNIT'
        cur_lobby = Lobby(player1, bot, game_state=state)
        request.session['CUR_LOBBY'] = cur_lobby.serialize()

    # Для GET-запросов возвращаем HTML-страницу
    
    cur_lobby = Lobby(restore=True, serialized_data=request.session['CUR_LOBBY'])
    return render(request, "index.html", {'lobby': cur_lobby})


