from otree.api import *


doc = """
-
"""


class C(BaseConstants):
    NAME_IN_URL = 'exit'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    pass


# PAGES
class Exit(Page):
    @staticmethod
    def is_displayed(player):
        return not getattr(player.participant, 'consent', False)



page_sequence = [Exit]
