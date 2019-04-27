import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("../Results/fitness_search.csv", quotechar="\"")
df["iteration"]
df = df.rename(columns = lambda x: x.strip())

df.columns

its = df.groupby("iteration")
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
    max_seg = 0
    for _idx, val in data.iterrows():
        if (val["segregation"] > max_seg):
            max_seg = val["segregation"]
    x.append(it)
    y.append(max_seg)

plt.scatter(x, y)
plt.show()
