import random
from Cards import *


class Strategy:
    def __init__(self):
        self.buyable = All_Cards + [NoCard]
        self.buy_counts = {}

    def shuffle_buys(self):
        shuffled_buys = list(self.buyable)
        random.shuffle(shuffled_buys)
        return shuffled_buys

    def buy_accepted(self, card):
        self.buy_counts[card] += 1


def cross(weights1, weights2):
    epsilon = random.random()
    new_weights = [w1 if random.random() < epsilon else w2 for w1, w2 in zip(weights1, weights2)]
    return new_weights


def mutate(weights, rate):
    for i in range(len(weights)):
        if random.random() < rate:
            weights[i] = random.random()


def perturb(weights, rate):
    for i in range(len(weights)):
        rand = random.random()
        w = weights[i] + rand
        if rand < rate and 0 <= w <= 1:
            weights[i] = w


def evolve(strats):
    len_strat = len(strats)
    parents = strats[:len_strat // 6]
    for parent in parents:
        parent.vp = 0
    new_strats = list(parents)
    for parent in parents:
        w = list(parent.weights)
        perturb(w, 0.02)
        new_strats.append(parent.__class__(w))
    for parent in parents:
        w = list(parent.weights)
        mutate(w, 0.05)
        new_strats.append(parent.__class__(w))
    while len(new_strats) < len_strat:
        p1 = random.choice(parents)
        p2 = random.choice(parents)
        # assert p1.__class__ == p2.__class__
        w = cross(p1.weights, p2.weights)
        mutate(w, 0.05)
        new_strats.append(p1.__class__(w))
    return new_strats


class SimpleGA(Strategy):
    def __init__(self, weights=None):
        super().__init__()
        self.idx = {}
        for card in self.buyable:
            self.idx[card] = len(self.idx)
        if weights:
            self.weights = weights
        else:
            self.weights = []
            for _ in range(len(self.buyable)):
                self.weights.append(random.random())

        def get_weight(c):
            return self.weights[self.idx[c]]

        self.prio_buys = sorted(self.buyable, key=get_weight)
        self.vp = 0

        self.prio_actions = [Lab, Village, Smithy]


def get_vp(strategy):
    return strategy.vp
