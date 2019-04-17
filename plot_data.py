import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("./test.csv")

# print(df)
print(df["iteration"])

bots = df.groupby("id")

ax = plt.axes()

ax.set_xlim(xmin=-2, xmax=2)
ax.set_ylim(ymin=-2, ymax=2)

its = int(df.shape[0] / 20)

for id, bot in bots:
    x = list(bot["px"])
    y = list(bot["py"])
    o = list(map(lambda i: .75 * i / its, range(its)))
    c = "blue"
    if (id % 2 == 1):
        c = "green"
    ax.scatter(x, y, color=c, alpha=.05)

plt.show()
