from django.http import JsonResponse
from django.shortcuts import render, redirect
from .game_models import GameState, Player, Lobby, Unit
from .bots import SimpleBot
from random import randrange
from llm_code import llm


def index(request):
    
    if request.method == 'POST':

        print('****************POST_INFO*********\n',request.POST)

        promt = None 
        cur_lobby = request.session['CUR_LOBBY']
        cur_lobby = Lobby(restore=True, serialized_data=cur_lobby)
        if 'promt' in request.POST:

            promt = request.POST.get('promt')
            print('PROMT:', promt)
            target_context = {'possible_targets': []}
            for i, unit in enumerate(cur_lobby.players[1].team):
                target_context['possible_targets'].append({
                                                         'id': i,
                                                         'name': unit.name,
                                                         'description': unit.desc
                                                        })

            _, damage_info, target = llm.cast_spell(promt, target_context)
            target_unit = cur_lobby.get_unit_by_name(target)
            selected_unit = cur_lobby.get_unit_by_name(cur_lobby.game_state.selected_unit)

            print('LLM RESPONSE:', damage_info,type(damage_info))
            for dam in damage_info.values():
                target_unit.hp -= dam

            if cur_lobby.players[1].is_bot:
                # This bot attack random units
                attacked = cur_lobby.players[0].team[randrange(0, 3)]
                target_unit.deal_damage(attacked)

            game_is_end = cur_lobby.delete_dead_from_field()
            
            cur_lobby.game_state.next_stage()


            lobby_data = cur_lobby.serialize()
            request.session['CUR_LOBBY'] = lobby_data
            return JsonResponse({
                'status': 'success',
                'message': f'Атакован: {target}. Выберите цель.',
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
                'message': f'Выбран юнит: {unit_name}. Выберите цель.',
                'lobby': lobby_data,  # Передаем как объект, а не как строку
                'game_is_end': game_is_end,
                'promt': promt

            })


    del request.session['CUR_LOBBY']
    if 'CUR_LOBBY' not in request.session or 'restart' in request.POST:
        player1 = Player('Vitya', request.session.session_key, 
                         [
                             Unit('knight1','kinda weak knight with cool armor', 5, 1, id=1),
                             Unit('knight2', 'looks like a barbarian than knight',5, 1, id=2),
                             Unit('knight3','really strong knight without armor but with big sword' ,5, 1, id=3)  
                         ])
        
        bot = SimpleBot([Unit('goblin1','small goblin with pighead at his head', 5, 1, id=4),
                         Unit('goblin2','goblin with old knife. He loose his eye a long time ago' ,5, 1, id=5),
                         Unit('goblin3', 'It is goblin warrior. He is a way bigger than usual goblin' ,5, 1, id=6)])
        
        state = GameState(player1.session_id, bot.session_id)
        state.turn_stage = 'SELECT-UNIT'
        cur_lobby = Lobby(player1, bot, game_state=state)
        request.session['CUR_LOBBY'] = cur_lobby.serialize()

    # Для GET-запросов возвращаем HTML-страницу
    
    cur_lobby = Lobby(restore=True, serialized_data=request.session['CUR_LOBBY'])
    return render(request, "index.html", {'lobby': cur_lobby})


