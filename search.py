#! python3
import math
import os
from math import sqrt
from typing import List

import pandas as pd

NUM_BOTS = 20
STEP_SIZE = .01
PRIOR_WEIGHTS = []


class Measure:
    """
    Holds the measurement for a single instance
    """
    speed: float
    momentum: float
    variance: float
    scatter: float
    rotation: float

    def __init__(self, speed, momentum, variance, scatter, rotation, dist_dev, dist_dev1, dist_dev2):
        self.speed = float(speed)
        self.momentum = float(momentum)
        self.variance = float(variance)
        self.scatter = float(scatter)
        self.rotation = float(rotation)
        self.dist_dev = float(dist_dev)
        self.dist_dev1 = float(dist_dev1)
        self.dist_dev2 = float(dist_dev2)

    def __repr__(self):
        return f"<{self.speed}, {self.momentum}, {self.variance}, {self.variance}, {self.scatter}, {self.rotation}>"

    def distance(self, other: "Measure") -> float:
        return sqrt((self.speed - other.speed) ** 2 +
                    (self.momentum - other.momentum) ** 2 +
                    (self.variance - other.variance) ** 2 +
                    (self.scatter - other.scatter) ** 2 +
                    (self.rotation - other.rotation) ** 2)


class Observation:
    """
    Holds the list of measurements for some trial
    """
    weights: List[float]
    measures: List["Measure"]

    def __init__(self, weights):
        self.weights = [round(w, 2) for w in weights]
        self.measures = []
        self.has_run = False

    def __repr__(self):
        return f"Obs <{self.weights}>"

    def write_template(self, template_filename="controller_template.bzz",
                       output_filename="controller.bzz"):
        with open(template_filename) as template:
            replaced = template.read()\
                .replace("{W0L}", str(self.weights[0]))\
                .replace("{W0R}", str(self.weights[1]))\
                .replace("{W1L}", str(self.weights[2]))\
                .replace("{W1R}", str(self.weights[3]))
            if (len(self.weights) > 4):
                replaced = replaced\
                    .replace("{WBL}", str(self.weights[4]))\
                    .replace("{WBR}", str(self.weights[5]))
            with open(output_filename, 'w') as outfile:
                outfile.write(replaced)

        pass

    def getMeasures(self) -> List["Measure"]:
        """
        if the measures haven't been calculated, calculate them
        else, return the measures
        """
        if (len(self.measures) == 0):
            return self.calcMeasures()
        else:
            return self.measures

    def run(self):
        """
        Run the simulation by creating the template file and executing it.
        """
        self.write_template()
        inc = "BUZZ_INCLUDE_PATH=/usr/local/share/buzz QT_QPA_PLATFORM=xcb"
        os.system(f"{inc} bzzc controller.bzz")
        os.system(f"{inc} argos3 -c layout.argos > /dev/null")
        self.has_run = True
        self.calcMeasures()

    def calcMeasures(self) -> List["Measure"]:
        """
        Run argos, and then read the corresponding csv
        """
        if (not self.has_run):
            self.run()
            self.measures = clean_data("test.csv")
            # os.system(f"cp test.csv 'Data/{self.weights}.csv'")
        return self.measures

    def permute(self, permute_number=4) -> List["Observation"]:
        """
        Rather than calculate all the permutaitons, just calculate up and down for each value
        """
        new_obs = []
        for idx, weight in enumerate(self.weights):
            larger = weight + STEP_SIZE
            smaller = weight - STEP_SIZE
            larger_w = self.weights[:idx] + [larger] + self.weights[idx + 1:]
            smaller_w = self.weights[:idx] + [smaller] + self.weights[idx + 1:]
            new_obs.append(Observation(larger_w))
            new_obs.append(Observation(smaller_w))
        return new_obs


    def permute_real(self, permute_number=4) -> List["Observation"]:
        """
        permute number controls how many weights to permute. 
        By default, we don't permute the the last 2 weights (the bias terms)
        return a step in each direction from the given population
        """
        obs = []

        perm_weights = []
        for weight in self.weights[:permute_number]:
            perm_weights.append(
                [weight - STEP_SIZE, weight + STEP_SIZE, weight])

        permuted = Observation.permuteHelper(perm_weights)
        obs = list(map(
            lambda weights: Observation(weights),
            filter(lambda permutation: permutation != self.weights, permuted)))

        obs = list(
            filter(lambda a_obs:
                   all(map(lambda val: val >= 0 and val <= 1, a_obs.weights)),
                   obs))

        return obs

    def segregation(self) -> float:
        """
        Get the segregation for this given measure
        Defined as: std deviation of group distance / total devation of distance
        """
        last: "Measure" = self.measures[-1]
        return 1 / ((last.dist_dev1 / last.dist_dev + last.dist_dev2 / last.dist_dev) / 2)

    @staticmethod
    def permuteHelper(permuted_weights: List[List[float]]):
        """
        takes in each indiviudal weight, permuted as [weight + step, weight - step, weight],
        returns all permutations of these elements (all step directions).
        Note: results  in 3^N combinations (729 for 6 weights)
        """
        if (len(permuted_weights) == 1):
            return [[i] for i in permuted_weights[0]]
        else:
            permuted = []
            current = permuted_weights[0]
            rest = permuted_weights[1:]
            permuted_rest = Observation.permuteHelper(rest)
            for p in current:
                for permutation in permuted_rest:
                    permuted.append([p] + permutation)
            return permuted

    def distance(self, other: "Observation") -> float:
        """
        *from the paper*: To create our final behavior vector, we used a sliding window average of
            each feature over the last 100 time steps. 

        I assume this is what they mean.
        """
        steps = 100
        measures = self.measures[:min(steps, len(self.measures))]
        other_measures = other.measures[:min(steps, len(self.measures))]
        dist = 0
        for m1, m2 in zip(measures, other_measures):
            dist += m1.distance(m2)
        dist /= steps
        return 0

def fitness(population: Observation, archive: List["Observation"], k=15) -> float:
    return population.segregation()

def novelty(population: Observation, archive: List["Observation"], k=15) -> float:
    """
    novelty = 1 / k * Sum i = 0..k (dist(b, Bi))

    returns:
        float representing novelty, taken as the average novelty to the 15 closest observations
    """
    dists = [d for d in map(lambda obs: obs.distance(population), archive)]
    dists.sort()
    nov = sum(dists) / max(1, len(dists))
    return nov


def shouldAddToArchive(population: List["Observation"],
                       features: "Observation",
                       archive: List["Observation"]):
    """
    Note: really we always want to archive according to the paper
    """
    return True


def updatePopulation(population: List["Observation"],
                     archive: List["Observation"],
                     N=3) -> List["Observation"]:
    """
    Given the population, permute the top N most unique observation,
    sorted by novelty.
    Remove the old types measurements
    """
    N = min(len(population), N)

    novelty_pairs = [(p, fitness(p, archive))
                     for p in population]

    # novelty_pairs = [(p, novelty(p, archive))
                     # for p in population]
    # highest novelty (most novel) first
    novelty_pairs = sorted(
        novelty_pairs, key=lambda pair: pair[1], reverse=True)

    # permute top N population,
    # this is a list of lists (permutations for each pop)
    new_pop = map(
        lambda pop: pop.permute(),
        (map(lambda pair: pair[0], novelty_pairs[:N]))
    )

    # flatten
    new_pop = [pop for permutations in new_pop for pop in permutations]
    new_pop = list(
        filter(lambda obs: not obs.weights in PRIOR_WEIGHTS, new_pop))

    return new_pop


def most_segregated(archive: List["Observation"]):
    """
    TODO: Given the archive, find the most segregated observation. 
    """
    sorted_seg = sorted(
        archive, key=lambda obs: obs.segregation(), reverse=True)
    for i in range(100):
        print(
            f"segregation for: {sorted_seg[i]} is {sorted_seg[i].segregation()}")
    return sorted_seg[0]


def search():
    print("iteration, population, weights, segregation")
    # seed = Observation([.1, .2, .3, .4, .5, .6])
    seed = Observation([0.5, 0.5, 0.5, .5, .5, .5])
    population = [seed]
    archive = []
    stop = False
    it = 0
    max_it = 100
    real_max_it = 100
    while(not stop):
        it = real_max_it - max_it
        it += 1
        max_pop = -1
        for idx, p in enumerate(population):
            _features = p.getMeasures()
            global PRIOR_WEIGHTS
            # It is important to keep track of the prior measurements to cut down on permutations...
            PRIOR_WEIGHTS.append(p.weights)
            if (shouldAddToArchive(p, p, archive)):
                archive.append(p)
            seg = p.segregation()
            print(f"{it}, {idx}, {p.weights}, {seg}")

            max_pop -= 1
            if (max_pop == 0):
                break

        population = updatePopulation(population, archive)
        # TODO remove
        max_it -= 1
        if (max_it == 0):
            break

    seg = most_segregated(archive)
    print("most segregated\n", seg)


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


def clean_data(filename, last_n=100):
    """
    reads the given raw data file and returns a list of measurements (measurement class defined above)
    Only takes that last 100 time steps
    """
    df: pd.DataFrame = pd.read_csv(filename).tail(last_n * NUM_BOTS)
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

        dist_dev = iteration["x"].apply(lambda x: length(sub_pos(x, m))).std()
        m1 = (group1["px"].mean(), iteration["py"].mean())
        dist_dev1 = group1["x"].apply(lambda x: length(sub_pos(x, m1))).std()
        m2 = (group2["px"].mean(), iteration["py"].mean())
        dist_dev2 = group2["x"].apply(lambda x: length(sub_pos(x, m2))).std()

        cleaned.append(Measure(avg_spd, ang_momentum,
                               radial_var, scatter, group_rotation,
                               dist_dev, dist_dev1, dist_dev2))

    return cleaned[max(0, len(cleaned) - 100):]

    # scatter = (group["x"].apply(lambda pos: length(sub_pos(pos, m)))).mean() / R**2


if __name__ == "__main__":
    os.system("cd ./Logger/ && sh build.sh")
    # search()
    obs = Observation([.3, .3, .3, .3, .3, .3])
    # obs = Observation([.61, .59, .01, .3, .01, .3])
    # obs = Observation([0.1, 0.09, 0.53, 0.49, 0.49, 0.5])
    # obs = Observation([0.56, 0.46, 0.21, 0.31, 0.21, 0.31])
    obs.run()
    # obs.permute()
    # obs.measures = clean_data("test.csv")
    # obs.getMeasures()
    # print("segregation is ", obs.segregation())
    # print(obs.permute())
    # print(obs.getMeasures()[-1])
    # print(len(obs.permute()))
    # print(len(obs.permute()))
    # obs.write_template()
    # print(obs.permute())
    # perm = Observation.permuteHelper([[.1, .3, .2], [.6, .8, .7]])
    # print(perm)
