import random
import pickle
import os
import sys


class Markov:
    CLAUSE_ENDS = [',', '.', ';', ':']

    def __init__(self, n=3):
        self.n = n
        self.p = 0
        self.seed = None
        self.data = {}
        self.recentData = {}
        self.cln = n
        self.manual = False

    def set_cln(self, cln):
        self.cln = cln if cln is not None and cln <= self.n else self.n

    def train(self, training_data):
        prev = ()
        for token in training_data:
            token = sys.intern(token)
            for pprev in [prev[i:] for i in range(len(prev) + 1)]:
                if not pprev in self.data:
                    self.data[pprev] = [0, {}]

                if not token in self.data[pprev][1]:
                    self.data[pprev][1][token] = 0

                self.data[pprev][1][token] += 1
                self.data[pprev][0] += 1

            prev += (token,)
            if len(prev) > self.n:
                prev = prev[1:]

    def load(self, filename):
        with open(os.path.expanduser(filename), "rb") as f:
            try:
                n, self.data = pickle.load(f)

                if self.n > n:
                    print("warning: changing n value to", n)
                    self.n = n
                return True
            except:
                print("Loading data file failed!")
                return False

    def dump(self, filename):
        try:
            with open(os.path.expanduser(filename), "wb") as f:
                pickle.dump((self.n, self.data), f)
            return True
        except:
            print("Could not dump to file.")
            return False

    def reset(self, seed, prob, prev, cln, manual):
        self.seed = seed
        self.p = prob
        self.prev = prev
        self.set_cln(cln)
        self.cleanRecentData()
        self.manual = manual
        random.seed(seed)

    def setManual(self, manual=False):
        self.manual = manual

    def __iter__(self):
        return self

    def __next__(self):
        if self.prev == () or random.random() < self.p:
            next = self._selectToken(())
        else:
            try:
                next = self._selectToken(self.prev)
            except:
                self.prev = ()
                next = self._selectToken(self.prev)

        self.prev += (next,)
        if len(self.prev) > self.n:
            self.prev = self.prev[1:]

        if next[-1] in self.CLAUSE_ENDS:
            self.prev = self.prev[-self.cln:]

        return next

    def lastStateSaturated(self):
        if self.prev not in self.recentData:
            return False
        return self.recentData[self.prev] > self.data[self.prev][0]

    def cleanRecentData(self):
        self.recentData = {}

    def manualChoice(self, max):
        while True:
            choice = input("Enter your choice: ").strip()
            try:
                choice = int(choice)
            except:
                print("Not an integer number, try again")
                continue
            if choice < 0 or choice > max:
                print("Number out of range, please, use numbers in range"
                      "[0-{0}]".format(max))
                continue
            break
        return choice-1

    def _selectToken(self, state=None):
        if state is None:
            state = self.prev
        if not state in self.recentData:
            self.recentData[state] = 0
        self.recentData[state] += 1
        if self.manual:
            choice = 0
            while True:
                choices = []
                for i in range(50):
                    choices.append(self._choose(self.data[state]))
                choices = list(set(choices))
                print("0: <Generate choices again>")
                for i in range(len(choices)):
                    print("{0}: {1}".format(i+1, choices[i]))
                choice = self.manualChoice(len(choices))
                if choice >= 0:
                    break
            return choices[choice]

        else:
            return self._choose(self.data[state])

    def _choose(self, freqdict):
        total, choices = freqdict
        idx = random.randrange(total)

        for token, freq in choices.items():
            if idx <= freq:
                return token

            idx -= freq
