from Player import *
from tqdm import tqdm

import pickle


def pickle_safe(qc, filename):
    qc2 = dict(qc)
    with open(filename + '.pickle', 'wb') as handle:
        pickle.dump(qc2, handle, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(filename):
    with open(filename + '.pickle', 'rb') as handle:
        return pickle.load(handle)


class GATournament:
    def __init__(self, strat, all_strats=30):
        self.all_strategies = [strat() for _ in range(all_strats)]

    def one_epoch(self, gps=15):  # games per strategy
        players = [Player(strat) for strat in self.all_strategies]  # to avoid reinitializing player again
        for player in players:
            for _ in range(gps):
                player.reset()  # instead of reinitializing new players we reset the one object we already have
                for turn in range(max_rounds):
                    player.draw_new_hand()
                    player.buy_acc_strat(player.strategy, turn)
                player.strategy.vp += player.calc_vp()  # add up all vps acquired in all gps
        self.all_strategies = sorted(self.all_strategies, key=get_vp, reverse=True)

    def evolve_strats(self, frac=6):
        self.all_strategies = evolve(self.all_strategies, frac)

    def run_tournament(self, epochs=100):
        for _ in tqdm(range(epochs)):
            self.one_epoch()
            self.evolve_strats()
        self.one_epoch()


# t1 = GATournament(LinearGA, all_strats=90)
# t1.run_tournament()
#
# for j in range(10):
#     for i in [0, 1, 2, -3, -2, -1]:
#         print(t1.all_strategies[j].prio_buys[i])
#     print(t1.all_strategies[j].vp)
#     print('\n')


class MCRLTournament:
    def __init__(self, q=None, c=None):
        self.player = Player(MCRL(q, c))

    def one_epoch(self, gps=15):
        player = self.player
        for _ in range(gps):
            player.strategy.start_game()
            player.reset()
            for turn in range(max_rounds):
                player.draw_new_hand()
                player.strategy.set_buy_prio(player, turn)
                player.play_actions()
                coins = player.calc_coins()
                for card in player.strategy.prio_buys:
                    if coins >= card.cost:
                        player.buy_card(card)
                        player.strategy.buy_accepted(card)
                        break
            player.strategy.game_ended(player.calc_vp())

    def last_epoch(self, gps=15):
        player = self.player
        for _ in range(gps):
            player.reset()
            for turn in range(max_rounds):
                player.draw_new_hand()
                player.strategy.set_best_buy_prio(player, turn)
                player.play_actions()
                coins = player.calc_coins()
                for card in player.strategy.prio_buys:
                    if coins >= card.cost:
                        player.buy_card(card)
                        player.strategy.buy_accepted(card)
                        player.strategy.count_buys(card, turn)
                        break
            player.strategy.vp = 0
