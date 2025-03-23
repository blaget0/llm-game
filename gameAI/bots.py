from .game_models import Player


class SimpleBot(Player):
    def __init__(self, team):
        super().__init__('SIMPLE_BOT', 'BOT',team, 1)

    def make_turn(self, enemy_team):
        for i in enemy_team:
            if not isinstance(i, int):
                break
        
        action = 'attack'
        target = enemy_team[i]

        return super().make_turn(enemy_team, action, target)

     