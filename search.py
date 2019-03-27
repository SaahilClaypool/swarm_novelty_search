#! python3
from typing import List

STEP_SIZE = .01


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


class Observation:
    """
    Holds the list of measurements for some trial
    """
    weights: List[float]
    measures: list

    def __init__(self, weights):
        self.weights = weights
        self.measures = []

    def __repr__(self):
        return f"Obs <{self.weights}>"

    def getMeasures(self):
        """
        if the measures haven't been calculated, calculate them
        else, return the measures
        """
        if (not self.measures):
            return self.calcMeasures()
        else:
            return self.measures

    def calcMeasures(self):
        """
        TODO this should calculate the measures by running argos / reading a csv or something
        """
        return self.measures

    def permute(self) -> List["Observation"]:
        """
        return a step in each direction from the given population
        """
        obs = []
        W0 = [self.weights[0] - STEP_SIZE,
              self.weights[0] + STEP_SIZE, self.weights[0]]
        W1 = [self.weights[1] - STEP_SIZE,
              self.weights[1] + STEP_SIZE, self.weights[1]]
        W2 = [self.weights[2] - STEP_SIZE,
              self.weights[2] + STEP_SIZE, self.weights[2]]

        for w0 in W0:
            for w1 in W1:
                for w2 in W2:
                    if (w0 >= 0 and w0 <= 1 and
                        w1 >= 0 and w1 <= 1 and
                        w2 >= 0 and w2 <= 1 and
                            not (w0 == self.weights[0] and w1 == self.weights[1] and w2 == self.weights[2])):
                        obs.append(Observation([w0, w1, w2]))

        return obs


def novelty(features: List["Measure"], archive: List["Observation"]) -> float:
    """
    TODO: calc novelty
    returns: 
        float representing novelty, where 0 is least novel, 1 is most novel 
        TODO: maybe 1 shouldn't be the highest allowed value?
    """
    return 0


def shouldAddToArchive(population: List["Observation"], features: List["Measure"], archive: List["Observation"]):
    """
    TODO: determine if should archive
    Add the behavior to the archive if it is sufficiently novel
    """
    return True


def updatePopulation(population: List["Observation"], archive: List["Observation"], N=3) -> List["Observation"]:
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

    # permute top N population, this is a list of lists (permutations for each pop)
    new_pop = map(
        lambda pop: pop.permute(),
        (map(lambda pair: pair[0], novelty_pairs[:N]))
    )

    # flatten
    new_pop = [pop for permutations in new_pop for pop in permutations]

    return new_pop


def search():
    seed = Observation([.1, .2, .3])
    population = [seed]
    archive = []
    print(seed)
    stop = False

    while(not stop):
        for p in population:
            features = p.getMeasures()
            nov = novelty(features, archive)
            if (shouldAddToArchive(p, features, archive)):
                archive.append(p)
        population = updatePopulation(population, archive)


if __name__ == "__main__":
    obs = Observation([.1, .2, .3])
    print(obs.permute())
