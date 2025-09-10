from os import environ

SESSION_CONFIGS = [
    dict(
        name='networking_game',
        display_name='networking_game',
	    num_demo_participants=3,
        app_sequence=['networking_game'],
	    completionlink='https://app.prolific.com/submissions/complete?cc=C104VFED',
	    use_browser_bots=False
    ),
]

ROOMS = [
    dict(
        name='your_study',
        display_name='your_study',
        #participant_label_file='_rooms/your_study.txt',
        #use_secure_urls=True,
    ),
]


SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['consent', 'is_dropout', 'too_many_inactive_in_group']

#SESSION_FIELDS = ['current_network']
#PLAYER_FIELDS = ['current_network']
LANGUAGE_CODE = 'en'
REAL_WORLD_CURRENCY_CODE = 'EUR'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = 'secret'
