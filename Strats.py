import random
from collections import defaultdict
from Cards import *

# class Strategy:
#     def __init__(self):
#         self.buyable = All_Cards + [NoCard]
#         self.buy_counts = {}
#
#     def shuffle_buys(self):
#         shuffled_buys = list(self.buyable)
#         random.shuffle(shuffled_buys)
#         return shuffled_buys
#
#     def buy_accepted(self, card):
#         self.buy_counts[card] += 1


def cross(weights1, weights2):
    epsilon = random.random()
    new_weights = [w1 if random.random() < epsilon else w2 for w1, w2 in zip(weights1, weights2)]
    return new_weights


def mutate(weights, rate, rdm_strat):
    for i in range(len(weights)):
        if random.random() < rate:
            weights[i] = rdm_strat[i]


# slightly adjust weights towards other weights; on average this reduces extreme weights towards center
def perturb(weights, rate, rdm_strat):
    for i in range(len(weights)):
        weights[i] = weights[i] + rate * (rdm_strat[i] - weights[i])


def evolve(strats, frac=6):
    len_strat = len(strats)
    parents = strats[:len_strat // frac]
    for parent in parents:
        parent.vp = 0
    new_strats = list(parents)
    for parent in parents:
        w = list(parent.weights)
        rdm_strat = parent.__class__(w)
        perturb(w, 0.02, rdm_strat.weights)
        new_strats.append(parent.__class__(w))
    for parent in parents:
        w = list(parent.weights)
        rdm_strat = parent.__class__(w)
        mutate(w, 0.05, rdm_strat.weights)
        new_strats.append(parent.__class__(w))
    while len(new_strats) < len_strat:
        p1 = random.choice(parents)
        p2 = random.choice(parents)
        # assert p1.__class__ == p2.__class__
        w = cross(p1.weights, p2.weights)
        rdm_strat = p1.__class__(w)
        mutate(w, 0.05, rdm_strat.weights)
        new_strats.append(p1.__class__(w))
    return new_strats


def get_vp(strategy):
    return strategy.vp


class SimpleGA:
    def __init__(self):
        self.buyable = All_Cards + [NoCard]
        self.idx = {}
        for card in self.buyable:
            self.idx[card] = len(self.idx)
        # self.weights =[]
        # def get_weight(c):
        #     return self.weights[self.idx[c]]
        #
        # self.prio_buys = sorted(self.buyable, key=get_weight)
        self.vp = 0

        self.prio_buys = []
        self.prio_actions = [Lab, Village, Smithy]


class StaticGA(SimpleGA):
    def __init__(self, weights=None):
        super().__init__()
        if weights:
            self.weights = weights
        else:
            self.weights = []
            for _ in range(len(self.buyable)):
                self.weights.append(random.random())

        def get_weight(c):
            return self.weights[self.idx[c]]

        for turn in range(max_rounds):
            self.prio_buys.append(sorted(self.buyable, key=get_weight))


def linear_coef():
    return random.normalvariate(0, 0.05)


class LinearGA(SimpleGA):
    def __init__(self, weights=None):
        super().__init__()
        if weights:
            self.weights = weights
        else:
            self.weights = []
            for _ in range(2 * len(self.buyable)):
                self.weights.append(random.random())
                self.weights.append(linear_coef())

        def get_weight(c):
            return self.weights[self.idx[c]] + turn * self.weights[self.idx[c]+1]

        for turn in range(max_rounds):
            self.prio_buys.append(sorted(self.buyable, key=get_weight))


# s1 = LinearGA()
# s2 = LinearGA()
#
# print(s2.weights)
#
# ns = evolve([s1, s2], frac=2)
# print(ns[1].weights)


def current_state(player, turn):
    t = turn
    # vc = 0  # victory cards
    # ac = 0  # action cards
    # cc = 0  # coin cards excluding Copper
    # for card in player.deck:
    #     if card.vp > 0: vc += 1
    #     elif card.is_action: ac += 1
    #     elif card.coins > 1: cc += 1
    # for card in player.hand:
    #     if card.vp > 0: vc += 1
    #     elif card.is_action: ac += 1
    #     elif card.coins > 1: cc += 1
    # for card in player.discardP:
    #     if card.vp > 0: vc += 1
    #     elif card.is_action: ac += 1
    #     elif card.coins > 1: cc += 1
    return t  # , vc, ac, cc


class MCRL:  # Monte Carlo Reinforcement Learning
    def __init__(self, q=None, c=None):
        self.buyable = All_Cards + [NoCard]
        self.idx = {}
        for card in self.buyable:
            self.idx[card] = len(self.idx)

        self.q = defaultdict(lambda: [0.5] * len(self.buyable))
        if q: self.q.update(q)
        self.c = defaultdict(lambda: [0] * len(self.buyable))
        if c: self.c.update(c)

        self.sa_hist = []
        self.last_s = None

        self.prio_buys = []
        self.prio_actions = [Lab, Village, Smithy]
        self.buy_at_turn = {}
        for i in range(max_rounds):
            self.buy_at_turn[i] = [0] * len(self.buyable)

    def start_game(self):
        self.last_s = None
        self.sa_hist.clear()

    def buy_accepted(self, card):
        self.sa_hist.append((self.last_s, self.buyable.index(card)))

    def count_buys(self, card, turn):
        self.buy_at_turn[turn][self.buyable.index(card)] += 1

    def set_buy_prio(self, player, turn):
        self.last_s = current_state(player, turn)
        q_val = self.q[self.last_s]  # array with values for each card in buyable
        if 0.1 < random.random():
            keys = [(q, random.random()) for q in q_val]  # If q values are same, choose one randomly.
            # Important since we initialize new states with same q values
            self.prio_buys = [card for card, k in sorted(zip(self.buyable, keys), key=lambda x: x[1], reverse=True)]
        else:
            pb = list(self.buyable)
            random.shuffle(pb)
            self.prio_buys = pb

    def set_best_buy_prio(self, player, turn):
        self.last_s = current_state(player, turn)
        q_val = self.q[self.last_s]  # array with values for each card in buyable
        keys = [(q, random.random()) for q in q_val]  # If q values are same, choose one randomly.
        # Important since we initialize new states with same q values
        self.prio_buys = [card for card, k in sorted(zip(self.buyable, keys), key=lambda x: x[1], reverse=True)]

    def game_ended(self, reward):
        # if self.last_s is None:
        #     assert False, "Games shouldn't end with no moves taken"
        g = reward  # self.vp?
        rev_hist = self.sa_hist[::-1]
        for s, a in rev_hist:
            self.c[s][a] += 1
            self.q[s][a] += (1 / self.c[s][a])*(g - self.q[s][a])





# class MCRL:  # Monte Carlo Reinforcement Learning
#     def __init__(self, q={}, c={}):
#         self.buyable = All_Cards + [NoCard]
#         self.idx = {}
#         for card in self.buyable:
#             self.idx[card] = len(self.idx)
#
#         self.q = defaultdict(ConstArray(0.5, len(self.buyable)))  # tbc
#         self.q.update(q)
#         self.c = defaultdict(ConstArray(0, len(self.buyable)))
#         self.c.update(c)
#         self.sa_hist = []
#         self.last_s = None
#         self.learn = True
#
#         self.vp = 0
#         #
#         self.prio_buys = []
#         self.prio_actions = [Lab, Village, Smithy]
#         self.buy_at_turn = {}
#         for i in range(max_rounds):
#             self.buy_at_turn[i] = [0] * len(self.buyable)
#
#     def start_game(self):
#         self.last_s = None
#         # self.last_a = None
#         self.sa_hist.clear()
#
#     def buy_accepted(self, card, turn):
#         self.sa_hist.append((self.last_s, self.buyable.index(card)))
#         self.buy_at_turn[turn][self.buyable.index(card)] += 1
#
#     def set_buy_prio(self, player, turn):
#         self.last_s = current_state(player, turn)
#         q = self.q[self.last_s]  # array with values for each card in buyable
#         if random.random() < 0.9:
#             self.prio_buys = [c for c, k in sorted(zip(self.buyable, q), key=lambda x: x[1], reverse=True)]
#         else:
#             pb = list(self.buyable)
#             random.shuffle(pb)
#             self.prio_buys = pb
#
#     def game_ended(self, reward):
#         if not self.learn:
#             return
#         if self.last_s is None:
#             assert False, "Games shouldn't end with no moves taken"
#
#         g = reward  # self.vp?
#         rev_hist = self.sa_hist[::-1]
#         for s, a in rev_hist:
#             self.c[s][a] += 1
#             self.q[s][a] += (1 / self.c[s][a])*(g - self.q[s][a])

