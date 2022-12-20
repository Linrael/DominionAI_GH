from Strats import *


class Player:
    def __init__(self, strategy):
        self.strategy = strategy
        self.deck = [Copper] * 7 + [Estate] * 3
        random.shuffle(self.deck)
        self.hand = []
        self.discardP = []

    def setup(self):
        self.deck = [Copper] * 7 + [Estate] * 3
        random.shuffle(self.deck)
        self.hand = []
        self.discardP = []

    def draw(self, n=5):
        length_deck = len(self.deck)
        if length_deck < n:
            [self.hand.append(self.deck.pop()) for _ in range(length_deck)]
            [self.deck.append(self.discardP.pop()) for _ in range(len(self.discardP))]
            random.shuffle(self.deck)
            [self.hand.append(self.deck.pop()) for _ in range(n - length_deck)]
        else:
            [self.hand.append(self.deck.pop()) for _ in range(n)]

    def buy_card(self, card):
        if card.name != NoCard.name:
            self.discardP.append(card)

    def calc_coins(self):
        coins = 0
        for card in self.hand:
            coins += card.coins
        return coins

    def buy_acc_strat(self, strategy):
        coins = self.calc_coins()
        for card in strategy.prio_buys:
            if coins >= card.cost:
                self.buy_card(card)
                break

    def discard_hand(self):
        [self.discardP.append(self.hand.pop()) for _ in range(len(self.hand))]

    def calc_vp(self):
        vp = 0
        for i in range(len(self.deck)):
            vp += self.deck[i].vp
        for i in range(len(self.hand)):
            vp += self.hand[i].vp
        for i in range(len(self.discardP)):
            vp += self.discardP[i].vp
        return vp

    def play_game(self, max_rounds):
        for _ in range(max_rounds):
            self.draw()
            self.buy_acc_strat(self.strategy)
            self.discard_hand()


class SinglePTournament:
    def __init__(self, max_rounds=20, all_strats=25, leading_strats=5):
        self.max_rounds = max_rounds
        self.all_strategies = [SimpleGA() for _ in range(all_strats)]
        self.leading_strats = self.all_strategies[:leading_strats]

    def one_epoch(self, max_rounds=20, gps=15):
        players = [Player(strat) for strat in self.all_strategies]
        for player in players:
            for i in range(gps):
                player.setup()
                player.play_game(max_rounds)
                player.strategy.vp += player.calc_vp()


t1 = SinglePTournament()
t1.one_epoch()
print(t1.all_strategies[1].vp)  # for i in range(len(t1.all_strategies)))
