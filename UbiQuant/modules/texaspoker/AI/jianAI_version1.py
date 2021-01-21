'''
    PretrainAI: v1_1版本
    详见AI-v1.1_interpretation.txt
'''
from lib.client_lib import State
from lib.client_lib import Player
from lib.client_lib import Hand
from lib.client_lib import Decision
import random

# todo 先看能否check，在give up 之前

def decode_card(num):
    name = ['spade', 'heart', 'diamond', 'club']
    value = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    return '%s, %s' %(name[num%4], value[num//4])


def translate_card(cards):
    '''
    translate the card string from decode_card into value/color pairs in consistency with holdem_calc.py
    '''
    results = []
    for card in cards:
        card = decode_card(card)
        color, value = card.split(', ')
        results.append(value + color[0])
    return results



def ai(id, state):
    weight = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    remain_card = list(range(0, 52))
    cards = state.sharedcards + state.player[id].cards
    player = state.player[id]
    my_hole_cards = translate_card(state.player[id].cards)
    board_cards = translate_card(state.sharedcards)

    # cal win ratio
    import holdem_calc
    if len(board_cards) == 0:
        win_props = holdem_calc.calculate(board=None, exact=False, num=20, input_file=None,
                              hole_cards=my_hole_cards + ["?", "?"], verbose=False)
    else:
        win_props = holdem_calc.calculate(board=board_cards, exact=False, num=20, input_file=None,
                              hole_cards=my_hole_cards + ["?", "?"], verbose=False)

    # 根据win ratio做决定
    decision = Decision()
    my_win_props = win_props[1]

    if id == 2 and state.turnNum == 0: #第一轮最后一个，就直接check
        decision.check = 1
        return decision

    if id == 0 and state.turnNum == 3: #最后一轮第一个不能放弃
        decision.check = 1
        return decision



    if my_win_props > 0.6:
        decision.raisebet = 1
        try:
            decision.amount = max(state.bigBlind, state.last_raise)
        except AttributeError:
            decision.amount = state.bigBlind

        if decision.amount > 400:
            if my_win_props > 0.6:
                decision.raisebet = 1
                decision.amount =  decision.amount
            else:
                decision.callbet = 1
                decision.raisebet = 0
        if decision.amount > 600:
            if my_win_props > 0.7:
                decision.raisebet = 1
                decision.amount = 2*decision.amount
            else:
                decision.callbet = 1
                decision.raisebet = 0

        if my_win_props > 0.7:
            decision.raisebet = 1
            decision.amount = 2 * decision.amount
        if my_win_props > 0.8:
            decision.raisebet = 1
            decision.amount = 3 * decision.amount

        if my_win_props > 0.9:
            decision.raisebet = 1
            decision.amount = 10 * decision.amount



    elif my_win_props > (0.3) and state.turnNum == 0:
        decision.callbet = 1
    elif my_win_props > (0.45) and state.turnNum == 1:
        decision.callbet = 1
    elif my_win_props > (0.3) and state.turnNum == 2 and decision.amount < 200:
        decision.callbet = 1

    # elif my_win_props < 0.2:
    #     decision.check = 1
    elif my_win_props < 0.15:
        decision.giveup = 1
    else:
        decision.giveup = 1

    # 最后一轮第二个，但是第一个放弃了，我不能放弃
    if decision.giveup == 1 and id == 1 and state.turnNum == 3 and state.playernum ==2:
        decision.giveup = 0
        decision.check = 1


    delta = state.minbet - state.player[state.currpos].bet
    if decision.callbet == 1 and delta == state.player[state.currpos].money:
        decision.callbet = 0
        decision.allin = 1
    if decision.callbet == 1 and state.minbet == 0:
        t = random.randint(0,2)
        if t == 0:
            decision.callbet = 0
            decision.raisebet = 1
            decision.amount = state.bigBlind
    print("jian position: ", state.player[id])
    print("\n")
    print("my card: ", my_hole_cards)
    print("board card: ", board_cards)
    print("my win_ratio: ", my_win_props)
    print("all win_ratio: ", win_props)
    print("jian decison: ", decision)
    return decision


#
# totalbet = 0
#     delta = state.minbet - state.player[state.currpos].bet
#     if delta >= state.player[state.currpos].money:
#         totalbet = 2000
#     else:
#         totalbet = state.player[state.currpos].totalbet + state.minbet
#
#     if num == 2:
#         # 两张牌
#         if cards[0] != cards[1]:
#             # 非对子
#             if max(cards) <= 8 and 0 not in cards:
#                 # 最大不超过9：若跟注后超过100，放弃。否则跟注
#                 if totalbet <= 100:
#                     decision.callbet = 1
#                 else:
#                     decision.giveup = 1
#             if max(cards) <= 11 and 0 not in cards:
#                 # 最大为10-Q：若跟注后超过150，放弃。否则跟注
#                 if totalbet <= 150:
#                     decision.callbet = 1
#                 else:
#                     decision.giveup = 1
#             else:
#                 # 最大为K-A： 若跟注后超过200，放弃。否则跟注
#                 if totalbet <= 200:
#                     decision.callbet = 1
#                 else:
#                     decision.giveup = 1
#         else:
#             # 对子
#             if max(cards) <= 11 and 0 not in cards:
#                 # 对子，不超过Q：跟注。若跟注后低于200，加注到200以上
#                 if totalbet < 200:
#                     decision = add_bet(state, 200)
#                 else:
#                     decision.callbet = 1
#             else:
#                 # 双A、双K：跟注。若跟注后低于300，加注到300
#                 if totalbet < 300:
#                     decision = add_bet(state, 300)
#                 else:
#                     decision.callbet = 1
#
#     elif num == 5:
#         # 五张牌
#         if sum < 4:
#             # 直接放弃
#             decision.giveup = 1
#         elif sum >= 4 and sum < 10:
#             # 若跟注后超过150，放弃。否则跟注
#             # 若已下的注额大于200, 且本次需跟注额不大于50， 则跟注
#             if totalbet < 150:
#                     decision.callbet = 1
#             elif state.player[state.currpos].totalbet + state.player[state.currpos].bet > 200 and delta < 50:
#                 decision.callbet = 1
#             else:
#                 decision.giveup = 1
#         elif sum >= 10 and sum < 20:
#             # 跟注。若跟注后低于300，加注到300
#             if totalbet < 300:
#                 decision = add_bet(state, 300)
#             else:
#                 decision.callbet = 1
#         elif sum >= 20 and sum < 50:
#             # 跟注。若跟注后低于600，加注到600
#             if totalbet < 600:
#                 decision = add_bet(state, 600)
#             else:
#                 decision.callbet = 1
#         else:
#             # allin
#             decision.allin = 1
#
#     elif num == 6:
#         # 六张牌
#         if sum < 2:
#             # 直接放弃
#             decision.giveup = 1
#         elif sum >= 2 and sum < 8:
#             # 若跟注后超过300，放弃。否则跟注
#             # 若已下的注额大于200, 且本次需跟注额不大于50， 则跟注
#             if totalbet < 300:
#                     decision.callbet = 1
#             elif state.player[state.currpos].totalbet + state.player[state.currpos].bet > 200 and delta < 50:
#                 decision.callbet = 1
#             else:
#                 decision.giveup = 1
#         elif sum >= 8 and sum < 20:
#             # 跟注。若跟注后低于300，加注到300
#             if totalbet < 300:
#                 decision = add_bet(state, 300)
#             else:
#                 decision.callbet = 1
#         elif sum >= 20 and sum < 40:
#             # 跟注。若跟注后低于600，加注到600
#             if totalbet < 600:
#                 decision = add_bet(state, 600)
#             else:
#                 decision.callbet = 1
#         else:
#             # allin
#             decision.allin = 1
#
#     elif num == 7:
#         # 七张牌
#         if level == 7:
#             # allin
#             decision.allin = 1
#         elif level == 6:
#             # 跟注，若跟注后低于600，加注到600
#             if totalbet < 600:
#                 decision = add_bet(state, 600)
#             else:
#                 decision.callbet = 1
#         elif level == 5:
#             # 跟注，若跟注后低于500，加注到500
#             if totalbet < 500:
#                 decision = add_bet(state, 500)
#             else:
#                 decision.callbet = 1
#         elif level == 4:
#             # 跟注，若跟注后低于400，加注到400
#             if totalbet < 400:
#                 decision = add_bet(state, 400)
#             else:
#                 decision.callbet = 1
#
#         elif level == 3:
#             # 若跟注后超过500，放弃。否则跟注。若跟注后低于300，加注到300
#             # 若已下的注额大于200, 且本次需跟注额不大于50， 则跟注
#             if totalbet < 300:
#                 decision = add_bet(state, 300)
#             elif totalbet < 500:
#                 decision.callbet = 1
#             elif state.player[state.currpos].totalbet + state.player[state.currpos].bet > 200 and delta < 50:
#                 decision.callbet = 1
#             else:
#                 decision.giveup = 1
#         elif level == 2:
#             if cards.count(0) == 2 or cards.count(12) == 2:
#                 # 双A双K 若跟注后超过200，放弃。否则跟注
#                 # 若已下的注额大于200, 且本次需跟注额不大于50， 则跟注
#                 if totalbet < 200:
#                     decision.callbet = 1
#                 elif state.player[state.currpos].totalbet + state.player[state.currpos].bet > 200 and delta < 50:
#                     decision.callbet = 1
#                 else:
#                     decision.giveup = 1
#             else:
#                 # 不超过双Q 若跟注后超过200，放弃。否则跟注
#                 if totalbet > 200:
#                     decision.giveup = 1
#                 else:
#                     decision.callbet = 1
#         elif level == 1:
#             decision.giveup = 1
#         else:
#             print('the num of cards is {}'.format(num))
#             assert(0)
#     if decision.callbet == 1 and delta == state.player[state.currpos].money:
#         decision.callbet = 0
#         decision.allin = 1
#     if decision.callbet == 1 and state.minbet == 0:
#         t = random.randint(0,2)
#         if t == 0:
#             decision.callbet = 0
#             decision.raisebet = 1
#             decision.amount = state.bigBlind
#     return decision
#
#
# # add_bet: 将本局总注额加到total
#
# def add_bet(state, total):
#     # amount: 本局需要下的总注
#     amount = total - state.player[state.currpos].totalbet
#     assert(amount > state.player[state.currpos].bet)
#     # Obey the rule of last_raised
#     minamount = state.last_raised + state.minbet
#     real_amount = max(amount, minamount)
#     # money_needed = real_amount - state.player[state.currpos].bet
#     decision = Decision()
#     decision.raisebet = 1
#     decision.amount = real_amount
#     return decision
