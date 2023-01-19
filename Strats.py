import random
import numpy as np
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
    eps = random.random()
    new_weights = [w1 if random.random() < eps else w2 for w1, w2 in zip(weights1, weights2)]
    return new_weights


def mutate(weights, prob, rdm_strat):
    for i in range(len(weights)):
        if random.random() < prob:
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
        rdm_strat = parent.__class__()
        perturb(w, 0.05, rdm_strat.weights)
        new_strats.append(parent.__class__(w))
    for parent in parents:
        w = list(parent.weights)
        rdm_strat = parent.__class__()
        mutate(w, 0.075, rdm_strat.weights)
        new_strats.append(parent.__class__(w))
    while len(new_strats) < len_strat:
        p1 = random.choice(parents)
        p2 = random.choice(parents)
        w = cross(p1.weights, p2.weights)
        rdm_strat = p1.__class__()
        mutate(w, 0.1, rdm_strat.weights)
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

def current_state_turn(player, turn):
    return turn


def current_state_vac(player, turn):
    vc = 0  # victory cards
    ac = 0  # action cards
    cc = 0  # coin cards excluding Copper
    for card in player.deck:
        if card.vp > 0: vc += 1
        elif card.is_action: ac += 1
        elif card.coins > 1: cc += 1
    for card in player.hand:
        if card.vp > 0: vc += 1
        elif card.is_action: ac += 1
        elif card.coins > 1: cc += 1
    for card in player.discardP:
        if card.vp > 0: vc += 1
        elif card.is_action: ac += 1
        elif card.coins > 1: cc += 1
    return turn, vc, ac, cc


def current_state_avg_val(player, turn):
    val = 0
    all_cards = len(player.deck) + len(player.hand) + len(player.discardP)
    for card in player.deck:
        val += card.coins
    for card in player.hand:
        val += card.coins
    for card in player.discardP:
        val += card.coins
    avg_val = round(10 * (val / all_cards)) / 10
    return turn, avg_val


def current_state_rem_draws(player, turn):
    val = 0
    smithies = 0
    all_cards = len(player.deck) + len(player.hand) + len(player.discardP)
    for card in player.deck:
        val += card.coins
        if card == Smithy:
            smithies += 1
    for card in player.hand:
        val += card.coins
        if card == Smithy:
            smithies +=1
    for card in player.discardP:
        val += card.coins
        if card == Smithy:
            smithies +=1
    avg_val = round(10 * (val / all_cards)) / 10

    len_deck = len(player.deck)
    drawable_cards_after_next_shuffle = (6 * (19 - turn) - len_deck)  # on average draw around 6 cards per turn
    deck_after_next_shuffle = (len_deck * 7 / 6 + len(player.hand) + len(player.discardP))  # on avg. buy 1 card per turn
    if drawable_cards_after_next_shuffle <= 0:
        return 0, avg_val, smithies
    elif drawable_cards_after_next_shuffle / deck_after_next_shuffle >= 3.25:
        return round(drawable_cards_after_next_shuffle / deck_after_next_shuffle), avg_val, smithies
    else:
        return round(2 * drawable_cards_after_next_shuffle / deck_after_next_shuffle) / 2, avg_val, smithies


class MCRL:  # Monte Carlo Reinforcement Learning
    def __init__(self, q=None, c=None):
        self.buyable = All_Cards + [NoCard]
        self.vp = 0

        self.q = defaultdict(lambda: [0] * len(self.buyable))
        if q: self.q.update(q)
        self.c = defaultdict(lambda: [0] * len(self.buyable))
        if c: self.c.update(c)

        self.sa_hist = []
        self.last_s = None

        self.prio_buys = []
        self.prio_actions = [Lab, Village, Smithy]

        self.buy_at_turn = np.zeros((max_rounds, len(self.buyable)), dtype=int)

    def start_game(self):
        self.last_s = None
        self.sa_hist.clear()

    def buy_accepted(self, card):
        self.sa_hist.append((self.last_s, self.buyable.index(card)))

    def count_buys(self, card, turn):
        self.buy_at_turn[turn, self.buyable.index(card)] += 1
        # print('!', end='')

    def set_buy_prio(self, player, turn):
        self.last_s = current_state_turn(player, turn)
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
        self.last_s = current_state_turn(player, turn)
        q_val = self.q[self.last_s]  # array with values for each card in buyable
        keys = [(q, random.random()) for q in q_val]  # If q values are same, choose one randomly.
        # Important since we initialize new states with same q values
        self.prio_buys = [card for card, k in sorted(zip(self.buyable, keys), key=lambda x: x[1], reverse=True)]

    def learn(self, g):
        rev_hist = self.sa_hist[::-1]
        for s, a in rev_hist:
            self.c[s][a] += 1
            self.q[s][a] += (1 / self.c[s][a])*(g - self.q[s][a])
