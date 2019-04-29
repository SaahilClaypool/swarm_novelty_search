import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../Results/fitness_search.csv", quotechar="\"")
df["iteration"]
df = df.rename(columns = lambda x: x.strip())

df.columns

its = df.groupby("iteration")
df["segregation"] = df["segregation"].apply(lambda x : 1 / (-x))
print(df["iteration"])

x = []
y = []
for it, data in its:
    for _idx, val in data.iterrows():
        x.append(it)
        y.append(val["segregation"])

plt.scatter(x, y)
plt.show()

x = []
y = []
for it, data in its:
    max_seg = -100
    max_seg_it = 0
    for _idx, val in data.iterrows():
        if (val["segregation"] > max_seg):
            max_seg = val["segregation"]
            max_seg_it = val
    print(max_seg_it)
    x.append(it)
    y.append(max_seg)

plt.scatter(x, y)
plt.xlabel("Generation")
plt.ylabel("Segregation Score")
plt.savefig("/home/saahil/Documents/swarm_intelligence/swarm_novelty_search/Paper/imgs/fitness_search.png")
plt.show()
