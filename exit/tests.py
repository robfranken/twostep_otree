from . import *

class PlayerBot(Bot):
    def play_round(self):
        def play_round(self):
            player = self.player
            if not getattr(player.participant, 'consent', False):
                yield Exit

