import random

import numpy as np

import pygame
from pygame import Vector2


relu = np.vectorize(lambda x: x if x > 0 else 0)
sigmoid = np.vectorize(lambda x: 1 / (1 + np.exp(-x)))
softmax = np.vectorize(lambda x: np.exp(x) / np.sum(np.exp(x)))


def random_color():
    return (tuple(random.randrange(0, 255) for _ in range(3)))


class Bird:
    """Class to represent a bird in the game,"""
    initial_position = (300, 300)
    radius = 10
    gravity = Vector2(0, 900)
    jump_speed = (0, -300)

    def __init__(self, color=random_color()):
        """Initializes the bird.

        Parameters
        ----------
        color : color of the bird
        """
        self.color = random_color()
        self.position = Vector2(self.initial_position)
        self.velocity = Vector2(0, 0)
        self.rect: pygame.Rect
        self.alive = True

    def __bool__(self):
        """Used to perform a quick check on Birds."""
        return self.alive

    def update(self, dt):
        """Update physical information about the Bird.

        Parameters
        ----------
        dt : the delta time
        """
        self.position += self.velocity * dt
        self.velocity += self.gravity * dt

    def jump(self):
        """Call this when the Bird performs a jump."""
        self.velocity = Vector2(self.jump_speed)


class NeuralNetwork:
    """Simple neural network without backpropagation."""
    activation = sigmoid

    def __init__(self, neurons):
        """Initialize the neural network.

        Parameters
        ----------
        neurons : list of the number of neurons, for every layer
        """
        self.neurons = neurons
        self.size = len(neurons)
        self.weights = [np.random.uniform(-1, 1, (self.neurons[i], self.neurons[i+1]))
                for i in range(self.size - 1)]
        self.biases = [np.random.uniform(-1, 1, (1, i)) for i in self.neurons[1:]]
        self.fitness = 0

    def __getitem__(self, key):
        """Used to perform a quick access to weight and biases.
        
        key == 0: weights
        key == 1: biases
        """
        if key == 0: return self.weights
        if key == 1: return self.biases
        else: raise IndexError

    def __iter__(self):
        """Used to perform quick access to weight and biases."""
        yield from [self.biases, self.weights]

    def predict(self, x):
        """Use weight, biases and activation function to run the network.

        Parameters
        ----------
        x : ndarray that represents input
        """
        res = x
        for i in range(self.size - 1):
            res = self.activation(res @ self.weights[i] + self.biases[i])
        return res

    def mutate(self, mutation_rate):
        """Performs random mutation.
        Parameters
        ----------
        mutation_rate : probability of a random parameter
        """
        for wb in self:
            for layer in wb:
                for value in layer:
                    if random.random() < mutation_rate:
                        value = random.uniform(-1, 1)

    @staticmethod
    def from_parents(father, mother):
        """Create a neural network from two others neural networks

        Parameters
        ----------
        father : a neural network
        mother : a neural network
        """
        child = NeuralNetwork(father.neurons)
        before = np.copy(child.weights[0])

        # for c_type, f_type, m_type in zip(child, father, mother): # for weights and biases
        #     for c_layer, f_layer, m_layer in zip(c_type, f_type, m_type): # for every layer
        #         for c_value, f_value, m_value in zip(c_layer, f_layer, m_layer): # for every w or bias in layer
        #             c_value = random.choice((f_value, m_value))

        # Weights
        for matrix in range(len(child.weights)):
            for line in range(len(child.weights[matrix])):
                for value in range(len(child.weights[matrix][line])):
                    child.weights[matrix][line][value] = random.choice((
                            father.weights[matrix][line][value],
                            mother.weights[matrix][line][value]
                        ))
        # Biases
        for matrix in range(len(child.biases)):
            for line in range(len(child.biases[matrix])):
                for value in range(len(child.biases[matrix][line])):
                    child.biases[matrix][line][value] = random.choice((
                            father.biases[matrix][line][value],
                            mother.biases[matrix][line][value]
                        ))

        return child

