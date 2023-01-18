from Player import *
from tqdm import tqdm

import pickle


def pickle_safe(qc, filename):
    # qc2 = dict(qc)
    with open(filename + '.pickle', 'wb') as handle:
        pickle.dump(qc, handle, protocol=pickle.HIGHEST_PROTOCOL)


def pickle_load(filename):
    with open(filename + '.pickle', 'rb') as handle:
        return pickle.load(handle)


class GATournament:
    def __init__(self, strat, all_strats=30, weights=None):
        if weights:
            self.all_strategies = [strat(weights) for _ in range(all_strats)]
            self.all_strategies = evolve(self.all_strategies, frac=10)
        else:
            self.all_strategies = [strat() for _ in range(all_strats)]

    def one_episode(self, gps):  # games per strategy
        players = [Player(strat) for strat in self.all_strategies]
        for player in players:
            for _ in range(gps):
                player.reset()
                for turn in range(max_rounds):
                    player.draw_new_hand()
                    player.buy_acc_gastrat(player.strategy, turn)
                player.strategy.vp += player.calc_vp()  # add up all vps acquired in all gps
        self.all_strategies = sorted(self.all_strategies, key=get_vp, reverse=True)
        self.all_strategies = evolve(self.all_strategies, frac=6)

    def last_episode(self, gps):  # games per strategy
        players = [Player(strat) for strat in self.all_strategies[:5]]
        for player in players:
            for _ in tqdm(range(gps)):
                player.reset()
                for turn in range(max_rounds):
                    player.draw_new_hand()
                    player.buy_acc_gastrat(player.strategy, turn)
                player.strategy.vp += player.calc_vp()  # add up all vps acquired in all gps
        self.all_strategies = sorted(self.all_strategies, key=get_vp, reverse=True)
        print('Best strat on avg: ' + str(self.all_strategies[0].vp / gps))

    def run_tournament(self, epochs=100, gps=15, gps_last_epoch=250):
        for _ in tqdm(range(int(epochs / 3))):
            self.one_episode(gps)
        for _ in tqdm(range(int(epochs / 3))):
            self.one_episode(2 * gps)
        for _ in tqdm(range(int(epochs / 3))):
            self.one_episode(3 * gps)
        self.last_episode(gps_last_epoch)

    def print_buy_history(self, top_strats=10, gps=200):
        for j in range(top_strats):
            for i in [0, 1, 2, -3, -2, -1]:
                print(self.all_strategies[j].prio_buys[i])
            print(self.all_strategies[j].vp / gps)
            print('\n')


class MCRLTournament:
    def __init__(self, q=None, c=None):
        self.player = Player(MCRL(q, c))

    def one_episode(self, gps=15):
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
            player.strategy.learn(player.calc_vp())

    def last_episode(self, gps):
        player = self.player
        vp = 0
        for _ in tqdm(range(gps)):
            player.strategy.start_game()
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
            vp += player.calc_vp()
        print('Average vp: ' + str(vp / gps))

    def run_tournament(self, epochs=100, gps=100, gps_last_epoch=1000):
        for _ in tqdm(range(epochs)):
            self.one_episode(gps)
        self.last_episode(gps_last_epoch)

    def print_buy_history(self):
        for i in range(max_rounds):
            print('Turn', i + 1)
            for j in range(len(self.player.strategy.buyable)):
                print(self.player.strategy.buyable[j], self.player.strategy.buy_at_turn[i, j], end='   ')
            print('')


class CustomTournament:
    def __init__(self):
        self.player = Player(MCRL())

    def last_episode(self, gps):  # games per strategy
        player = self.player
        vp = 0
        for _ in tqdm(range(gps)):
            player.reset()
            for turn in range(max_rounds):
                player.draw_new_hand()
                player.custom_buy(turn)
            vp += player.calc_vp()
        print('Avg: ' + str(vp / gps))

    def print_buy_history(self):
        for i in range(max_rounds):
            print('Turn', i + 1)
            for j in range(len(self.player.strategy.buyable)):
                print(self.player.strategy.buyable[j], self.player.strategy.buy_at_turn[i, j], end='   ')
            print('')
