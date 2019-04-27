import pandas as pd
import matplotlib.pyplot as plt
import math

NUM_BOTS = 20
def plot_seg(filename, outfile=""):
    """
    Plot the path for the given item
    """
    ax = plt.axes()

    seg = clean_data(filename)
    seg = list(seg.values)
    seg
    plt.plot(seg)

    if (len(outfile)):
        plt.savefig(outfile)

    plt.show()

def length(v):
    return math.sqrt(dotproduct(v, v))


def sub_pos(p, m):
    return (p[0] - m[0],  p[1] - m[1])


def dotproduct(v1, v2):
    return sum((a*b) for a, b in zip(v1, v2))


def angle(v1, v2):
    return math.acos(dotproduct(v1, v2) / (length(v1) * length(v2)))


def cross(a, b):
    t = angle(a, b)
    return length(a) * length(b) * math.sin(t)
def clean_data(filename, last_n=5000):
    """
    reads the given raw data file and returns a list of measurements (measurement class defined above)
    Only takes that last 100 time steps
    """
    df: pd.DataFrame = pd.read_csv(filename).tail(last_n * NUM_BOTS)
    df = df[df["iteration"] % 10 == 0]
    df = df.groupby("iteration")
    # TODO: find the world size
    R = 2 * 2**.5
    has_prev = False
    prev = False
    cleaned = []
    for name, iteration in df:
        iteration = iteration.reset_index()
        if (not has_prev):
            has_prev = True
            prev = iteration
            continue
        iteration["x"] = list(zip(iteration["px"], iteration["py"]))
        # TODO: this is bad, but might work
        iteration["vx"] = iteration["px"] - prev["px"]
        iteration["vy"] = iteration["px"] - prev["px"]
        iteration["v"] = list(zip(iteration["vx"], iteration["vy"]))

        m = (iteration["px"].mean(), iteration["py"].mean())
        s = (iteration["vx"].mean(), iteration["vy"].mean())

        avg_spd = iteration["v"].apply(length).mean()
        scatter = iteration["x"].apply(lambda p: sub_pos(
            p, m)).apply(length).mean() / R ** 2

        iteration["v_x"] = list(
            zip(iteration["v"], iteration["x"].apply(lambda x: sub_pos(x, m))))
        ang_momentum = iteration["v_x"].apply(
            lambda vx: cross(vx[0], vx[1])).mean() / R

        iteration["v_xd"] = iteration["v_x"].apply(
            lambda vx: (vx[0], vx[1], length(vx[1])))
        group_rotation = iteration["v_xd"].apply(
            lambda vxd: cross(vxd[0], vxd[1]) / vxd[2]).mean()

        mean_dist = iteration["x"].apply(
            lambda p: sub_pos(p, m)).apply(length).mean()
        radial_var = iteration["x"].apply(lambda p: sub_pos(p, m)).apply(
            length).apply(lambda v: (v - mean_dist) ** 2).mean() / R ** 2

        # Add our own measure of segregation:
        # Ratio of the cluster group std dev of distance vs std dev of total
        group1 = iteration[iteration.apply(
            lambda bot: bot["id"] % 2 == 0, axis=1)]
        group2 = iteration[iteration.apply(
            lambda bot: bot["id"] % 2 == 1, axis=1)]

        # dist_dev = iteration["x"].apply(lambda x: length(sub_pos(x, m))).std()
        # m1 = (group1["px"].mean(), iteration["py"].mean())
        # dist_dev1 = group1["x"].apply(lambda x: length(sub_pos(x, m1))).std()
        # m2 = (group2["px"].mean(), iteration["py"].mean())
        # dist_dev2 = group2["x"].apply(lambda x: length(sub_pos(x, m2))).std()
        dist_dev_m = iteration["x"].apply(lambda x: length(sub_pos(x, m))).mean()
        dist_dev = iteration["x"].apply(lambda x: abs(length(sub_pos(x, m)) - dist_dev_m)).sum() / iteration["x"].count()
        m1 = (group1["px"].mean(), iteration["py"].mean())
        dist_dev1_m = group1["x"].apply(lambda x: length(sub_pos(x, m1))).mean()
        dist_dev1 = group1["x"].apply(lambda x: abs(length(sub_pos(x, m1)) - dist_dev1_m)).sum() / group1["x"].count()
        m2 = (group2["px"].mean(), iteration["py"].mean())
        dist_dev2_m = group2["x"].apply(lambda x: length(sub_pos(x, m2))).mean()
        dist_dev2 = group2["x"].apply(lambda x: abs(length(sub_pos(x, m2)) - dist_dev2_m)).sum()/ group2["x"].count()

        cleaned.append([name, avg_spd, ang_momentum,
                        radial_var, scatter, group_rotation,
                        dist_dev, dist_dev1, dist_dev2])

    cleaned = pd.DataFrame(data=cleaned, columns=["iteration", "avg_spd", "ang_momentum", "radial_var", "scatter", "group_rotation", "dist_dev", "dist_dev1", "dist_dev2"])
    # cleaned["segregation"] = cleaned.apply(lambda row: 1 / ((row.dist_dev1 / row.dist_dev + row.dist_dev2 / row.dist_dev) / 2), axis=1)
    cleaned["segregation"] = cleaned.apply(lambda row: - ((row.dist_dev1 / row.dist_dev + row.dist_dev2 / row.dist_dev) / 2), axis=1)
    cleaned.to_csv(filename[:-4]+"_clean.csv")
    return cleaned["segregation"]

def main():
    filename="../Data/61.59.01.3.3.7.csv"
    filename="../Data/61.59.01.3.01.3.csv"
    filename="../test.csv"
    clean_data(filename)
    plot_seg(filename)

if __name__ == '__main__':
    main()

