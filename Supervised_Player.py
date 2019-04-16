from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.neural_network import MLPClassifier
from sklearn import preprocessing
import csv

class Supervised_Player(object):

    def __init__(self, data_file):
        self.scaler = preprocessing.StandardScaler()
        self.clf = self.train_classifier(data_file)
        self.num_per_gen = 5
        self.max_gen = 5
        self.cur_gen = 0

    def increment_gen(self):
        self.cur_gen+=1
    def make_decision(self, stimuli):
        scaled_input = self.scaler.transform(stimuli)
        decision = self.clf.predict(scaled_input)[0]
        try:
            print(self.clf.predict_proba(scaled_input))
        except:
            pass
        print(decision)
        if decision == 1:
            decision = "SPACE"
        else:
            decision = "NO_INPUT"
        return decision

    def read_data_file(self, data_file):
        stimulis = []
        actions = []
        with open(data_file, mode='r') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                if row[0] == "SPACE":
                    row[0] = 1
                else:
                    row[0] = 0
                for i in range(len(row)):
                    row[i] = float(row[i])
                actions.append(row[0])
                stimulis.append(row[1:])
        self.scaler.fit(stimulis)
        stimulis = self.scaler.transform(stimulis)
        return (actions, stimulis)

    def train_classifier(self, data_file):
        clf = KNeighborsClassifier(n_neighbors=5)
        df = self.read_data_file(data_file)
        clf.fit(df[1], df[0])
        return clf