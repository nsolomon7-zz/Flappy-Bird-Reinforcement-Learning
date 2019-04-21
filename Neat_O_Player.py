import math, random, copy, os
from scipy.stats import logistic

num_per_gen = 30
elitism = 0.2
random_behavior = 0.2
mutation_rate = 0.1
mutation_range = 0.5
historic = 0
low_historic = False
score_sort = -1
num_child = 1
network_layers = [5, [], 1]


class Neat_O_Player(object):

    best_ever_file = os.path.join(os.getcwd(), "best_ever.txt")
    best_per_gen_file = os.path.join(os.getcwd(), "best_per_gen.txt")

    def __init__(self):
        try:
            os.remove(self.best_per_gen_file)
        except:
            pass
        self.num_per_gen = num_per_gen
        self.max_gen = 500
        self.cur_gen = 0
        self.cur_bird = None
        self.best_score_ever = -1

        self.generations = Generations()

    def restart(self):
        self.generations = Generations()

    def increment_gen(self):
        self.save_best_score()
        self.cur_gen = self.cur_gen + 1
        self.cur_bird = None

        networks = []
        print("Creating Gen #%d" % self.cur_gen)
        if self.cur_gen == 1:
            networks = self.generations.first_generation()
        else:
            networks = self.generations.next_generation()

        nns = []
        for i in range(len(networks)):
            nn = Network()
            nn.set_save(networks[i])
            nns.append(nn)

        if not historic == -1:
            if len(self.generations.generations) > historic + 1:
                self.generations.generations = self.generations.generations[len(self.generations.generations) - (historic+1):]

        return nns


    def network_score(self, network, score):
        self.generations.add_genome(Genome(score, network.get_save()))

    def make_decision(self, stimuli, nn):
        score = nn.compute(stimuli)
        if score[0] > 0.5:
            return "SPACE"
        return "do nothing"

    def save_best_score(self):
        if len(self.generations.generations) == 0:
            return
        best_score_in_gen = -1
        best_in_gen = None
        for g in self.generations.generations[0].genomes:
            if g.score > best_score_in_gen:
                best_in_gen = g
                best_score_in_gen = g.score

        fhandler = open(self.best_per_gen_file, "a")
        fhandler.writelines("Gen #%d scored %f pts: " % (self.cur_gen, best_in_gen.score) + str(best_in_gen.network) + "\n")
        fhandler.close()

        if best_score_in_gen > self.best_score_ever:
            fhandler = open(self.best_ever_file, "w")
            fhandler.writelines("Gen #%d scored %f pts: " % (self.cur_gen, best_in_gen.score) + str(best_in_gen.network) + "\n")
            fhandler.close()
            self.best_score_ever = best_score_in_gen




class Neuron(object):
    def __init__(self):
        self.value = 0
        self.weights = []

    def populate(self, num):
        self.weights = []
        for i in range(num):
            self.weights.append(random_clamped())

class Layer(object):
    def __init__(self, idx=0):
        self.idx = idx
        self.neurons = []

    def populate(self,num_neurons, num_inputs):
        self.neurons=[]
        for i in range(num_neurons):
             n = Neuron()
             n.populate(num_inputs)
             self.neurons.append(n)


class Network(object):
    def __init__(self):
        self.layers = []

    def perceptron_generation(self,input, hiddens, output):
        index = 0
        prev_neurons = 0
        layer = Layer(index)
        layer.populate(input, prev_neurons)
        prev_neurons = input
        self.layers.append(layer)
        index += 1
        for h in hiddens:
            layer = Layer(index)
            layer.populate(h, prev_neurons)
            prev_neurons = h
            self.layers.append(layer)
            index += 1
        layer = Layer(index)
        layer.populate(output, prev_neurons)
        self.layers.append(layer)

    def get_save(self):
        datas = {"neurons": [], "weights": []}

        for i in range(len(self.layers)):
            datas["neurons"].append(len(self.layers[i].neurons))
            for j in range(len(self.layers[i].neurons)):
                for k in range(len(self.layers[i].neurons[j].weights)):
                    datas["weights"].append(self.layers[i].neurons[j].weights[k])

        return datas

    def set_save(self, save):
        prev_neurons = 0
        index = 0
        index_weights = 0
        self.layers = []
        for i in range(len(save["neurons"])):
            layer = Layer(index)
            layer.populate(save["neurons"][i], prev_neurons)
            for j in range(len(layer.neurons)):
                for k in range(len(layer.neurons[j].weights)):
                    layer.neurons[j].weights[k] = save["weights"][index_weights]
                    index_weights +=1
            prev_neurons = save["neurons"][i]
            index += 1
            self.layers.append(layer)

    def compute(self, inputs):

        for i in range(len(inputs[0])):
            if self.layers[0] and self.layers[0].neurons[i]:
                self.layers[0].neurons[i].value = inputs[0][i]

        prev_layer = self.layers[0]
        for i in range(1, len(self.layers)):
            for j in range(len(self.layers[i].neurons)):
                sum = 0
                for k in range(len(prev_layer.neurons)):
                    sum += prev_layer.neurons[k].value * self.layers[i].neurons[j].weights[k]
                self.layers[i].neurons[j].value = activation(sum)
            prev_layer = self.layers[i]

        out = []
        last_layer = self.layers[-1]
        for i in range(len(last_layer.neurons)):
            out.append(last_layer.neurons[i].value)

        return out

class Genome(object):
    def __init__(self, score=0, network=None):
        self.score = score
        self.network = network


class Generation(object):
    def __init__(self):
        self.genomes = []

    def add_genome(self, genome):
        count = 0
        while count < len(self.genomes):
            if score_sort < 0:
                if genome.score > self.genomes[count].score:
                    break
            else:
                if genome.score < self.genomes[count].score:
                    break
            count += 1

        self.genomes.insert(count, genome)

    def fuck(self, g1, g2, num_children):
        datas = []
        for n in range(num_children):
            data = copy.deepcopy(g1)
            for i in range(len(g2.network["weights"])):
                if random.random() <= 0.5:
                    data.network["weights"][i] = g2.network["weights"][i]

            for i in range(len(data.network["weights"])):
                if random.random() < mutation_rate:
                    data.network["weights"][i] += random.random() * mutation_range * 2 - mutation_range

            datas.append(data)

        return datas

    def generate_next_generation(self):
        nexts = []
        for i in range(round(elitism*num_per_gen)):
            if len(nexts) < num_per_gen:
                nexts.append(copy.deepcopy(self.genomes[i].network))

        for i in range(round(random_behavior*num_per_gen)):
            n = copy.deepcopy(self.genomes[0].network)
            for k in range(len(n["weights"])):
                n["weights"][k] = random_clamped()
            if len(nexts) < num_per_gen:
                nexts.append(n)

        maximum = 0
        percentiles = self.calc_percentiles()
        while True:
            parents = self.select_parents(percentiles)
            children = self.fuck(parents[0], parents[1], num_child)
            for c in children:
                nexts.append(c.network)
                if len(nexts) >= num_per_gen:
                    return nexts

    def calc_percentiles(self):
        tot_score = sum([g.score for g in self.genomes])
        percentiles = []
        tot_percentile = 0
        for g in self.genomes:
            perc = g.score / tot_score
            percentiles.append(perc + tot_percentile)
            tot_percentile += perc
        return percentiles

    def select_parents(self, percentiles):
        p1 = None
        p2 = None
        p1_perc = random.random()
        p2_perc = random.random()
        count = 0
        prev_perc = 0
        for perc in percentiles:
            if p1_perc <= perc and p1_perc > prev_perc:
                p1 = self.genomes[count]
            if p2_perc <= perc and p2_perc > prev_perc:
                p2 = self.genomes[count]
            if p1 and p2:
                return [p1, p2]
            prev_perc = perc
            count += 1




class Generations(object):
    def __init__(self):
        self.generations = []
        self.cur_gen = Generation()

    def first_generation(self):
        out = []
        for i in range(num_per_gen):
            nn = Network()
            nn.perceptron_generation(network_layers[0], network_layers[1], network_layers[2])
            out.append(nn.get_save())

        self.generations.append(Generation())
        return out

    def next_generation(self):
        if len(self.generations) == 0:
            return self.first_generation()

        gen = self.generations[-1].generate_next_generation()
        self.generations.append(Generation())
        return gen

    def add_genome(self, g):
        if len(self.generations) == 0:
            return False
        return self.generations[-1].add_genome(g)




def activation(a):
    return logistic.cdf(a)



def random_clamped():
    return random.random() * 2 - 1
