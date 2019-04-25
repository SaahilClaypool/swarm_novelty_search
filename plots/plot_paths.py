import pandas as pd
import matplotlib.pyplot as plt


def plot_path(filename, outfile="", gran=20):
    """
    Plot the path for the given item
    """
    df = pd.read_csv(filename)
    df = df[df["iteration"] % gran == 0]
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
        size = [2400 * (i)**2 / its ** 2 for i in range(its)]
        ax.scatter(x, y, color=c, s=size, alpha=.2)

    if (len(outfile)):
        plt.savefig(outfile)

    plt.show()

def main():
    filename="../Data/61.59.01.3.3.7.csv"
    filename="../test.csv"
    plot_path(filename)

if __name__ == '__main__':
    main()
