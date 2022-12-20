from Player import *

class SinglePTournament:
    def __init__(self, max_rounds=20, all_strats=30):
        self.max_rounds = max_rounds
        self.all_strategies = [SimpleGA() for _ in range(all_strats)]

    def one_epoch(self, gps=15):
        players = [Player(strat) for strat in self.all_strategies]
        for player in players:
            for _ in range(gps):
                player.setup()
                player.play_game(self.max_rounds)
                player.strategy.vp += player.calc_vp()
        self.all_strategies = sorted(self.all_strategies, key=get_vp, reverse=True)

    def evolve_strats(self):
        self.all_strategies = evolve(self.all_strategies)


t1 = SinglePTournament(all_strats=90)
for _ in range(500):
    t1.one_epoch()
    t1.evolve_strats()
t1.one_epoch()


for ii in range(len(t1.all_strategies)):
    print(t1.all_strategies[ii].prio_buys)
    print(t1.all_strategies[ii].vp)
    print('\n')

