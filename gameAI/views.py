from django.http import JsonResponse
from django.shortcuts import render, redirect
from .game_models import GameState, Player, Lobby, Unit
from .bots import SimpleBot
from random import randrange
from llm_code import llm
from django.shortcuts import render
from .models import Drawing
import base64
import os
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import uuid
import logging
from django.templatetags.static import static
from llm_code.image_ranking_initialize import find_unit_properties
from django.contrib.auth.decorators import login_required


logger = logging.getLogger(__name__)

from django.conf import settings


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect



from django.shortcuts import render
from .models import GameResult

@login_required
def game_history(request):
    results = GameResult.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'history.html', {'results': results})

@login_required
def leaderbord(request):
    results = GameResult.objects.order_by('wave')
    return render(request, 'leaderbord.html', {'results': results})


def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')




def check_media_folder_exists(folder_name):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'drawings')
    folder_path = os.path.join(folder_path, folder_name)
    print('MEDIA_ROOT MEDIA_ROOT MEDIA_ROOT MEDIA_ROOT:', settings.MEDIA_ROOT,)
    return os.path.exists(folder_path)

def get_images_path(folder_name):
    images = []
    folder_path = os.path.join(settings.MEDIA_ROOT, 'drawings', folder_name)
    
    if os.path.exists(folder_path):
        for image in os.listdir(folder_path):
            if image.lower().endswith(('.png', '.jpg', '.jpeg')):
                # Сохраняем только относительный путь от MEDIA_ROOT
                images.append(f'{folder_name}/{image}')
    else:
        # Используем static для дефолтных изображений
        default_image = static('images/DEFAULT.png')
        images = [default_image] * 3
    
    return images

        



default_damages = {"fire_damage": 1, "frost_damage": 1}
default_damage_resistances = {"fire_damage": 0, "frost_damage": 0}
default_damage_multipliers = {"fire_damage": 1, "frost_damage": 1}


def TEST_DRAW(request):
    drawing = Drawing.objects.all() 
    print('Объекты2: ', drawing)
    image_data = ''
    return render(request, 'TEST.html', {'image_data': image_data})

@login_required
def home_page(request):
    if request.method == 'POST':
        return redirect('/draw')
  
    return render(request, 'home.html')

@login_required
def index(request):
    print(request.session.session_key)
    
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
                    target_unit = cur_lobby.get_unit_by_name(target.lower())

                    player_damage_dealt = selected_unit.deal_damage(target_unit, damage_info)
                    player_message = f'Wizard says: {response_text}. The spell did {player_damage_dealt} damage to {target}'
                else: 
                    player_message = f'Wizard says: {response_text}.'

            elif selected_unit.name == 'healer':
                response_text, heal_info, target = llm.cast_heal(promt, target_context)
                if heal_info != 'none' and target != 'none':
                    target_unit = cur_lobby.get_unit_by_name(target)

                    heal = heal_info['heal']
                    if target_unit is not None:
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
                attacked = cur_lobby.players[0].team[randrange(0, len(cur_lobby.players[0].team))]
                attacker_index = randrange(0, len(cur_lobby.players[1].team))

                bot_damage_dealt = cur_lobby.players[1].team[attacker_index].deal_damage(attacked, cur_lobby.players[1].team[attacker_index].damages)
                bot_message = f"Bot attacked {attacked.name} with {cur_lobby.players[1].team[attacker_index].name} and dealt {bot_damage_dealt} damage."

            game_is_end = cur_lobby.delete_dead_from_field()
            if len(cur_lobby.players[1].team) == 0:
                cur_lobby.wave += 1
                new_damages = {"fire_damage": 1 + cur_lobby.wave, "frost_damage": 1 + cur_lobby.wave }
                new_damage_resistances = {"fire_damage": 0 + cur_lobby.wave/100, "frost_damage": 0 + cur_lobby.wave/100}
                new_damage_multipliers = {"fire_damage": 1 + cur_lobby.wave/10, "frost_damage": 1 + cur_lobby.wave/10}
                bot = SimpleBot([Unit(name='goblin1',desc='Goblin from darkness of dungeon', hp=5 +  cur_lobby.wave*2, damages=new_damages, id=4, damage_multipliers=new_damage_multipliers, damage_resistances=new_damage_resistances),
                         Unit(name='goblin2',desc='Goblin from darkness of dungeon', hp=5 + cur_lobby.wave*2, damages=new_damages, id=5, damage_multipliers=new_damage_multipliers, damage_resistances=new_damage_resistances),
                         Unit(name='goblin3',desc='Goblin from darkness of dungeon', hp=5 +  cur_lobby.wave*2, damages=new_damages, id=6, damage_multipliers=new_damage_multipliers, damage_resistances=new_damage_resistances)])

                cur_lobby.players[1] = bot
                

            if game_is_end:
                from .models import GameResult
                GameResult.objects.create(
                    user=request.user,
                    wave=cur_lobby.wave
                )

                return redirect('history')   
            
            cur_lobby.game_state.next_stage()
            


            lobby_data = cur_lobby.serialize()
            request.session['CUR_LOBBY'] = lobby_data
            print({'status': 'success',
                'message': player_message,
                'bot_message': bot_message,
                'lobby': lobby_data,  # Передаем как объект, а не как строку
                'game_is_end': game_is_end})
            
            return JsonResponse({
                'status': 'success',
                'message': player_message,
                'bot_message': bot_message,
                'lobby': lobby_data,  # Передаем как объект, а не как строку
                'game_is_end': game_is_end,
                'MEDIA_URL': settings.MEDIA_URL

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
                'promt': promt,
                'MEDIA_URL': settings.MEDIA_URL

            })

    if 'CUR_LOBBY' in request.session:
        del request.session['CUR_LOBBY']
    if 'CUR_LOBBY' not in request.session or 'restart' in request.POST:
        images = get_images_path('units'+str(request.session.session_key)+'units')
        print('IMAGES IMAGES IMAGES IMAGES:', images)
        prepared_imgs = ['media\\drawings\\'+ img.replace('/', '\\') for img in   images]
        props = find_unit_properties(prepared_imgs)
        print('PROPS PROPS PROPS',  props)
        player1 = Player('Player', request.session.session_key, 
                         [
                             Unit(image=images[0] ,
                                  name='wizard',desc='A powerful wizard, who can cast spells with magic', hp=max([round(props[0][1]*10) + randrange(0, 9) - 4, 1]), damages=default_damages, id=1, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                             Unit(image=images[1] ,
                                 name='healer',desc='A healer, who can heal team members and restore their health', hp=max([round(props[1][1]*10) + randrange(0, 9) - 4, 1]), damages=default_damages, id=2, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances),
                             Unit(image=images[2] ,
                                 name='knight',desc='A really strong knight without armor but with big sword', hp=max([round(props[2][1]*10) + randrange(0, 9) - 4, 1]), damages={"fire_damage": 5, "frost_damage": 5}, id=3, damage_multipliers=default_damage_multipliers, damage_resistances=default_damage_resistances)  
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


    print('MEDIA_ROOT MEDIA_ROOT MEDIA_ROOT MEDIA_ROOT:', settings.MEDIA_ROOT,)

    return render(request, "index.html", {'lobby': cur_lobby,
                                          'MEDIA_URL': settings.MEDIA_URL})




@login_required
def drawing_board(request):

    return render(request, 'drawer.html')


@login_required
@csrf_exempt
def save_drawing(request):
    if request.method == 'POST':
        try:
            
            save_dir = os.path.join(settings.MEDIA_ROOT, 'drawings', 'units' + str(request.session.session_key) + 'units')
            
            # Create directory if not exists
            os.makedirs(save_dir, exist_ok=True)
            
            # Save all three images
            from io import BytesIO
            from PIL import Image

            for i in range(1, 4):
                file_key = f'unit{i}'
                if file_key in request.FILES:
                    file = request.FILES[file_key]
                    file_path = os.path.join(save_dir, f'unit{i}.png')
                    
                    # Открываем изображение с помощью Pillow
                    img = Image.open(file)
                    
                    # Конвертируем в RGB, если это PNG с прозрачностью
                    if img.mode in ('RGBA', 'LA'):
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    
                    # Изменяем размер до 100x100 с антиалиасингом
                    img = img.resize((100, 100), Image.LANCZOS)
                    
                    # Сохраняем в формате PNG
                    output = BytesIO()
                    img.save(output, format='PNG', quality=95)
                    output.seek(0)
                    
                    # Записываем сжатое изображение в файл
                    with open(file_path, 'wb') as f:
                        f.write(output.getvalue())
            
            return JsonResponse({'url': '/game', 'MEDIA_URL': settings.MEDIA_URL})
        except Exception as e:
            logger.error(f"Error saving drawings: {str(e)}", exc_info=True)
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=500)
    
    return JsonResponse({'status': 'error'}, status=400)







