'''
    DavidAI: v1_0版本
    详见德扑策略.md
'''
import re

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

def cal_win_ratio(hole_cards, board_cards, num_iter=2):
    '''
    calculate win ratio
    '''
    import holdem_calc_fast
    if len(board_cards) == 0:
        win_props = holdem_calc_fast.calculate(board=None, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + ["?", "?", "?", "?"], verbose=False)
    else:
        win_props = holdem_calc_fast.calculate(board=board_cards, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + ["?", "?", "?", "?"], verbose=False)
    return win_props

def cal_odds(action, ):
    '''
    计算赔率
    '''
    pass

def count_raise(records, round, mypos):
    '''
    计算某一轮的的raise和all in 次数
    剔除了自己的raise，剔除了大小盲的raise
    '''
    record = records[round]
    r_num = 0
    a_num = 0
    for position in record.keys():
        if position == mypos:  # 跳过自己的position
            continue
        for action in record[position]:
            if re.findall("actionNum: [01]",action):  # 跳过actionNum 0 和 actionNum 1，大小盲
                continue

            if "raisebet" in action:
                r_num += 1
            if "allin" in action:
                a_num += 1
    return r_num, a_num

def adjust_win_ratio(state, mypos, win_ratio, records):
    '''
    观察到all in, 胜率 - a_penalty
    观察到raise, 胜率 - r_penalty
    '''
    round = state.turnNum  # 0, 1, 2, 3 for pre-flop round, flop round, turn round and river round

    r_penalty, a_penalty = 0.02, 0.05
    r_num, a_num = count_raise(records, round, mypos)

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


def ai(id, state, records):
    weight = [0, 1, 2, 4, 8, 16, 32, 64, 128, 256, 512]
    remain_card = list(range(0, 52))
    cards = state.sharedcards + state.player[id].cards
    player = state.player[id]
    my_hole_cards = translate_card(state.player[id].cards)
    board_cards = translate_card(state.sharedcards)

    # cal win ratio
    win_props = cal_win_ratio(my_hole_cards, board_cards, num_iter=2)
    my_win_props = win_props[1]

    # adjust win ratio
    my_win_props = adjust_win_ratio(state, id, my_win_props, records)

    # 根据win ratio做决定
    decision = Decision()


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


