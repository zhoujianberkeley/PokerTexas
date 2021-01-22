import random
import pandas as pd
import time
import holdem_functions
import holdem_argparser
from holdem_functions import Card

df = pd.DataFrame(columns=['card','winning_percentage'])
def main():
    hole_cards, num, exact, board, file_name = holdem_argparser.parse_args()
    print(hole_cards, num, exact, board, file_name)
    #參考b站教程給出的一等强力手牌表
    # hole_cards =((Card('Ad'),Card('Ah')),(None,None))
    run(hole_cards, num, exact, board, file_name, True)
    # hole_cards =((Card('Ad'),Card('Kd')),(None,None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Ad'), Card('Ks')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Ks'), Card('Kd')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)

    #二等牌力
    # hole_cards = ((Card('Ad'), Card('Qh')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Qh'), Card('Kd')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Ad'), Card('Qd')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Qd'), Card('Kd')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Ad'), Card('Jd')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)

    # #三等牌力
    # hole_cards = ((Card('Ad'), Card('Td')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # for i in range(2,10):
    #     hole_cards = ((Card('Ad'), Card(str(i)+'d')), (None, None))
    #     run(hole_cards, num, exact, board, file_name, True)

    # #各种对子分布
    # hole_cards = ((Card('Jd'), Card('Js')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)
    # hole_cards = ((Card('Qd'), Card('Qs')), (None, None))
    # run(hole_cards, num, exact, board, file_name, True)


    #用于计算牌力分布而专门做的修改。
    # deck = holdem_functions.generate_deck(hole_cards, board)
    #
    # #不同花
    # value = ['Q', 'K', 'A']
    #
    # for i in range(len(value)):
    #     for j in range(i,len(value)):
    #         hole_cards = ((Card(value[i]+'d'), Card(value[j]+'s')), (None, None))
    #         for k in range(1000):
    #             random.seed(time.time())
    #             board = random.sample(deck, 3)
    #
    #             run(hole_cards, num, exact, board, file_name, True)
    #
    # #同花
    # for i in range(len(value)):
    #     for j in range(i+1,len(value)):
    #         hole_cards = ((Card(value[i]+'s'), Card(value[j]+'s')), (None, None),(None, None))
    #         run(hole_cards, num, exact, board, file_name, True)





def calculate(board, exact, num, input_file, hole_cards, verbose):
    args = holdem_argparser.LibArgs(board, exact, num, input_file, hole_cards)
    hole_cards, n, e, board, filename = holdem_argparser.parse_lib_args(args)
    return run(hole_cards, n, e, board, filename, verbose)

def run(hole_cards, num, exact, board, file_name, verbose):
    if file_name:
        input_file = open(file_name, 'r')
        for line in input_file:
            if line is not None and len(line.strip()) == 0:
                continue
            hole_cards, board = holdem_argparser.parse_file_args(line)
            deck = holdem_functions.generate_deck(hole_cards, board)
            run_simulation(hole_cards, num, exact, board, deck, verbose)
            print("-----------------------------------")
        input_file.close()
    else:
        deck = holdem_functions.generate_deck(hole_cards, board) # generact deck of cards
        return run_simulation(hole_cards, num, exact, board, deck, verbose)

def run_simulation(hole_cards, num, exact, given_board, deck, verbose):
    num_players = len(hole_cards)
    # Create results data structures which track results of comparisons
    # 1) result_histograms: a list for each player that shows the number of
    #    times each type of poker hand (e.g. flush, straight) was gotten
    # 2) winner_list: number of times each player wins the given round
    # 3) result_list: list of the best possible poker hand for each pair of
    #    hole cards for a given board
    result_histograms, winner_list = [], [0] * (num_players + 1)
    for _ in range(num_players):
        result_histograms.append([0] * len(holdem_functions.hand_rankings))
    # Choose whether we're running a Monte Carlo or exhaustive simulation
    board_length = 0 if given_board is None else len(given_board)
    # When a board is given, exact calculation is much faster than Monte Carlo
    # simulation, so default to exact if a board is given
    if exact:
    # if exact or (given_board is not None):
        generate_boards = holdem_functions.generate_exhaustive_boards
    else:
        generate_boards = holdem_functions.generate_random_boards

    num_unkonwn_pairs = sum([card == (None, None) for card in hole_cards])
    if num_unkonwn_pairs == 1:
        hole_cards_list = list(hole_cards)
        unknown_index = hole_cards.index((None, None))
        # max_times=2
        # current_times=0
        start_time = time.time()
        for filler_hole_cards in holdem_functions.generate_hole_cards(deck):
            # if current_times>max_times:
            #     break
            # current_times += 1
            hole_cards_list[unknown_index] = filler_hole_cards
            deck_list = list(deck)
            deck_list.remove(filler_hole_cards[0])
            deck_list.remove(filler_hole_cards[1])
            holdem_functions.find_winner(generate_boards, tuple(deck_list),
                                         tuple(hole_cards_list), num,
                                         board_length, given_board, winner_list,
                                         result_histograms)
        print("Time elapsed in for loop:", time.time() - start_time)
    elif num_unkonwn_pairs == 2:
        hole_cards_list = list(hole_cards)
        unknown_index1 = hole_cards.index((None, None))
        unknown_index2 = hole_cards.index((None, None), unknown_index1+1)
        start_time = time.time()
        for filler_hole_cards2 in holdem_functions.generate_hole_cards(deck, 4):

            hole_cards_list[unknown_index1] = filler_hole_cards2[0:2]
            hole_cards_list[unknown_index2] = filler_hole_cards2[2:4]
            deck_list = list(deck)
            [deck_list.remove(i) for i in filler_hole_cards2]

            holdem_functions.find_winner(generate_boards, tuple(deck_list),
                                         tuple(hole_cards_list), num,
                                         board_length, given_board, winner_list,
                                         result_histograms)
        print("Time elapsed in for loop:", time.time() - start_time)

    else:
        holdem_functions.find_winner(generate_boards, deck, hole_cards, num,
                                     board_length, given_board, winner_list,
                                     result_histograms)
    if verbose:
        global df
        df = holdem_functions.record_result(hole_cards, winner_list,result_histograms,df)
        # print(df)
        # holdem_functions.print_results(hole_cards, winner_list,
        #                                result_histograms)
    return holdem_functions.find_winning_percentage(winner_list)

if __name__ == '__main__':
    start = time.time()
    main()
    df.to_csv('winning_record_three_player.csv')
    print("\nTime elapsed(seconds): ", time.time() - start)


