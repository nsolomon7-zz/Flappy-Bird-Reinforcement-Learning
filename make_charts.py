import matplotlib.pyplot as plt
import os, re
import numpy as np


neat_x = []
with open(os.path.join(os.getcwd(), "best_per_gen_NEAT.txt")) as f:
    lines = f.readlines()
    for l in lines:
        pts = float(re.findall(r"[-+]?\d*\.\d+|\d+", l)[1])
        neat_x.append(pts)
        if pts >= 700:
            break

ne_x = []
with open(os.path.join(os.getcwd(), "best_per_gen_neuroevolution.txt")) as f:
    lines = f.readlines()
    for l in lines:
        pts = float(re.findall(r"[-+]?\d*\.\d+|\d+", l)[1])
        ne_x.append(pts)
        if pts >= 700:
            break
print(ne_x)
print(neat_x)
if len(ne_x) == 1:
    ne_x = ne_x * len(neat_x)
if len(neat_x) == 1:
    neat_x = neat_x * len(ne_x)
ylabels = [str(int(a/62)) for a in range(0, 683, 62)]
yvals = np.arange(0, 12, 1)
print(yvals)
plt.plot(neat_x, 'k')
plt.plot(ne_x, 'b')
plt.title("Comparison with Best Stimuli")
plt.xlabel("Generation")
plt.ylabel("Score")
plt.legend(["NEAT", "Neuroevolution"], loc='best')
plt.show()

