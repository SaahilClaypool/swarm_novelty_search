#! python3
from typing import List
from math import sqrt
import os
import pandas as pd
import math

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

    def __init__(self, speed, momentum, variance, scatter, rotation):
        self.speed = float(speed)
        self.momentum = float(momentum)
        self.variance = float(variance)
        self.scatter = float(scatter)
        self.rotation = float(rotation)

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
        self.weights = weights
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
                .replace("{W1R}", str(self.weights[3]))\
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
        inc = "BUZZ_INCLUDE_PATH=/usr/local/share/buzz"
        os.system(f"{inc} bzzc controller.bzz")
        os.system(f"{inc} argos3 -c layout.argos")
        self.has_run = True

    def calcMeasures(self) -> List["Measure"]:
        """
        Run argos, and then read the corresponding csv
        """
        if (not self.has_run):
            self.run()
        self.measures = clean_data("test.csv")
        return self.measures

    def permute(self) -> List["Observation"]:
        """
        return a step in each direction from the given population
        """
        obs = []

        perm_weights = []
        for weight in self.weights:
            perm_weights.append(
                [weight - STEP_SIZE, weight + STEP_SIZE, weight])

        permuted = Observation.permuteHelper(perm_weights)
        obs = list(map(
            lambda weights: Observation(weights),
            filter(lambda permutation: permutation != self.weights, permuted)))

        return obs

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

    novelty_pairs = [(p, novelty(p, archive))
                     for p in population]
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


def search():
    seed = Observation([.1, .2, .3, .4, .5, .6])
    population = [seed]
    archive = []
    print(seed)
    stop = False
    max_it = 5
    while(not stop):
        print(len(population))
        for p in population:
            _features = p.getMeasures()
            global PRIOR_WEIGHTS
            # It is important to keep track of the prior measurements to cut down on permutations...
            PRIOR_WEIGHTS.append(p.weights)
            if (shouldAddToArchive(p, p, archive)):
                archive.append(p)
        population = updatePopulation(population, archive)
        # TODO remove
        max_it -= 1
        if (max_it <= 0):
            break

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

def clean_data(filename):
    """
    reads the given raw data file and returns a list of measurements (measurement class defined above)
    Only takes that last 100 time steps
    """
    df: pd.DataFrame  = pd.read_csv(filename)
    df = df.groupby("iteration")
    # TODO: find the world size
    R = 1
    has_prev = False
    prev = False
    cleaned = []
    for name, group in df:
        group = group.reset_index()
        if (not has_prev):
            has_prev = True
            prev = group
            continue
        group["x"] = list(zip(group["px"], group["py"]))
        # TODO: this is bad, but might work
        group["vx"] = group["px"] - prev["px"]
        group["vy"] = group["px"] - prev["px"]
        group["v"] = list(zip(group["vx"], group["vy"]))

        m = (group["px"].mean(), group["py"].mean())
        s = (group["vx"].mean(), group["vy"].mean())

        avg_spd = group["v"].apply(length).mean()
        scatter = group["x"].apply(lambda p: sub_pos(p, m)).apply(length).mean() / R **2

        group["v_x"] = list(zip(group["v"], group["x"].apply(lambda x : sub_pos(x, m))))
        ang_momentum = group["v_x"].apply(lambda vx: cross(vx[0], vx[1])).mean()

        group["v_xd"] = group["v_x"].apply(lambda vx: (vx[0], vx[1], length(vx[1])))
        group_rotation = group["v_xd"].apply(lambda vxd: cross(vxd[0], vxd[1]) / vxd[2]).mean()

        mean_dist  = group["x"].apply(lambda p: sub_pos(p, m)).apply(length).mean()
        radial_var  = group["x"].apply(lambda p: sub_pos(p, m)).apply(length).apply(lambda v: (v - mean_dist) ** 2).mean()
        cleaned.append(Measure(avg_spd, ang_momentum, radial_var, scatter, group_rotation))

    return cleaned[max(0, len(cleaned) - 100):]

        # scatter = (group["x"].apply(lambda pos: length(sub_pos(pos, m)))).mean() / R**2
        


if __name__ == "__main__":
    # cleaned = clean_data("test.csv")
    os.system("cd ./Logger/ && sh build.sh")
    # search()
    obs = Observation([.01,.01, .1, .3, 0.00, .4])
    obs.run()
    print(obs.getMeasures())
    # print(len(obs.permute()))
    # obs.write_template()
    # print(obs.permute())
    # perm = Observation.permuteHelper([[.1, .3, .2], [.6, .8, .7]])
    # print(perm)

