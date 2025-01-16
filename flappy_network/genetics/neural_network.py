from typing import Tuple

import random

import numpy as np


relu = np.vectorize(lambda x: x if x > 0 else 0)
sigmoid = np.vectorize(lambda x: 1 / (1 + np.exp(-x)))
softmax = np.vectorize(lambda x: np.exp(x) / np.sum(np.exp(x)))


class NeuralNetwork:
    """Simple neural network without backpropagation."""

    activation = sigmoid

    def __init__(self, layers: Tuple):
        """Initialize the neural network.

        :param layers: list of the number of neurons, for every layer.
        """
        self.layers = layers
        self.size = len(layers)
        self.weights = [np.random.uniform(-1, 1, (self.layers[i], self.layers[ i +1]))
                        for i in range(self.size - 1)]
        self.biases = [np.random.uniform(-1, 1, (1, i)) for i in self.layers[1:]]
        self.fitness = 0

    def __getitem__(self, key: int):
        """Used to perform a quick access to weight and biases.

        key == 0: weights
        key == 1: biases
        """
        return (self.weights, self.biases, IndexError)[key]

    def __iter__(self):
        """Used to perform quick access to weight and biases."""
        yield from [self.biases, self.weights]

    def predict(self, x: np.ndarray):
        """Use weight, biases and activation function to run the network.
        for inputs see 'mainloop.Simulation.get_bird_state'.

        :param x: numpy array that represents inputs.
        """
        res = x
        for i in range(self.size - 1):
            res = self.activation(res @ self.weights[i] + self.biases[i])
        return res

    def mutate(self, mutation_rate: int):
        """Performs random mutation.

        :param mutation_rate: probability of a random parameter.
        """
        for wb in self:
            for layer in wb:
                for value in layer:
                    if random.random() < mutation_rate:
                        value = random.uniform(-1, 1)

    @staticmethod
    def from_parents(father, mother):
        """Create a neural network from two others neural networks

        :param father: a neural network.
        :param mother: a neural network.
        """
        child = NeuralNetwork(father.layers)

        for c_type, f_type, m_type in zip(child, father, mother):  # for weights and biases
            for c_layer, f_layer, m_layer in zip(c_type, f_type, m_type):  # for every layer
                for c_value, f_value, m_value in zip(c_layer, f_layer, m_layer):  # for every w or bias in layer
                    c_value = random.choice((f_value, m_value))

        return child
