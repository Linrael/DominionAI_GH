from Strats import *


class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.deck = [Copper] * 7 + [Estate] * 3
        random.shuffle(self.deck)
        self.hand = []
        self.table = []
        self.discardP = []
        self.actions = 1

    def reset(self):
        self.deck = [Copper] * 7 + [Estate] * 3
        random.shuffle(self.deck)
        self.hand = []
        self.table = []
        self.discardP = []
        self.actions = 1

    def draw(self, n=1):
        length_deck = len(self.deck)
        if length_deck >= n:
            [self.hand.append(self.deck.pop()) for _ in range(n)]
        else:
            if length_deck + len(self.discardP) >= n:
                [self.hand.append(self.deck.pop()) for _ in range(length_deck)]
                [self.deck.append(self.discardP.pop()) for _ in range(len(self.discardP))]
                random.shuffle(self.deck)
                [self.hand.append(self.deck.pop()) for _ in range(n - length_deck)]
            else:
                [self.hand.append(self.deck.pop()) for _ in range(length_deck)]
                [self.hand.append(self.discardP.pop()) for _ in range(len(self.discardP))]

    def draw_new_hand(self):
        [self.discardP.append(self.hand.pop()) for _ in range(len(self.hand))]
        [self.discardP.append(self.table.pop()) for _ in range(len(self.table))]
        self.actions = 1
        self.draw(5)

    def buy_card(self, card):
        if card.name != NoCard.name:
            self.discardP.append(card)

    def play_card(self, card):
        self.hand.remove(card)
        self.table.append(card)
        self.actions += card.plus_actions
        self.draw(card.plus_cards)
        self.actions -= 1

    def play_actions(self):
        while self.actions > 0:
            for action in self.strategy.prio_actions:
                if action in self.hand:
                    self.play_card(action)
                    break
            else:
                break
        # for card in self.hand:
        #     if card.is_action and card.plus_actions > 0:  # 1st play all +action cards, since it can never hurt
        #         card.play(self)
        #     if card.is_action and card.plus_actions == 0 and self.actions > 0:
        #         card.play(self)

    def calc_coins(self):
        coins = 0
        for card in self.hand:
            coins += card.coins
        return coins

    def buy_acc_strat(self, strategy, turn):  # buy according to strat
        self.play_actions()
        coins = self.calc_coins()
        for card in strategy.prio_buys[turn]:
            if coins >= card.cost:
                self.buy_card(card)
                break

    def calc_vp(self):
        vp = 0
        for i in range(len(self.deck)):
            vp += self.deck[i].vp
        for i in range(len(self.hand)):
            vp += self.hand[i].vp
        for i in range(len(self.discardP)):
            vp += self.discardP[i].vp
        return vp
