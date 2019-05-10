import math
import random

from dlgo import agent
from dlgo.types import Player
from dlgo.utils import coords_from_point


__all__ = [
    'MCTSAgent',
]


def fmt(x):
    if x is Player.black:
        return 'B'
    elif x is Player.white:
        return 'W'
    elif x.is_pass:
        return 'pass'
    elif x.is_resign:
        return 'resign'
    else:
        return coords_from_point(x.oint)


def show_tree(node, indent='', max_depth=3):
    if max_depth < 0:
        return
    elif node is None:
        return
    elif node.parent is None:
        print('%sroot' % indent)
    else:
        player = node.parent.game_state.next_player
        move = node.move
        print('%s%s %s %d %.3f' % (
            indent, fmt(player), fmt(move),
            node.num_rollouts,
            node.winning_frac(player),
        ))


class MCTSNode(object):
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            Player.black: 0,
            Player.white: 0
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.legal_moves()

    def get_random_children(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        new_game_state = self.game_state.apply_move(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.is_over()

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)


class MCTSAgent(agent.Agent):
    def __init__(self, num_rounds,  temperature):
        agent.Agent.__init__(self)
        self.num_rounds = num_rounds
        self.temperature = temperature

    def select_move(self, game_state):
        root_node = MCTSNode(game_state)
        root_node = self._create_markov_tree(root_node, self.num_rounds)

        scored_moves = [
            (child.winning_frac(game_state.next_player), child.move, child.num_rollouts)
            for child in root_node.children
        ]
        scored_moves.sort(key=lambda x: x[0], reverse=True)
        for s, m, n in scored_moves[:10]:
            print('%s - %.3f (%d)' % (m, s, n))

        best_move = self._get_best_move(game_state, root_node)
        return best_move

    def _get_best_move(self, game_state, root_node):
        best_move = None
        best_winning_percentage = -1.0
        for child in root_node.children:
            child_winning_percentage = child.winning_frac(game_state.next_player)
            if child_winning_percentage > best_winning_percentage:
                best_winning_percentage = child_winning_percentage
                best_move = child.move
        return best_move

    def _create_markov_tree(self, root_node, num_rounds):
        for i in range(num_rounds):
            node = root_node
            while (not node.can_add_child()) and (not node.is_terminal()):
                node = self.select_child(node)

            if node.can_add_child():
                node = node.get_random_children()

            winner = self.simulate_random_game(node.game_state)

            while node is not None:
                node.record_win(winner)
                node = node.parent
        return root_node

    def select_child(self, node):
        """
        select a child according to the Upper Confidence bound for trees metric (UCT)
        :param node:
        :return:
        """
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None

        for child in node.children:
            win_percentage = child.winning_frac(node.game_state.next_player)
            uct_score = get_uct_score(log_rollouts, child.num_rollouts, win_percentage, self.temperature)

            if uct_score > best_score:
                best_score = uct_score
                best_child = child
        return best_child

    @staticmethod
    def simulate_random_game(game):
        bots = {
            Player.black: agent.RandomBot(),
            Player.white: agent.RandomBot(),
        }
        while not game.is_over():
            bot_move = bots[game.next_player].select_move(game)
            game = game.apppy_move(bot_move)
        return game.winner()


def get_uct_score(parent_rollouts, child_rollouts, win_percentage, temperature):
    exploration = math.sqrt(math.log(parent_rollouts) / child_rollouts)
    return win_percentage + temperature * exploration



