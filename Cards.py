# Cards and some general input about the game
max_rounds = 20


class Card:
    def __init__(self, name, cost, coins=0, vp=0, is_action=False):
        self.name = name
        self.cost = cost
        self.coins = coins
        self.vp = vp
        self.is_action = is_action

    def __repr__(self):
        return self.name


class ActionCard(Card):
    def __init__(self, name, cost, coins=0, vp=0, plus_actions=0, plus_cards=0):
        super().__init__(name, cost, coins, vp, is_action=True)
        self.plus_actions = plus_actions
        self.plus_cards = plus_cards
    #
    # def play(self, player):
    #     player.actions -= 1
    #     player.actions += self.plus_actions
    #     player.draw(self.plus_cards)


Copper = Card('Copper', 0, coins=1)
Silver = Card('Silver', 3, coins=2)
Gold = Card('Gold', 6, coins=3)

Village = ActionCard('Village', 3, plus_actions=2, plus_cards=1)
Smithy = ActionCard('Smithy', 4, plus_cards=3)
Lab = ActionCard('Lab', 5, plus_actions=1, plus_cards=2)

Estate = Card('Estate', 2, vp=1)
Duchy = Card('Duchy', 5, vp=3)
Province = Card('Province', 8, vp=6)

NoCard = Card('NoCard', 0)

All_Cards = [Province, Duchy, Estate, Gold, Silver, Copper, Lab, Smithy, Village]
