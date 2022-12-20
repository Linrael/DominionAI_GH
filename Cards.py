class Card:
    def __init__(self, name, cost, coins=0, vp=0):
        self.name = name
        self.cost = cost
        self.coins = coins
        self.vp = vp

    def __repr__(self):
        return self.name


Copper = Card('Copper', 0, coins=1)
Silver = Card('Silver', 3, coins=2)
Gold = Card('Gold', 6, coins=3)

Estate = Card('Estate', 2, vp=1)
Duchy = Card('Duchy', 5, vp=3)
Province = Card('Province', 8, vp=6)

NoCard = Card('NoCard', 0)

All_Cards = [Province, Gold, Duchy, Silver, Estate, Copper]
