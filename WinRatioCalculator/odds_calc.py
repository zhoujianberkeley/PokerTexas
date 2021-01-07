



# 1 number of player
# 2 balance of each player
#
# 3 current pot
#
# 4 prob to fold/check
#
# 5 pot if call
#   pot if fold
#

class Player():

    def __init__(self, id, balance, initalbet):
        self.id = id
        self.balance = balance
        self.bet = initalbet

    def raise_(self, amount, mininum_raise=0):
        if amount < mininum_raise:
            amount = mininum_raise

        if amount > self.balance:
            self.all_in()
        else:
            self.balance -= amount
            self.bet += amount

    def all_in(self):
        self.bet += self.balance
        self.balance = 0

    def check(self):
        pass

    def fold(self):
        pass

import holdem_calc
class AIPlayer(Player):

    def __init__(self, id, balance, initalbet, hole_cards):
        super().__init__(id, balance, initalbet)
        self.cards = hole_cards
        self.tie, self.win, self.lost = holdem_calc.calculate(None, False, 1000, None, ["8s", "7s", "Qc", "Th"], False)

    def update_odds(self):
        pass

    def strategy(self):
        pass

