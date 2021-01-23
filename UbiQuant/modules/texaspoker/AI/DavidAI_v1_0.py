"""
    DavidAI: v1_0版本
    详见德扑策略.md
"""

import numpy as np
import random
import re
import time

from lib.client_lib import State
from lib.client_lib import Player
from lib.client_lib import Hand
from lib.client_lib import Decision
from lib.AI_logger import AI_Logger


logger = AI_Logger('debug_logger')

record_logger = AI_Logger('record_logger')

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


def cal_win_ratio(hole_cards, board_cards, num_other_player, num_iter):
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


def am_I_the_last_raiser(records, round, mypos):
    '''
    主要为了判断本轮最新一次加注的是不是自己，防止出现在某一轮中一直加注.(不确定官方网站处理时是否会自动处理这种行为）
    '''
    if round not in records.keys():
        return False

    record = records[round]
    latest_raiser = ''
    for position in record.keys():
        for action in record[position]:
            if re.findall("actionNum: [01]", action):  # 跳过actionNum 0 和 actionNum 1，大小盲
                continue
            if "raisebet" in action or "allin" in action:
                latest_raiser = position
    return latest_raiser == mypos

def do_hole_cards_have_pair(hole_cards):
    return hole_cards[0][0]==hole_cards[1][0]

def do_hole_cards_have_A_suit(hole_cards):
    return hole_cards[0][1]==hole_cards[1][1] and (hole_cards[0][0]=='A' or hole_cards[1][0]=='A')

# def action_of_a_player_in_a_round(records,round,player_pos):
#     """
#     计算某一轮的的raise和all in 次数
#     剔除了自己的raise，剔除了大小盲的raise
#     """
#     action_dict = dict()
#     record = records[round]
#     r_num = 0
#     a_num = 0
#     c_num = 0
#     for position in record.keys():
#         if position != player_pos:
#             continue
#         for action in record[position]:
#             if re.findall("actionNum: [01]", action):  # 跳过actionNum 0 和 actionNum 1，大小盲
#                 continue
#
#             if "raisebet" in action:
#                 r_num += 1
#             if "allin" in action:
#                 a_num += 1
#             if 'check' in action:
#                 c_num +=1
#
#     action_dict['raisebet']=r_num
#     action_dict['allin'] = a_num
#     action_dict['check'] = c_num
#     return action_dict

def count_raise(records, round, mypos, skip_self=True):
    """
    计算某一轮的的raise和all in 次数
    剔除了自己的raise，剔除了大小盲的raise
    skip_self:是否跳过自己的flag变量
    """

    r_num, a_num = 0, 0
    if round not in records.keys():
        logger.debug(f"{round} not in records keys")
        return r_num, a_num

    record = records[round]
    for position in record.keys():
        if position == mypos and skip_self:  # 跳过自己的position
            continue
        for action in record[position]:
            if re.findall("actionNum: [01]", action):  # 跳过actionNum 0 和 actionNum 1，大小盲
                continue
            if "raisebet" in action:
                r_num += 1
            elif "allin" in action:
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
    桌面赔率:当前桌面上有我的筹码x1，总筹码y1,假设轮到我现在决定要不要跟注z1，如果胜率 	   其中p是对手跟注z1的概率
	跟注：赔率=(x1+z1) / (y1+z1+ sum of p乘以z1)
	加注：赔率=(x1+z1) / (y1+z1+z1) if 除我之外只有一个玩家
		 赔率=(x1+z1) / (y1+z1+z1 + p乘以z1) if 除我之外有两个玩家
    """
    pot = state.moneypot  # money in the pot
    logger.debug("id2"+str(mypos))
    player = state.player[mypos]
    totalbet = player.totalbet + player.bet

    if action == "check":
        if not can_I_check(mypos, state):
            odds = np.inf
        else:
            odds = totalbet / pot
    elif action == "callbet":
        if not can_I_callbet(mypos, state):
            odds = np.inf
        else:
            # player.delta是跟注额度
            # sum([p.diff_callbet for p in state.player if p.active]) 是所有active player的跟注额度，p.diff_callbet = 0如果p已经callbet/raisebet
            if state.playernum == 2:
                odds = (totalbet + player.diff_callbet) / \
                       (pot + player.diff_callbet + sum([p.diff_callbet for p in state.player if (p.active and p is not player)]))
            elif state.playernum > 2:
                odds = (totalbet + player.diff_callbet) / \
                       (pot + player.diff_callbet + sum(
                           [0.5 * p.diff_callbet for p in state.player if (p.active and p is not player)]))
    elif action == "raisebet": # todo 考虑 对方没钱的时候
        if state.playernum == 2:
            odds = (totalbet + amount) / \
                   (pot + amount + sum([(amount - p.bet) for p in state.player if (p.active and p is not player)]))
        elif state.playernum > 2:
            odds = (totalbet + amount) / \
                   (pot + amount + sum(
                       [0.5 * (amount - p.bet) for p in state.player if (p.active and p is not player)]))
    elif action == "allin":
        # 如果allin 加的注 > raisebet所需要最小的注，odds和raisebet一样的
        if player.money > state.last_raised + state.minbet:
            return cal_odds(state, mypos, action="raisebet", amount=player.money)
        # 如果allin 加的注 < raisebet所需要最小的注
        if state.playernum == 2:
            odds = (totalbet + player.money) / \
                   (pot + player.money + sum([p.diff_callbet for p in state.player if (p.active and p is not player)]))
        elif state.playernum > 2:
            odds = (totalbet + player.money) / \
                   (pot + player.money + sum([0.5*p.diff_callbet for p in state.player if (p.active and p is not player)]))
    else:
        raise NotImplementedError("illegal action")
    return odds


def cal_raise_amount(state, mypos, type):
    """
    基于之前玩家的raise，计算我们如果raise，所需要增加到的总筹码
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
    ##疑问:那这样的话，是不是假设剩下人的最小筹码如果赶不上min_raise_amount，我还是会选择raise？


def remaining_money(state, mypos):
    """
    查其他玩家最少还剩多少钱
    """
    remains = []
    for play_num in range(len(state.player)):
        if play_num == mypos:
            continue
        else:
            remains.append(state.player[play_num].money)
    return min(remains)


def add_bet(state, total):
    """
    用于raise, 将本局总注额加到total
    """
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
    # 需要跟注
    if state.player[id].bet < state.minbet:
        return False
    return True

def can_I_callbet(id, state):

    # 有钱跟注,而且严格区分callbet和check，如果前人没有raise，就不能call
    if state.minbet-state.player[id].bet<state.player[id].money and not can_I_check(id,state):
        return True
    return False


def can_I_raisebet(id, state, records, amount,allow_continue_raisebet=False):
    #有钱加注

    # min_raise_amount = state.last_raised + state.minbet
    min_raise_amount = amount
    if allow_continue_raisebet:
        if state.player[id].money> (min_raise_amount - state.player[id].bet): 
            return True
        return False
    else:  # 只有本轮的最新加注者不是我自己时才能加注
        if state.player[id].money> (min_raise_amount - state.player[id].bet)and not am_I_the_last_raiser(records,state.turnNum,state.currpos):
            return True
        return False

# todo shentingwei 暂定逻辑 待修改
def can_I_allin(id,state,records,amount):
    if not can_I_check(id,state) and not can_I_callbet(id,state) and not can_I_raisebet(id,state,records,amount):
        return True
    return False

def ai(id, state, records, num_iter=5):
    my_hole_cards = translate_card(state.player[id].cards)
    board_cards = translate_card(state.sharedcards)

    record_logger.info('***********record start***************')
    record_logger.info('sharedcards:%s' % str(state.sharedcards))
    for x in state.sharedcards:
        record_logger.info('%s. ' % decode_card(x))
    record_logger.info('cards:%s' % str(state.player[id].cards))
    for x in state.player[id].cards:
        record_logger.info('%s. ' % decode_card(x))
    record_logger.info('\n')
    record_logger.info('Have money {} left'.format(state.player[id].money))
    record_logger.info('\n')
    record_logger.info(f"round {state.turnNum}")

    decision = Decision()

    # 在最初局，只使用二人对弈胜率来评判牌力大小
    if state.turnNum == 0:
        r_num, a_num = count_raise(records,state.turnNum,state.currpos,skip_self=False)
        time_of_rise = r_num + a_num

        # 算2个人的牌力
        hole_card_power = cal_win_ratio(my_hole_cards, board_cards, num_other_player=1, num_iter=num_iter)[1]
        record_logger.info(f"pre flop round， 牌力{hole_card_power}")
        record_logger.info('***********record finish***************')

        # 一等手牌
        if hole_card_power > 0.64:
            num_active_player = state.playernum
            # 还剩两个对手，持续下注
            if num_active_player > 2:
                amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
                if can_I_raisebet(id,state,records,amount,allow_continue_raisebet=True):
                    decision.amount = amount
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
        if hole_card_power > 0.605:

            #之前没有起raise的或者没有3bet的,优先raise
            if time_of_rise<=1:
                amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
                if can_I_raisebet(id, state, records, amount):
                    decision.amount = amount
                    decision.raisebet = 1
                    return decision

            #出现4bet，该弃牌了
            if time_of_rise >=3:  #todo 万一我加了很多钱呢，是否加入odds
                decision.giveup = 1
                return decision

            decision.callbet=1
            return decision

        # 三等手牌
        if hole_card_power > 0.550:
            # 没有人rasie
            if time_of_rise==0:
                amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
                if can_I_raisebet(id, state, records, amount):
                    decision.amount = amount
                    decision.raisebet = 1
                    return decision
            # 有人rasie，我3bet

            if time_of_rise == 1 and state.currpos==2:
                amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
                if can_I_raisebet(id, state, records, amount):
                    decision.amount = amount
                    decision.raisebet = 1
                    return decision

            #出现3bet及以上，而且不是我发起的，弃牌
            if time_of_rise >=2 and not am_I_the_last_raiser(records,state.turnNum,state.currpos):
                decision.giveup=1
                return decision

            decision.callbet = 1
            return decision

        # 四等手牌
        if hole_card_power > 0.408:
            # 只玩带A或者对子牌 #todo jian understand the logic
            if do_hole_cards_have_A_suit(my_hole_cards) or do_hole_cards_have_pair(my_hole_cards):
                if can_I_check(id,state):
                    decision.check =1
                    return decision

                #最多只跟一個大盲
                if can_I_callbet(id,state) and time_of_rise<=1 and state.minbet ==40:
                    decision.callbet =1
                    return decision

            decision.giveup =1
            return decision

        ##三人局，0号button，1号小盲，2号大盲

        # 弱势手牌，无成本直接弃牌
        if state.currpos == 0:
            decision.giveup = 1
            return decision

        #小盲位
        if state.currpos == 1:
            if state.minbet == 40:
                win_props = cal_win_ratio(my_hole_cards, board_cards, num_other_player=2, num_iter=1)
                my_win_props = win_props[1]

                # adjust win ratio
                my_win_props = adjust_win_ratio(state, id, my_win_props, records)

                if can_I_callbet(id, state) and my_win_props > cal_odds(state,state.currpos,'callbet'):
                    decision.callbet = 1
                    return decision

            decision.giveup=1
            return decision

        if state.currpos == 2:
            if can_I_check(id,state):
                decision.check=1
                return decision

            decision.giveup=1
            return decision

    # 桌面上已出现公共牌，3，4，5张策略相同
    else:
        # cal win ratio
        win_props = cal_win_ratio(my_hole_cards, board_cards, num_other_player=state.playernum-1, num_iter=2)
        my_win_props = win_props[1]
        record_logger.info(f"牌力{my_win_props}")
        # adjust win ratio
        my_win_props = adjust_win_ratio(state, id, my_win_props, records)
        record_logger.info(f"调整牌力{my_win_props}")
        record_logger.info('***********my decision***************')
        amount = cal_raise_amount(state, state.currpos, decide_raise_amount_type())
        # 提取合法的行为
        dict_of_move = dict()
        dict_of_move['check'] = can_I_check(id,state)
        dict_of_move['callbet'] = can_I_callbet(id,state)
        dict_of_move['raisebet'] = can_I_raisebet(id,state,records,amount)
        dict_of_move['allin'] = can_I_allin(id,state,records,amount)

        best_action = 'callbet'
        min_odds = np.inf
        for action in dict_of_move.keys():
            if dict_of_move[action]:
                if action == 'raisebet': # todo Jian update decide raise amount type
                    _amount = amount
                    current_odds = cal_odds(state, state.currpos, action, amount=_amount)
                    record_logger.info(f"{action} {amount}的赔率：{current_odds}")
                else:
                    current_odds = cal_odds(state, state.currpos, action, amount=None)
                    record_logger.info(f"{action} 的赔率：{current_odds}")

                if current_odds <= min_odds:
                    min_odds = current_odds
                    best_action = action
        record_logger.info(f"最小赔率：{min_odds}")
        if my_win_props < min_odds:
            if can_I_check(id,state):
                decision.check = 1
            else:
                decision.giveup= 1
            return decision

        exec('decision.'+best_action+'=1')
        if best_action == 'raisebet': # todo Jian update decide raise amount type
            decision.amount = amount
        return decision

