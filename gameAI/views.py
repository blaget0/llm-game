from django.http import JsonResponse
from django.shortcuts import render
from .game_models import GameState, Player, Lobby, Unit
from .bots import SimpleBot
from random import randrange
from ..LLMGame.llm import get_target


def index(request):
    
    if request.method == 'POST':
        print('!!!!', request.POST)


        if 'target' in request.POST:
            target = request.POST.get('target')
            cur_lobby = Lobby(restore=True, serialized_data=request.session['CUR_LOBBY'])

            print(cur_lobby.game_state.selected_unit, target, '!@@@!:\n', cur_lobby.players)
            cur_unit, target_unit = cur_lobby.get_unit_by_name(cur_lobby.game_state.selected_unit), cur_lobby.get_unit_by_name(target)
            cur_unit.deal_damage(target_unit)
            cur_lobby.game_state.next_stage()
            
            print(isinstance(cur_lobby.players[1], SimpleBot), cur_lobby.players[1])
            if cur_lobby.players[1].is_bot:
                # This bot attack random units
                attacked = cur_lobby.players[0].team[randrange(0, 3)]
                target_unit.deal_damage(attacked)
            game_is_end = cur_lobby.delete_dead_from_field()
                


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
                 'game_is_end': game_is_end

            })


    if 'CUR_LOBBY' not in request.session or 'restart' in request.POST:
        player1 = Player('Vitya', request.session.session_key, 
                         [
                             Unit('knight1', 5, 1, id=1),
                             Unit('knight2', 5, 1, id=2),
                             Unit('knight3', 5, 1, id=3)  
                         ])
        
        bot = SimpleBot([Unit('goblin1', 5, 1, id=4),
                         Unit('goblin2', 5, 1, id=5),
                         Unit('goblin3', 5, 1, id=6)])
        
        state = GameState(player1.session_id, bot.session_id)
        state.turn_stage = 'SELECT-UNIT'
        cur_lobby = Lobby(player1, bot, game_state=state)
        request.session['CUR_LOBBY'] = cur_lobby.serialize()

    # Для GET-запросов возвращаем HTML-страницу
    
    cur_lobby = Lobby(restore=True, serialized_data=request.session['CUR_LOBBY'])
    cur_lobby.game_state.turn_stage = 'SELECT-UNIT'
    return render(request, "index.html", {'lobby': cur_lobby})