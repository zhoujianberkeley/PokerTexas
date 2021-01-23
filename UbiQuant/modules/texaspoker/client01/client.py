import glob
import pickle
import sys
import threading
import grpc
import sys
from  pathlib import Path
import time
import os

# **************************************modify here to add syspath if you need. ***************************
_current_root = str(Path(__file__).resolve().parents[1])
sys.path.append(_current_root)
sys.path.append('.')
# ******************************************************************************************

# `ISTESTING` is set to True when you are testing your program
# should be set to False when test is finished.
#**************************************************************************
ISTESTING = False
#******************************************************************************

# *********************modify here to change import path if you need ***********************
import communicate.dealer_pb2 as dealer_pb2
import communicate.dealer_pb2_grpc as rpc
from lib.client_lib import State
from lib.client_lib import Player
from lib.client_lib import MessageType_HeartBeat
from lib.client_lib import MessageType_StateUpdate
from lib.client_lib import MessageType_GameDecision
from lib.client_lib import MessageType_StateControl
from lib.client_lib import MessageType_ClientInit
from lib.client_lib import MessageType_GameOver
from lib.client_lib import MessageType_InvalidToken
from lib.client_lib import MessageType_GameStarted
from lib.client_lib import MessageType_IllegalDecision
from lib.AI_logger import AI_Logger
# *******************************************************************************************




# **************************************modify here to use your own RLAI! ***************************
# from AI.v1_1 import ai
from AI.DavidAI_v1_0 import ai
# *************************************************************************************************



# **************************************modify here to set address and port ***********************
address = '47.103.23.116'
port = 56713 # 56703-56720
# 56720是有前端的port，UI链接http://47.103.23.116:56702/card?name=01David&passwd=kxUEGLXn
# 如果是非56720别的port，得把client02,client03都得连进去

# *************************************************************************************************


#**********
# Position 0 is always the botton.
# bigBlind is set defalut to 20 and smallBlind is set default to 10.
# BigBlind may be changed during the competition.
# Every user has 1000 counters at the beginning.
# If a user runs out of counters, the user will not be allowed to join any game anymore.
# The player registered at position 1 is the default smallBlind.
# The player registered at position 2 is the default bigBlind.
# Your ai doesn't need to send the smallBlind or the bigBlind decision to the sever.
# The server will give the blindbet automatically and brodcast the desicion to all the player.
#*********

record_logger = AI_Logger('record_logger')

CLIENT_VERSION = 'V1.4'

class Client(object):
    def __init__(self, u: str, AI, logger, pos=0):
        self.client_reset(u, AI, logger, pos)

        key_file = self.username + '_key.txt'
        self.key = 'NULL'

        self.cond = threading.Condition()

        if os.path.exists(key_file):
            self.key = open(key_file).read()
        print('self.key is inited to ' + self.key)


    def client_reset(self, u: str, AI, logger, pos):
        self.username = u
        # create a gRPC channel + stub
        channel = grpc.insecure_channel(address + ':' + str(port))
        self.conn = rpc.GameStub(channel)
        self.ai = AI
        self._lock = threading.Lock()
        self._decision_so_far = []  # history of the decision info from the server
        self._decision_record = {}  # history of the decision info from the server,
        # first key is round, second key is player id, value is decision


        self._new_response = []     # response list from the server
        self._new_request = []      # request list waiting to send to the server

        self.mypos = pos
        self.initMoney = -1
        self.bigBlind = -1
        self.totalPlayer = -1
        self.button = -1
        self.step = -1
        self.logger = logger
        if self.logger is None:
            self.logger = AI_Logger('root_logger')
        self.state = State(self.logger, self.totalPlayer, self.initMoney, self.bigBlind, self.button)

        self.initialized = False
        self.stoped = False
        self.round = 0
        self.allowheartbeat = True
        self.heartbeaklock = threading.Lock()

    def print_stateupdate(self, res):

        # self.logger.info('$$$ giveup=%d, check=%d, allin=%d, callbet=%d, raisebet=%d, amount=%d, pos=%d' % (res.giveup, res.check, res.allin, res.callbet, res.raisebet, res.amount, res.pos))
        string = '[ACTION]: player at {} '.format(res.pos)
        if res.giveup:
            string += 'giveup '
        if res.check:
            string += 'check '
        if res.allin:
            string += 'allin '
        if res.callbet:
            if res.actionNum == 0:
                string += 'add smallBlind {} '.format(self.bigBlind//2)
            elif res.actionNum == 1:
                string += 'add bigBlind {} '.format(self.bigBlind)
            else:
                string += 'callbet ' # 跟注
        if res.raisebet:
            string += 'raisebet to {} '.format(res.amount)
        string += 'in round {}. actionNum: {}'.format(self.round, res.actionNum)
        self.logger.info(string)
        # print(self._decision_record)
        self.record_decision(res, string)

    def record_decision(self, res, record):
        _round = self.round
        _position = res.pos
        if _round not in self._decision_record.keys():
            self._decision_record[_round] = {}
        if _position not in self._decision_record[_round].keys():
            self._decision_record[_round][_position] = []
        self._decision_record[_round][_position].append(record)

    def chat_with_server(self):
        while True:
            self.cond.acquire()
            while True:
                while len(self._new_request) != 0:
                    # yield a resquest from the request list to the server
                    msg = self._new_request.pop(0)
                    yield msg
                self.cond.wait()
            self.cond.release()

    def run(self):
        while True:
            # every 1 sec append a request to the list
            self.add_request(self.HeartBeat())
            time.sleep(0.5)
            if self.stoped:
                self.heartbeaklock.acquire()
                self.allowheartbeat = False
                self.heartbeaklock.release()
                self.client_reset(self.username, self.ai, self.logger, 0)
                self.heartbeaklock.acquire()
                self.allowheartbeat = True
                self.heartbeaklock.release()

                # self.logger.info('Game is finished. Client %d exit.'%(self.mypos))
                # break

    def start(self):
        responses = self.conn.GameStream(self.chat_with_server())
        for res in responses:
            # self.logger.info('res.type %d'%(res.type))
            self._new_response.append(res)
            # if self.stoped:
            #     break
            if res.type == MessageType_GameDecision:
                # server asking for a decision from the client
                self.state.currpos = res.pos
                if res.pos == self.mypos:
                    print("-------------------------------------")
                    print(self._decision_so_far)
                    print("-------------------------------------")
                    # decision = self.ai(self.mypos, self.state)
                    logger.debug("self.mypos: " + str(self.mypos))
                    decision = self.ai(self.mypos, self.state, self._decision_record)

                    record_logger.info(decision)

                    if not decision.isValid():
                        self.logger.info('$$$ This client made a invalid decision')
                        print(decision, flush=True)
                        decision.fix()
                        print(decision, flush=True)

                    self.logger.info('$$$ This client made a decision at pos {}'.format(self.mypos))
                    self.add_request(dealer_pb2.DealerRequest(user=self.username, giveup=decision.giveup,
                    allin=decision.allin, check=decision.check, raisebet=decision.raisebet,
                    callbet=decision.callbet, amount=decision.amount, pos=self.mypos, type=MessageType_StateUpdate, token=self.key))

            elif res.type == MessageType_StateUpdate:
                # server sending an info to the client to modify the state
                self.print_stateupdate(res)
                self.state.currpos = res.pos
                self._decision_so_far.append(res)
                if res.giveup == 1:
                    self.state.player[self.state.currpos].active = False
                    self.state.playernum -= 1
                elif res.check == 1:
                    pass
                elif res.allin == 1:
                    self.state.moneypot += self.state.player[self.state.currpos].money
                    self.state.player[self.state.currpos].allinbet()
                    if self.state.player[self.state.currpos].bet > self.state.minbet:
                        self.state.last_raised = max(self.state.player[self.state.currpos].bet - self.state.minbet, self.state.last_raised)
                        self.state.minbet = self.state.player[self.state.currpos].bet
                elif res.callbet == 1:
                    delta = self.state.minbet - self.state.player[self.state.currpos].bet
                    self.state.player[self.state.currpos].raisebet(delta)
                    self.state.moneypot += delta

                elif res.raisebet == 1:
                    self.state.last_raised = max(res.amount - self.state.minbet, self.state.last_raised)
                    self.state.minbet = res.amount
                    delta = res.amount - self.state.player[self.state.currpos].bet
                    self.state.player[self.state.currpos].raisebet(delta)
                    self.state.moneypot += delta

                else:
                    self.logger.info('impossible condition')
                    # assert(0)


                #**************************Modify here if you want to print some other message to read*******************
                # This information of this player's action is stored in variable 'res'.
                # The information of the game is stored in the variable 'self.state'.
                #*********************************************************************************************************

                self.step += 1

            elif res.type == MessageType_IllegalDecision:
                self.logger.info('player at pos {} illegalMove and is forced to give up. actionNum {}'.format(res.pos, res.actionNum));
                self.state.player[self.state.currpos].active = False
                self.state.playernum -= 1

            elif res.type == MessageType_StateControl:
                # server send a state control command
                if res.command == 'restore':
                    self.round += 1
                    if res.pos == 1:
                        self.state.restore(res.pos, self.button, self.bigBlind)
                    else:
                        self.state.restore(res.pos, self.button, 0)
                elif res.command == 'update':
                    self.state.update(self.totalPlayer)
                elif res.command == 'givecard':
                    self.state.player[res.pos].cards.append(res.num)
                elif res.command == 'sharedcard':
                    self.state.sharedcards.append(res.num)
                elif res.command == 'setUserMoney':
                    self.state.set_user_money(res.userMoney)
                elif res.command == 'competitionEnd':
                    self.logger.info('The competition finished.')
                    return

            elif res.type == MessageType_ClientInit:
                # for money in res.userMoney:
                #     print("Money {} is ".format(money))
                self.client_reset(self.username, self.ai, self.logger, self.mypos)
                # client initialize
                assert(self.step == -1)
                s = res.command.split()
                self.initMoney = int(s[0])
                self.bigBlind = int(s[1])
                self.totalPlayer = int(s[2])
                self.button = int(s[3])
                self.key = res.token
                if self.initMoney == -2:
                    self.logger.info('Bad key for this username.')
                    exit()
                if self.initMoney == -4:
                    self.logger.info('Has no money left.')
                    exit()
                if self.initMoney == -3:
                    self.logger.info('Wait for next game begin.')
                    continue


                key_file = self.username + '_key.txt'
                if not os.path.exists(key_file):
                    with open(key_file, 'w') as f:
                        f.write(self.key)

                self.mypos = res.pos
                self.logger.info('This ai is begin at the pos {}'.format(self.mypos))

                ### If the player in current position already connected to the game,
                # then the game server will return msg in which button is -1
                # If the player join the game failed, then the thread exit.
                if self.button == -1:
                    self.logger.info('Game already started. wait for next game.')
                    # self.stoped = True
                    continue
                self.logger.info(res.extra)
                self.step = 0
                self.state = State(self.logger, self.totalPlayer, self.initMoney, self.bigBlind, self.button)
                self.state.last_raised = self.bigBlind

               # self.initialized = True

                self.logger.info('******client initialized****** client:%d step:%d'%(self.mypos, self.step))

            elif res.type == MessageType_GameOver:
                # game over info
                self.logger.info('***********game over***************')
                self.logger.info('sharedcards:%s' % str(self.state.sharedcards))
                for x in self.state.sharedcards:
                    self.logger.info('%s. ' % decode_card(x))
                self.logger.info('cards:%s' % str(self.state.player[self.mypos].cards))
                for x in self.state.player[self.mypos].cards:
                    self.logger.info('%s. ' % decode_card(x))
                self.logger.info('\n')
                self.logger.info('Have money {} left'.format(res.userMoney[self.mypos]))

                self.stoped = True
                # # save decision record
                # record_path = "records"
                # if not os.path.exists(record_path):
                #     os.makedirs(record_path)
                # with open(os.path.join(record_path, 'decision_record.pickle'), 'wb') as f:
                #     # Pickle the 'data' dictionary using the highest protocol available.
                #     pickle.dump(self._decision_record, f, pickle.HIGHEST_PROTOCOL)

                # self.client_reset(self.username, self.ai, self.logger, self.mypos)
                if ISTESTING:
                    return

    def add_request(self, msg):
        self.cond.acquire()
        self._new_request.append(msg)
        self.cond.notify()
        self.cond.release()

    def HeartBeat(self):
        # a empty message, only to find if there is new info from the server
        self.heartbeaklock.acquire()

        while not self.allowheartbeat:
            self.heartbeaklock.release()
            time.sleep(1)
            self.heartbeatlock.acquire()

        self.heartbeaklock.release()

        return dealer_pb2.DealerRequest(user=self.username, command='heartbeat', type=0, pos=self.mypos,
                                        token=self.key, status=self.step)

def decode_card(num):
    name = ['spade', 'heart', 'diamond', 'club']
    value = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    return '%s, %s' %(name[num%4], value[num//4])

def run_func(thread):
    thread.run()

def background_thread_run(thread):
    t = threading.Thread(target=run_func, args=(thread,))
    t.setDaemon(True)
    t.start()


def client_start(thread):
    background_thread_run(thread)
    thread.start()


class ClientJob(object):
    def __init__(self, c):
        self.client = c

    def run(self):
        # print('run for client:%d'%(self.client.mypos))
        client_start(self.client)


#**********************************NOTICE**************************************
# You should make sure that your username is unique and can only contain letters, numbers and '_'.
# You should never keep more than one connection to the server at the same time.
#******************************************************************************


if __name__ == '__main__':
# ************************************ modify here to use your own username! ***********************

    if len(sys.argv) == 1:
        print('Error: enter the name for the client!')
#    username = sys.argv[1]
#     username = "02David"
    username = glob.glob('*David_key.txt')[0][:-8]

    from lib.simple_logger import file_logger
    fileName = 'action_logger.log'
    logger = file_logger(fileName)
# ****************************************************************************************************


# ************************************ modify here to use your own RLAI! ********************************

    c = Client(username, ai, logger)
    ClientJob(c).run()

# ****************************************************************************************************
