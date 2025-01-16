from typing import Tuple

import random

import numpy as np
from pygame import Vector2

from ..gameobjects.bird import Bird
from .neural_network import NeuralNetwork


class Population:
    """Class representing the population."""

    def __init__(self, size: int, layers: Tuple[int], mutation_rate: float):
        """Initialize class with birds and networks.

        :param layers: tuple or list of the number of layers for each layer of the networks.
        :param mutation_rate: the probability of having a random weight in the network.
        """
        self.pop = [NeuralNetwork(layers) for _ in range(size)]
        self.birds = [Bird() for _ in range(size)]
        self.size = size
        self.generation = 0
        self.mutation_rate = mutation_rate
        self.greatest_net = self.pop[0]

    def __iter__(self):
        """Used to iterate over this class."""
        yield from zip(self.pop, self.birds)

    def predict(self, inputs: np.ndarray):
        """Predict the output of every member of the population, and move birds.

        :param inputs: neural network inputs, defined in 'mainloop.Simulation.get_bird_state'.
        """
        for i, (net, bird) in enumerate(self):
            if net.predict(inputs[i]) > 0.5 and bird.alive:
                bird.jump()

    def calculate_fitness(self, target: Vector2):
        """Calculate the fitness of every element of the population.
        Fitness is calculated for every alive bird and it's higher if the bird
        is in the same horizontal line of the target.

        :param target: the middle of the next obstacle to be jumped into.
        """
        for net, bird in self:
            if bird.alive:
                net.fitness += 1 / abs(target.y - bird.position.y) # or simply net.fitness += 1

    def evolve(self):
        """Evolve the population, based on the previous population.
        The next population is made of:
        1. The bird who had the greatest fitness level, in between all generations.
        2. The top 50% of the previous generation, mixed with the greatest.
        3. Then the greatest of the previous are mixed in between themselves.
        3. Last two members are breed from two random members of the previous population.
        """
        # 1. Select parents
        best_nets = sorted(self.pop, key=lambda x: x.fitness, reverse=True)[0:self.size // 2]
        if best_nets[0].fitness > self.greatest_net.fitness:
            self.greatest_net = best_nets[0]
        # 2. Generate children
        new_pop = [self.greatest_net]
        new_pop += [NeuralNetwork.from_parents(self.greatest_net, bird) for bird in best_nets]
        new_pop += [NeuralNetwork.from_parents(*random.choices(best_nets, k=2))
                    for _ in range(self.size // 2 + 1, self.size - 2)]
        new_pop += [NeuralNetwork.from_parents(*random.choices(self.pop, k=2)) for _ in range(2)]
        # 3. Mutate children
        for net in new_pop:
            net.mutate(self.mutation_rate)

        self.pop = new_pop
        self.birds = [Bird() for _ in range(self.size)]
        self.generation += 1
