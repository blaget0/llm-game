from random import randrange
import json 


class SerializeableClass():
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def serialize(self):
        return json.dumps(
            self,
            default=lambda o: o.__dict__,
            sort_keys=True,
            indent=4)

    
class Player(SerializeableClass):
    def __init__(self, name, session_id, team, is_bot=0):
        self.name = name
        self.team = team 
        self.session_id = session_id
        self.is_bot = is_bot
        
    def make_turn(self, enemy_team, action, target=None):
        return (action, target)
    
    def delete_dead_units(self):
        for unit in self.team:
            if unit.is_dead():
                self.team.remove(unit)
    
    def get_team(self):
        return self.team  
    
    def __str__(self):
        return f"--------------\nPlayer:{self.name}\n\nTEAM:{self.team}\n----------------"

    def __repr__(self):
        return f'Игрок: {self.name}'
    

class Lobby(SerializeableClass):
    def __init__(self, *players, game_state=None, restore=False, serialized_data=None):
        if restore:
            self.players = []
            data = json.loads(serialized_data)
            for player in data['players']:
                print(player['team'])
                self.players.append(Player(name=player['name'], session_id=player['session_id'], 
                                           team=[Unit(**unit) for unit in player['team']], is_bot=player['is_bot']))

            self.game_state = GameState(restore=True, serialized_data=data['game_state'])
        else:    
            self.players = list(players)
            self.game_state = game_state

    
    
    def get_unit_by_name(self, name):
        units = []
        for player in self.players:
            units += player.team
        for unit in units:
            if unit.name == name:
                return unit
    
    def delete_dead_from_field(self):
        for player in self.players:
            player.delete_dead_units()
        
        return len(self.players) == 0



class Unit(SerializeableClass):
    def __init__(self, name, desc, hp, damages, id, image='images/DEFAULT.png', abilities=[], damage_multipliers = {}, damage_resistances = {}):
        self.name = name 
        self.desc = desc
        self.hp = hp 
        self.damages = damages
        self.abilities = abilities
        self.image = image
        self.id = id
        self.damage_multipliers = damage_multipliers
        self.damage_resistances = damage_resistances

    def deal_damage(self, other, input_damages):
        total = 0
        crit_chance = 0.15
        for damage_type, damage_multiplier_type, damage_resistance_type in list(zip(input_damages.keys(), self.damage_multipliers.keys(), other.damage_resistances.keys())):
            total += input_damages[damage_type] * self.damage_multipliers[damage_multiplier_type] * (1 - other.damage_resistances[damage_resistance_type])

        other.hp -= total * ( 1.5 if randrange(0, 1000)/1000 <= crit_chance else 1)
    
    
    def is_dead(self):
        return self.hp <= 0
        

    def __repr__(self):
        return self.name


class GameState(SerializeableClass):
    def __init__(self, *sessions, restore=False, serialized_data=None):
        if restore:
            self.sessions = serialized_data['sessions']
            self.current_turn = serialized_data['current_turn']
            self.selected_unit = serialized_data['selected_unit']
            self.turn_stage = serialized_data['turn_stage']
        else:
            self.sessions = sessions
            self.current_turn = randrange(0, 2)
            self.selected_unit = None
            self.turn_stage = 'SELECT-UNIT'

    def next_stage(self):
        turn_map = ['SELECT-UNIT', 'ACTION']
        self.turn_stage = turn_map[(turn_map.index(self.turn_stage) + 1) % len(turn_map)]
    

    def change_turn(self):
        self.current_turn  = (self.current_turn + 1) % 2

    def select_unit(self, unit: Unit):
        self.selected_unit = unit


class Field(SerializeableClass):
    def __init__(self):
        self.map = [[0,0,0],
                    [0,0,0]]
        



    