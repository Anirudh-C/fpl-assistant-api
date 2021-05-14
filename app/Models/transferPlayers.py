#All swap aptions are maintained as objects irrespective of whether they are feasible or not.
class Swap:
    def __init__(self, score, cost, p1, p2):
        self.del_score = score
        self.del_cost = cost
        self.player_in = p1
        self.player_out = p2

    def __bool__(self):
        return bool(self.player_in) or bool(self.player_out)


#Since swaps can be made only if position is same, function creates lists of players for different positions.
def positionwiseLists(allPlayers):

    players = [player for player in allPlayers if player['score'] != None]

    keepers = [player for player in players if player['element_type'] == 1]
    defenders = [player for player in players if player['element_type'] == 2]
    midfielders = [player for player in players if player['element_type'] == 3]
    forwards = [player for player in players if player['element_type'] == 4]

    return keepers, defenders, midfielders, forwards


def createSwaps(players, subs):

    swaps = []
    del_cost, del_score = 0.0, 0.0

    for sub in subs:
        for player in players:
            #print(sub['score'])
            del_score = sub['score'] - player['score']
            del_cost = player['now_cost'] - sub['now_cost']
            swap = Swap(del_score, del_cost, sub, player)
            swaps.append(swap)

    return swaps


def bestSwaps(swap_count, swaps, balance):

    #iterate through sorted bu score array to find first swap that is feasible.
    if swap_count == 0:
        return []
    if swap_count == 1:

        for swap in swaps:
            if swap.del_cost + balance >= 0:
                return [swap]

    else:

        best_score = 0
        first_swap, second_swap = None, None
        #iterate through multiple option (clever greedy) to figure out best combination of swaps.
        for swap1 in swaps:
            for swap2 in swaps[1:]:
                if swap1.del_score + swap2.del_score > best_score:
                    if swap1.del_cost + swap2.del_cost + balance >= 0 and swap1.player_in != swap2.player_in and swap1.player_out != swap2.player_out:
                        best_score = swap1.del_score + swap2.del_score
                        first_swap = swap1
                        second_swap = swap2
                else:
                    break

        return [first_swap, second_swap]


def scoreSort(swap):

    return swap.del_score


def transfer_algo(all_players: list, user_squad: list, avltransfers: int,
                  balance: float):

    for player in user_squad:
        all_players.remove(player)
    all_keepers, all_defenders, all_midfielders, all_forwards = positionwiseLists(
        all_players)
    user_keepers, user_defenders, user_midfielders, user_forwards = positionwiseLists(
        user_squad)

    #list of swaps possible for each position. Maintained separately.
    keeper_swaps = createSwaps(user_keepers, all_keepers)
    defender_swaps = createSwaps(user_defenders, all_defenders)
    midfielders_swaps = createSwaps(user_midfielders, all_midfielders)
    forwards_swaps = createSwaps(user_forwards, all_forwards)

    all_swaps = keeper_swaps + defender_swaps + midfielders_swaps + forwards_swaps
    all_swaps.sort(key=scoreSort, reverse=True)

    fpl_balance = 10 * balance
    my_swaps = bestSwaps(avltransfers, all_swaps, fpl_balance)
    our_swaps = []
    for swap in my_swaps:
        if swap:
            our_swaps.append((swap.player_out, swap.player_in))

    return our_swaps
