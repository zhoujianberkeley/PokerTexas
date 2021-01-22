'''
    DavidAI: v1_0版本
    详见德扑策略.md
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

def cal_win_ratio(hole_cards, board_cards, num_other_player = 2,num_iter=2):
    '''
    calculate win ratio
    '''
    import holdem_calc_fast

    other_players = []
    for i in range(num_other_player):
        other_players = other_players+["?","?"]

    if len(board_cards) == 0:
        win_props = holdem_calc_fast.calculate(board=None, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + other_players, verbose=False)
    else:
        win_props = holdem_calc_fast.calculate(board=board_cards, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + other_players, verbose=False)
    return win_props



def cal_odds():
    '''
    计算赔率
    '''
    pass

def adjust_win_ratio(state, mypos, win_ratio, records):
    '''
    观察到all in, 胜率 - a_penalty
    观察到raise, 胜率 - r_penalty
    '''
    round = state.turnNum = 0  # 0, 1, 2, 3 for pre-flop round, flop round, turn round and river round
    records = records[f'round{round}']

    r_num, r_penalty = 0, 0.02
    a_num, a_penalty = 0, 0.05
    for position in records:
        if position == f"position{mypos}": #跳过自己的position
            continue
        for action in records[position]:
            if "raisebet" in action:
                r_num += 1
            if "allin" in action:
                a_num += 1

    if round == 0:
        # pre-flop round
        adjust_win_ratio = win_ratio
    elif round == 1:
        # flop round
        adjust_win_ratio = win_ratio - r_num*r_penalty - a_num*a_penalty
    elif round == 2:
        # turn round
        adjust_win_ratio = win_ratio - r_num * r_penalty - a_num * a_penalty
    elif round == 3:
        # river round
        adjust_win_ratio = win_ratio - r_num * r_penalty - a_num * a_penalty
    else:
        raise NotImplementedError(f"{round} is not valid round number")
    return adjust_win_ratio

def cal_raise_amount(state, mypos, type):
    '''
    基于之前玩家的raise，计算我们如果raise，所需要增加的总筹码
    '''
    increase = state.last_raised
    minimum = state.minbet
    pot = state.moneypot # money in the pot
    min_raise_amount = increase + minimum
    min_remains = remaining_money(state, mypos)

    if type == 'fullpot':
        raise_amount = pot
    elif type == 'halfpot':
        raise_amount = pot//2
    else:
        raise_amount = min_raise_amount

    if raise_amount > min_remains:
        raise_amount = min_remains
        print(f'raise_amount {raise_amount} > min_remains {min_remains}, decrease to {min_remains}')

    if raise_amount < min_raise_amount:
        raise_amount = min_raise_amount
        print(f'raise_amount {raise_amount} < min_raise_amount {min_raise_amount}, increase to {min_raise_amount}')

    return raise_amount

def remaining_money(state, mypos):
    '''
    查其他玩家最少还剩多少钱
    '''
    remains = []
    for play_num in range(len(state.player)):
        if play_num == mypos:
            continue
        else:
            remains.append(state.player[play_num].money)
    return min(remains)

def add_bet(state, total):
    '''
    用于raise, 将本局总注额加到total
    '''
    # amount: 本局需要下的总注
    amount = total - state.player[state.currpos].totalbet
    assert(amount > state.player[state.currpos].bet)
    # Obey the rule of last_raised
    minamount = state.last_raised + state.minbet
    real_amount = max(amount, minamount)
    # money_needed = real_amount - state.player[state.currpos].bet
    decision = Decision()
    decision.raisebet = 1
    decision.amount = real_amount
    return decision


def ai(id, state):


    my_hole_cards = translate_card(state.player[id].cards)
    board_cards = translate_card(state.sharedcards)
    # 在最初局，只使用二人对弈胜率来评判牌力大小
    if not state.turnNum:
        hole_card_power = cal_win_ratio(my_hole_cards,board_cards,num_other_player=2)

        if hole_card_power>0.76:
            return

        if hole_card_power>0.71:
            return

        if hole_card_power>0.65:
            return
        if hole_card_power>0.57:

            return


        return


    #桌面上已出现公共牌，3，4，5张策略相同
    else:

        return


