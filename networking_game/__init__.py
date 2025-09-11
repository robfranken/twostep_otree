from otree.api import *
import json
import random

doc = """
TwoStep networking game: players sequentially add/delete ties until n*rate steps.
"""

class Constants(BaseConstants):
    name_in_url = 'twostep'
    players_per_group = 5
    num_rounds = 1
    rate = 4  # steps per player
    density = 0.03  # network density
    # rewards
    p_out = -0.5
    p_recip = 3
    p_triad = 2

class Subsession(BaseSubsession):
    pass

class Group(BaseGroup):
    network_state = models.LongStringField(initial='')
    starting_network = models.LongStringField(initial='')
    whose_turn = models.IntegerField(initial=1)
    num_steps = models.IntegerField(initial=0)
    game_finished = models.BooleanField(default=False)

class Player(BasePlayer):
    points = models.IntegerField(initial=0)

# ExtraModel to store all ministeps in
class Action(ExtraModel):
    group = models.Link(Group)
    player = models.Link(Player)
    action_type = models.StringField(choices=['add', 'delete', 'pass'])
    target = models.IntegerField()
    step_number = models.IntegerField()

def creating_session(subsession: Subsession):
    for group in subsession.get_groups():
        n = len(group.get_players())
        num_possible_ties = n * (n - 1)
        num_ties_to_add = min(max(1, int(Constants.density * num_possible_ties)), num_possible_ties)
        possible_ties = [(i, j) for i in range(n) for j in range(n) if i != j]
        selected_ties = random.sample(possible_ties, num_ties_to_add)

        adj_matrix = [[0]*n for _ in range(n)]
        for i, j in selected_ties:
            adj_matrix[i][j] = 1

        group.network_state = json.dumps(adj_matrix)
        # save the starting network
        group.starting_network = group.network_state
        group.whose_turn = 1
        group.num_steps = 0

def calc_points_for_adj(adj_matrix):
    """Calculate points for all players given an adjacency matrix."""
    n = len(adj_matrix)
    points_list = []

    for i in range(n):
        out_pts = sum(adj_matrix[i]) * Constants.p_out
        recip_pts = sum(1 for j in range(n) if i != j and adj_matrix[i][j] == 1 and adj_matrix[j][i] == 1) * Constants.p_recip
        triad_pts = sum(
            Constants.p_triad
            for j in range(n)
            for k in range(n)
            if i != j and i != k and j != k and adj_matrix[i][j] and adj_matrix[j][k] and adj_matrix[k][i]
        )
        points_list.append({'out': out_pts, 'recip': recip_pts, 'triad': triad_pts, 'total': out_pts + recip_pts + triad_pts})
    return points_list

class Play(Page):
    live_method_timeout = 3600  # 1 hour timeout

    @staticmethod
    def js_vars(player: Player):
        return dict(my_index=player.id_in_group)

    @staticmethod
    def vars_for_template(player: Player):
        max_steps = Constants.rate + 2
        min_steps = max(1, Constants.rate - 2)
        return dict(Constants=Constants, index=player.id_in_group, max_steps=max_steps, min_steps=min_steps)

    @staticmethod
    def live_method(player: Player, data):
        group = player.group
        n = len(group.get_players())

        try:
            adj_matrix = json.loads(group.network_state)
        except Exception:
            adj_matrix = [[0] * n for _ in range(n)]

        action_taken = False
        whose_turn = group.whose_turn
        action_type = None
        target = None

        if not group.game_finished and group.whose_turn == player.id_in_group:
            if data.get('pass_turn'):
                action_taken = True
                action_type = 'pass'
            else:
                target = data.get('add_tie') or data.get('delete_tie')
                action_type = 'add' if 'add_tie' in data else 'delete'
                try:
                    target = int(target)
                except (TypeError, ValueError):
                    target = None

                if target and 1 <= target <= n and target != player.id_in_group:
                    target_idx = target - 1
                    if action_type == 'add' and adj_matrix[player.id_in_group - 1][target_idx] == 0:
                        adj_matrix[player.id_in_group - 1][target_idx] = 1
                        action_taken = True
                    elif action_type == 'delete' and adj_matrix[player.id_in_group - 1][target_idx] == 1:
                        adj_matrix[player.id_in_group - 1][target_idx] = 0
                        action_taken = True

            if action_taken:
                group.num_steps += 1
                group.network_state = json.dumps(adj_matrix)

                #update ExtraModel
                Action.create(
                    group=group,
                    player=player,
                    action_type=action_type,
                    target=target if target else None,
                    step_number=group.num_steps
                )
                #print(
                #    f"ExtraModel added: player={player.id_in_group}, action_type={action_type}, target={target}, step_number={group.num_steps}")

                if group.num_steps >= n * Constants.rate:
                    group.game_finished = True
                    whose_turn = 0
                else:
                    group.whose_turn = (group.whose_turn % n) + 1
                    whose_turn = group.whose_turn

        current_points = calc_points_for_adj(adj_matrix)

        broadcast = {
            'network_state': adj_matrix,
            'whose_turn': whose_turn,
            'num_steps': group.num_steps,
            'points_breakdown': current_points,
            'game_finished': group.game_finished,
        }

        return {0: broadcast}

def custom_export(players):
    # export our ExtraModel (containing chains of ministeps)
    yield ['session', 'participant', 'step_number', 'action', 'target']
    for player in players:
        participant = player.participant
        actions = Action.filter(player=player)
        for action in actions:
            yield [ player.session.code,
                    participant.code,
                    action.step_number,
                    action.action_type,
                    action.target
                    ]

page_sequence = [Play]
