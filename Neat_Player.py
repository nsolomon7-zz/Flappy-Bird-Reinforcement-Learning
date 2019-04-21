import math, random, copy, os
from scipy.stats import logistic
import numpy as np

num_per_gen = 50
elitism = 0.2
random_behavior = 0.2
mutation_rate = 0.1
mutation_range = 0.5
historic = 0
low_historic = False
score_sort = -1
num_child = 1
network_layers = [2, [1], 1]


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

class ConnectionGene(object):

    def __init__(self, fr, to, w, inno):
        self.from_node = fr
        self.to_node = to
        self.weight = w
        self.enabled = True
        self.inno_num = inno

    def mutate_weight(self):
        r = random.random()
        if r < 0.1:
            self.weight = random.randrange(-1, 1, .001)
        else:
            self.weight += random.normalvariate(0, 0.1)
            if self.weight > 1:
                self.weight = 1
            elif self.weight < -1:
                self.weight = -1

    def clone(self, fr, to):
        clone = ConnectionGene(fr, to, self.weight, self.inno_num)
        clone.enabled = self.enabled
        return clone

class ConnectionHistory(object):

    def __init__(self, fr, to, inno, inno_nums):
        self.from_node = fr
        self.to_node = to
        self.inno_num = inno
        self.inno_numbers = copy.deepcopy(inno_nums)

    def matches(self, g, fr, to):
        if len(g.genes) == len(self.inno_numbers):
            if fr.number == self.from_node and to.number == self.to_node:
                for i in range(len(g.genes)):
                    if g.genes[i].inno_num not in self.inno_numbers:
                        return False

                return True
        return False


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
    def __init__(self, inputs, outputs, crossover, score=0, network=None):
        self.score = score
        self.network = network
        self.genes = []
        self.nodes = []
        self.inputs = inputs
        self.outputs = outputs
        self.layers = 2
        self.next_node = 0
        self.network = []

        if crossover:
            return

        for i in range(len(inputs)):
            self.nodes.append(Node(i))
            self.next_node += 1
            self.nodes[i].layer = 0

        self.nodes.append(Node(self.next_node))
        self.bias_node = self.next_node
        self.next_node += 1
        self.nodes[self.bias_node].layer = 0


    def fully_connect(self, innovation_hist):

        for i in range(len(self.inputs)):
            for j in range(len(self.outputs)):
                conn_inno_num = self.get_inno_num(innovation_hist, self.nodes[i], self.nodes[len(self.nodes) - j - 2])
                self.genes.append(ConnectionGene(self.nodes[i], self.nodes[len(self.nodes) - j - 2], random.randrange(-1, 1, .001), conn_inno_num))

        conn_inno_num = self.get_inno_num(innovation_hist, self.nodes[self.bias_node], self.nodes[len(self.nodes) - 2])
        self.genes.append(ConnectionGene(self.nodes[self.bias_node], self.nodes[len(self.nodes) - 2], random.randrange(-1, 1, .001), conn_inno_num))

        self.connect_nodes()


    def get_node(self, node_num):
        for i in range(len(self.nodes)):
            if self.nodes[i].num == node_num:
                return self.nodes[i]

        return None

    def connect_nodes(self):
        for i in range(len(self.nodes)):
            self.nodes[i].output_conns = []

        for i in range(len(self.genes)):
            self.genes[i].from_node.output_conns.append(self.genes[i])

    def feed_forward(self, input_vals):
        for i in range(len(self.inputs)):
            self.nodes[i].output_vals = input_vals[i]

        self.nodes[self.bias_node].output_val = 1

        for i in range(len(self.network)):
            self.network[i].engage()

        outs = []
        for i in range(len(self.outputs)):
            outs[i] = self.nodes[self.inputs + i].output_val

        for i in range(len(self.nodes)):
            self.nodes[i].input_sum = 0

        return outs


    def generate_network(self):
        self.connect_nodes()
        self.network = []

        for l in range(self.layers):
            for i in range(len(self.nodes)):
                if self.nodes[i].layer == l:
                    self.network.append(self.nodes[i])


    def add_node(self, inno_hist):

        if len(self.genes) == 0:
            self.add_connection(inno_hist)
            return

        rand_conn = random.randrange(len(self.genes))

        while self.genes[rand_conn].from_node == self.nodes[self.bias_node] and len(self.genes) != 1:
            rand_conn = random.randrange(len(self.genes))

        self.genes[rand_conn].enabled = False

        new_node_num = self.next_node
        self.nodes.append(Node(new_node_num))
        self.next_node += 1

        conn_inno_num = self.get_inno_num(inno_hist, self.genes[rand_conn].from_node, self.get_node(new_node_num))
        self.genes.append(ConnectionGene(self.genes[rand_conn].from_node, self.get_node(new_node_num), 1, conn_inno_num))

        conn_inno_num = self.get_inno_num(inno_hist, self.get_node(new_node_num), self.genes[rand_conn].to_node)
        self.genes.append(ConnectionGene(self.genes[new_node_num], self.genes[rand_conn].to_node, self.genes[rand_conn].weight, conn_inno_num))

        self.get_node(new_node_num).layer = self.genes[rand_conn].from_node.layer + 1
        conn_inno_num = self.get_inno_num(inno_hist, self.nodes[self.bias_node], self.get_node(new_node_num))
        self.genes.append(ConnectionGene(self.nodes[self.bias_node], self.get_node(new_node_num), 0, conn_inno_num))

        if self.get_node(new_node_num).layer == self.genes[rand_conn].to_node.layer:
            for i in range(len(self.nodes)):
                if self.nodes[i].layer >= self.get_node(new_node_num).layer:
                    self.nodes[i].layer += 1
            self.layers +=1

        self.connect_nodes()

    def add_connection(self, inno_hist):
        if self.fully_connected():
            return

        rn1 = random.randrange(len(self.nodes))
        rn2 = random.randrange(len(self.nodes))

        while self.rand_conns_no_good(rn1, rn2):
            rn1 = random.randrange(len(self.nodes))
            rn2 = random.randrange(len(self.nodes))

        t = None
        if self.nodes[rn1].layer > self.nodes[rn2].layer:
            t = rn2
            rn2 = rn2
            rn1 = t

        conn_inno_num = self.get_inno_num(inno_hist, self.nodes[rn1], self.nodes[rn2])
        self.genes.append(ConnectionGene(self.nodes[rn1], self.nodes[rn2], random.randrange(-1, 1, .001), conn_inno_num))
        self.connect_nodes()

    def rand_conns_no_good(self, rn1, rn2):
        if self.nodes[rn1].layer == self.nodes[rn2].layer:
            return True
        if self.nodes[rn1].is_connected_to(self.nodes[rn2]):
            return True
        return False

    def get_inno_num(self, inno_hist, fr, to):
        is_new = True
        conn_inno_num = 0
        next_conn_num = 0
        for i in range(len(inno_hist)):
            if inno_hist[i].matches(self, fr, to):
                is_new = False
                conn_inno_num = inno_hist[i].inno_num
                break

        if is_new:
            inno_nums = []
            for i in range(len(self.genes)):
                inno_nums.append(self.genes[i].inno_num)

            inno_hist.append(ConnectionHistory(fr.num, to.num, conn_inno_num, inno_nums))
            next_conn_num += 1
            conn_inno_num += 1
        return conn_inno_num

    def fully_connected(self):
        max_conns = 0
        nodes_in_layer = []

        for i in range(self.layers):
            nodes_in_layer[i] = 0

        for i in range(len(self.nodes)):
            nodes_in_layer[self.nodes[i].layer] += 1

        for i in range(self.layers - 1):
            nodes_in_front = 0
            for j in range(i+1, self.layers):
                nodes_in_front += nodes_in_layer[j]

            max_conns += nodes_in_layer[i] * nodes_in_front


        if max_conns <= len(self.genes):
            return True

        return False

    def mutate(self, inno_hist):
        if len(self.genes) == 0:
            self.add_connection(inno_hist)

        r1 = random.random()

        if r1 < 0.8:
            for i in range(len(self.genes)):
                self.genes[i].mutate_weight()


        r2 = random.random()
        if r2 < 0.05:
            self.add_node(inno_hist)

    def crossover(self, p2):
        child = Genome(self.inputs, self.outputs, True)
        child.genes = []
        child.nodes = []
        child.layers = self.layers
        child.next_node = self.next_node
        child.bias_node = self.bias_node
        child_genes = []
        is_enabled = []
        for i in range(len(self.genes)):
            set_enabled = True
            p2_gene = self.matching_gene(p2, self.genes[i].inno_num)
            if p2_gene != -1:
                if not self.genes[i].enabled or not p2.genes[p2_gene].enabled:
                    if random.random() < 0.75:
                        set_enabled = False

                r = random.random()
                if r < 0.5:
                    child_genes.append(self.genes[i])
                else:
                    child_genes.append(p2.genes[p2_gene])
            else:
                child_genes.append(self.genes[i])
                set_enabled = self.genes[i].enabled
            is_enabled.append(set_enabled)

        for i in range(len(self.nodes)):
            child.nodes.append(self.nodes[i].clone())

        for i in range(len(child_genes)):
            child.genes.append(child_genes[i].clone(child.get_node(child_genes[i].from_node.num), child.get_node(child_genes[i].to_node.num)))
            child.genes[i].enabled = is_enabled[i]

        child.connect_nodes()
        return child

    def matching_gene(self, p2, inno_num):
        for i in range(len(p2.genes)):
            if p2.genes[i].inno_num == inno_num:
                return i

        return -1

    def clone(self):
        clone = Genome(self.inputs, self.outputs, True)
        for i in range(len(self.nodes)):
            clone.nodes.append(self.nodes[i].clone())

        for i in range(len(self.genes)):
            clone.genes.append(self.genes[i].clone(clone.get_node(self.genes[i].from_node.num), clone.get_node(self.genes[i].to_node.num)))

        clone.layers = self.layers
        clone.next_node = self.next_node
        clone.bias_node = self.bias_node
        clone.connect_nodes()
        return clone


class Node(object):

    def __init__(self, no):
        self.num = no
        self.input_sum = 0
        self.output_val = 0
        self.output
def activation(a):
    return logistic.cdf(a)

def random_clamped():
    return random.random() * 2 - 1
