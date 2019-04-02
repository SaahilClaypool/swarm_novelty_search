#! python3
from typing import List

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
        self.speed = speed
        self.momentum = momentum
        self.variance = variance
        self.scatter = scatter
        self.rotation = rotation

    def __repr__(self):
        return f"<{self.speed}, {self.momentum}, {self.variance}, {self.variance}, {self.scatter}, {self.rotation}>"

class Observation:
    """
    Holds the list of measurements for some trial
    """
    weights: List[float]
    measures: List["Measure"]

    def __init__(self, weights):
        self.weights = weights
        self.measures = []

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
        if (len(self.measures) ==  0) :
            return self.calcMeasures()
        else:
            return self.measures

    def calcMeasures(self) -> List["Measure"]:
        """
        TODO this should calculate the measures by
        running argos / reading a csv or something
        """
        filename = "data.csv"
        measures = []
        with open(filename, 'r') as datafile:
            import csv
            dreader = csv.DictReader(datafile)
            for row in dreader:
                measures.append(Measure(**row))
        self.measures = measures
        return self.measures

    def permute(self) -> List["Observation"]:
        """
        return a step in each direction from the given population
        """
        obs = []

        perm_weights = []
        for weight in self.weights:
            perm_weights.append([weight - STEP_SIZE, weight + STEP_SIZE, weight])

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


def novelty(features: List["Measure"], archive: List["Observation"]) -> float:
    """
    TODO: calc novelty

    novelty = 1 / k * Sum i = 0..k (dist(b, Bi))

    returns:
        float representing novelty, where 0 is least novel, 1 is most novel
        TODO: maybe 1 shouldn't be the highest allowed value?

    """
    return 0


def shouldAddToArchive(population: List["Observation"],
                       features: List["Measure"],
                       archive: List["Observation"]):
    """
    TODO: determine if should archive
    Add the behavior to the archive if it is sufficiently novel
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

    novelty_pairs = [(p, novelty(p.getMeasures(), archive))
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
    new_pop = list(filter(lambda obs: not obs.weights in PRIOR_WEIGHTS, new_pop))

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
            features = p.getMeasures()
            global PRIOR_WEIGHTS
            # It is important to keep track of the prior measurements to cut down on permutations...
            PRIOR_WEIGHTS.append(p.weights)
            nov = novelty(features, archive)
            if (shouldAddToArchive(p, features, archive)):
                archive.append(p)
        population = updatePopulation(population, archive)
        # TODO remove
        max_it -= 1
        if (max_it <= 0):
            break


if __name__ == "__main__":
    search()
    # obs = Observation([.1, .2, .3, .4, .5, .6])
    # print(len(obs.permute()))
    # obs.write_template()
    # print(obs.permute())
    # perm = Observation.permuteHelper([[.1, .3, .2], [.6, .8, .7]])
    # print(perm)

