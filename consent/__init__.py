import datetime

from otree.api import *


doc = """
Constent form
"""

class Constants(BaseConstants):
    name_in_url = 'consent'
    players_per_group = None
    num_rounds = 1

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    pass

class Player(BasePlayer):
    consent = models.BooleanField(
        label="",
        choices=[[True, 'I consent']],
        blank=True
    )
    consent_timestamp = models.StringField(blank=True)

class ConsentPage(Page):
    form_model = 'player'
    form_fields = ['consent']

    def error_message(player, values):
        if not values.get('consent'):
            return "You must check the box to give your consent in order to participate in this study."

    def before_next_page(player: Player, timeout_happened):
        if player.consent:
            #timestamp as a string
            player.consent_timestamp = datetime.datetime.now().isoformat()
        else:
            player.participant.is_dropout = True
        player.participant.consent = player.consent

#def app_after_this_page(player, upcoming_apps):
#        if not player.consent:
#            # skip to the last app if participant did not consent
#            return upcoming_apps[-1]

page_sequence = [ConsentPage]