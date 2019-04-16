import math, random

class Neat_O_Player(object):

    def __init__(self):
        self.num_per_gen = 20
        self.elitism = 0.2
        self.random_behavior = 0.2
        self.mutation_rate = 0.1
        self.mutation_range = 0.5
        self.historic = 0
        self.low_historic = False
        self.score_sort = -1
        self.num_child = 1
        self.max_gen = 5
        self.cur_gen = 0
        self.cur_bird = None
        self.network = [1, [1], 1]


    def increment_gen(self):
        self.cur_gen+=1
        self.cur_bird = None

    def get_next_bird(self):
        if not self.cur_bird:
            return self.make_first_bird()

    def make_first_bird(self):
        pass

    def make_decision(self, stimuli):
        pass


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
        laayer = Layer(index)
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
        for i in range(len(save.neurons)):
            layer = Layer(index)
            layer.populate(save.neurons[i], prev_neurons)
            for j in range(len(layer.neurons)):
                for k in range(len(layer.neurons[j].weights)):
                    layer.neurons[j].weights[k] = save.weights[index_weights]
                    index_weights +=1
            prev_neurons = save.neurons[i]
            index += 1
            self.layers.append(layer)

    def compute(self, inputs):

        for i in range(len(inputs)):
            if self.layers[0] and self.layers[0].neurons[i]:
                self.layers[0].neurons[i].value = inputs[i]

        prev_layer = self.layers[0]
        for i in range(len(self.layers)):
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



def activation(a):
    ap = (-a) / 1
    return (1 / (1 + math.exp(ap)))


def random_clamped():
    return random.random() * 2 - 1
