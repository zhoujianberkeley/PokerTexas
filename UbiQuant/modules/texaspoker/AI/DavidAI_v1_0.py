'''
    DavidAI: v1_0版本
    详见德扑策略.md
'''
import re

from numba import np

from lib.client_lib import State
from lib.client_lib import Player
from lib.client_lib import Hand
from lib.client_lib import Decision
import time
import random


# todo 先看能否check，在give up 之前

def decode_card(num):
    name = ['spade', 'heart', 'diamond', 'club']
    value = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    return '%s, %s' % (name[num % 4], value[num // 4])


def translate_card(cards):
    """
    translate the card string from decode_card into value/color pairs in consistency with holdem_calc.py
    """
    results = []
    for card in cards:
        card = decode_card(card)
        color, value = card.split(', ')
        results.append(value + color[0])
    return results


def cal_win_ratio(hole_cards, board_cards, num_other_player=2, num_iter=2):
    """
    calculate win ratio
    """
    import holdem_calc_fast

    other_players = []
    for i in range(num_other_player):
        other_players = other_players + ["?", "?"]

    if len(board_cards) == 0:
        win_props = holdem_calc_fast.calculate(board=None, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + other_players, verbose=False)
    else:
        win_props = holdem_calc_fast.calculate(board=board_cards, exact=False, num=num_iter, input_file=None,
                                               hole_cards=hole_cards + other_players, verbose=False)
    return win_props


def count_raise(records, round, mypos):
    """
    计算某一轮的的raise和all in 次数
    剔除了自己的raise，剔除了大小盲的raise
    """
    record = records[round]
    r_num = 0
    a_num = 0
    for position in record.keys():
        if position == mypos:  # 跳过自己的position
            continue
        for action in record[position]:
            if re.findall("actionNum: [01]", action):  # 跳过actionNum 0 和 actionNum 1，大小盲
                continue

            if "raisebet" in action:
                r_num += 1
            if "allin" in action:
                a_num += 1
    return r_num, a_num


def adjust_win_ratio(state, mypos, win_ratio, records):
    """
    观察到all in, 胜率 - a_penalty
    观察到raise, 胜率 - r_penalty
    """
    round = state.turnNum  # 0, 1, 2, 3 for pre-flop round, flop round, turn round and river round

    r_penalty, a_penalty = 0.02, 0.05
    r_num, a_num = count_raise(records, round, mypos)

    if round == 0:
        # pre-flop round
        _adjust_win_ratio = win_ratio
    elif round == 1:
        # flop round
        _adjust_win_ratio = win_ratio - r_num * r_penalty - a_num * a_penalty
    elif round == 2:
        # turn round
        _adjust_win_ratio = win_ratio - r_num * r_penalty - a_num * a_penalty
    elif round == 3:
        # river round
        _adjust_win_ratio = win_ratio - r_num * r_penalty - a_num * a_penalty
    else:
        raise NotImplementedError(f"{round} is not valid round number")
    return _adjust_win_ratio


def cal_odds(state, mypos, action, amount=None):
    """
    4. 桌面赔率:当前桌面上有我的筹码x1，总筹码y1,假设轮到我现在决定要不要跟注z1，如果胜率 	   其中p是对手跟注z1的概率，一般来讲不应该下注。
	跟注：赔率=(x1+z1) / (y1+z1+ sum of p乘以z1)
	加注：赔率=(x1+z1) / (y1+z1+z1) if 除我之外只有一个玩家
		 赔率=(x1+z1) / (y1+z1+z1 + p乘以z1) if 除我之外有两个玩家
    """
    pot = state.moneypot   # money in the pot

    player = state.player[id]
    totalbet = player.totalbet + player.bet

    if action == "check":
        if not can_I_check(mypos, state):
            odds = np.infinity
        else:
            odds = totalbet/pot
    elif action == "callbet":
        if not can_I_callbet(mypos, state):
            odds = np.infinity
        else:
            # player.delta是跟注额度
            # sum([p.delta for p in state.player if p.active]) 是所有active player的跟注额度，p.delta = 0如果p已经callbet/raisebet
            if state.playernum == 2:
                odds = (totalbet + player.delta) / \
                       (pot + amount + sum([p.delta for p in state.player if (p.active and p is not player)]))
            elif state.playernum > 2:
                odds = (totalbet + player.delta) / \
                       (pot + player.delta + sum([0.5*p.delta for p in state.player if (p.active and p is not player)]))
    elif action == "raisebet":
        if state.playernum == 2:
            odds = (totalbet + amount) / \
                   (pot + amount + sum([(amount - p.bet) for p in state.player if (p.active and p is not player)]))
        elif state.playernum > 2:
            odds = (totalbet + amount) / \
                   (pot + amount + sum([0.5*(amount - p.bet) for p in state.player if (p.active and p is not player)]))
            #todo 考虑 对方没钱的时候
    else:
        raise NotImplementedError("illegal action")
    return odds



def cal_raise_amount(state, mypos, type):
    """
    基于之前玩家的raise，计算我们如果raise，所需要增加的总筹码
    """
    pot = state.moneypot  # money in the pot
    min_raise_amount = state.last_raised + state.minbet
    min_remains = remaining_money(state, mypos)

    if type == 'fullpot':
        raise_amount = pot
    elif type == 'halfpot':
        raise_amount = pot // 2
    else:
        raise_amount = min_raise_amount
    # 如果加注 大于 其他玩家所剩的最少的筹码数量，向下调整到所剩的最少的筹码数量
    if raise_amount > min_remains:
        raise_amount = min_remains
        print(f'raise_amount {raise_amount} > min_remains {min_remains}, decrease to {min_remains}')
    # 如果加注 小于 最小加注量，向上调整到最小加注量
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
    assert (amount > state.player[state.currpos].bet)
    # Obey the rule of last_raised
    minamount = state.last_raised + state.minbet
    real_amount = max(amount, minamount)
    # money_needed = real_amount - state.player[state.currpos].bet
    decision = Decision()
    decision.raisebet = 1
    decision.amount = real_amount
    return decision


def decide_raise_amount_type():
    '''
    由于不确定到底使用哪种raise amount，现在暂时先random一下
    '''
    random.seed(time.time())
    return random.sample(['fullpot', 'halfpot', 'other'], 1)


def can_I_check(id, state):
    max_bet_in_current_round = max([player.bet for player in state.player])
    # 需要跟注
    if state.player[id].bet < max_bet_in_current_round:
    # 可以改成
    # if state.player[id].bet < state.minbet:
        return False
    return True


def can_I_callbet(id, state):
    pass


def ai(id, state, records):
    my_hole_cards = translate_card(state.player[id].cards)
    board_cards = translate_card(state.sharedcards)

    # cal win ratio
    win_props = cal_win_ratio(my_hole_cards, board_cards, num_iter=2)
    my_win_props = win_props[1]

    # adjust win ratio
    my_win_props = adjust_win_ratio(state, id, my_win_props, records)

    decision = Decision()

    # 在最初局，只使用二人对弈胜率来评判牌力大小
    if not state.turnNum:
        hole_card_power = cal_win_ratio(my_hole_cards, board_cards, num_other_player=1)[1]

        # 一等手牌
        if hole_card_power > 0.76:

            num_active_player = sum([player.active for player in state.player])

            # 还剩两个对手，持续下注
            if num_active_player > 2:
                decision.amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
                decision.raisebet = 1
                return decision

            # call或check
            if num_active_player <= 2:
                if can_I_check(id, state):
                    decision.check = 1
                    return decision
                else:
                    decision.callbet = 1
                    return decision

        # 二等手牌
        if hole_card_power > 0.71:
            return

        # 三等手牌
        if hole_card_power > 0.65:
            return

        # 四等手牌
        if hole_card_power > 0.57:
            return

        ##三人局，0号button，1号小盲，2号大盲

        # 弱势手牌，无成本直接弃牌
        if state.currpos == 0:
            decision.giveup = 1
            return decision

        if state.currpos == 1:
            return

        if state.currpos == 2:
            return



    # 桌面上已出现公共牌，3，4，5张策略相同
    else:

        if can_I_check():
            return
