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

    def vp_one_strat(self, gps):  # games per strategy
        player = Player(self.all_strategies[0])
        vp = 0
        for _ in tqdm(range(gps)):
            player.reset()
            for turn in range(max_rounds):
                player.draw_new_hand()
                player.buy_acc_gastrat(player.strategy, turn)
            vp += player.calc_vp()  # add up all vps acquired in all gps
        print('Best strat on avg: ' + str(vp / gps))

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
        card_list = np.zeros(10)
        for i in range(max_rounds):
            print('Turn', i + 1)
            for j in range(len(self.player.strategy.buyable)):
                print(self.player.strategy.buyable[j], self.player.strategy.buy_at_turn[i, j], end='   ')
                card_list[j] += self.player.strategy.buy_at_turn[i, j]
            print('')
        print(card_list / 1_000_000)

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


'''
    # One GA training can look like this:

t = GATournament(StaticGA, all_strats=100)
t.run_tournament(3_000,15,1_000_000)

pickle_safe(t.all_strategies[0].weights, 'Static_100strats_3kep_15gps')

    # To get the buy menu of the best performing strategy use:
print(t.all_strategies[0].prio_buys)

    # To get the 1st and last 3 buys of the top x strategies averaged over avg games use:
t.print_buy_history(x, avg)

    # To load some saved data use:
ws = pickle_load('Lin_100strats_10kep_15gps_PLUS_10kep_20gps_ag')
t1 = GATournament(LinearGA, all_strats=100, weights=ws)
t1.vp_one_strat(1_000_000)
print(t5.all_strategies[0].prio_buys)

##############

    # One RL training can look like this:
    # IMPORTANT: Change in Strats.py in set_buy_prio and set_best_buy_prio current_state_... to the state function you want to use
t2 = MCRLTournament()
t2.run_tournament(10_000, 10_000, 1_000_000)  # Here we run 10k * 10k games. The 2 numbers have no meaning, just the product matters.
# I kept it that way to have a more useful progress bar

pickle_safe(dict(t2.player.strategy.q), 'q_turn_10kx10k')
pickle_safe(dict(t2.player.strategy.c), 'c_turn_10kx10k')

    # Print with:
t2.print_buy_history()

    # Look at Q-values (= see average vp for each state)
print(t2.player.strategy.q)

    # To load:
loadedq = pickle_load('q_turn_10kx10k')
loadedc = pickle_load('c_turn_10kx10k')

t3 = MCRLTournament(loadedq, loadedc)
t3.last_episode(1_000_000)
t3.print_buy_history()

############

    # To run some buy menu u put in manually use:
tc = CustomTournament()
tc.last_episode(1_000_000)
tc.print_buy_history()
'''
