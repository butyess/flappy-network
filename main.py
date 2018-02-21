# todo: fix lag

import sys
import os
import random
import pygame
import pygame.freetype
from pygame.locals import *

from keras.models import Sequential
from keras.layers import Dense
from keras import backend as K

import numpy as np

pygame.init()
pygame.freetype.init()

font = pygame.freetype.SysFont("Source Code Pro For Powerline", 20)
if os.name == 'nt':
    font = pygame.freetype.SysFont("Source Code Pro", 20)

WHITE = (255, 255, 255)
RED = (255, 10, 10)
BLUE = (0, 0, 255)
YELLOW = (0, 255, 255)
ORANGE = (100, 200, 200)
GREEN = (0, 255, 0)

W, H = 500, 400
DS = pygame.display.set_mode((W, H))
clock = pygame.time.Clock()
font_color = (250, 250, 250)

def random_initializer(shape, dtype=None):
    return K.random_uniform(shape, dtype=dtype, minval=-1.0, maxval=1.0)


def normalize(value, maximum):
    if value < -maximum:
        value = -maximum
    elif value > maximum:
        value = maximum
    return value/maximum


def confront(player, target):
    if target >= H / 2:
        maximum = target
    elif target < H / 2:
        maximum = H - target
    return (player - target) / maximum


def random_color():
    return (tuple(random.randrange(0, 255) for _ in range(3)))


class Obstacle:
    path = [random.randint(50, H - 150)]
    ob = 0
    def __init__(self):
        self.x = W
        self.up = Obstacle.path[Obstacle.ob]
        self.y = self.up + 50
        self.alive = True
        self.index = Obstacle.ob
        Obstacle.ob += 1

    def draw(self):
        if self.x < -20:
            self.alive = False
        # upper obstacle
        self.rectup = pygame.draw.rect(DS, RED, (self.x, 0, 20, self.up))
        # lower obstacle
        self.rectdn = pygame.draw.rect(DS, RED, (self.x, self.up + 100, 20, H - (self.up + 100) ))
        self.x -= 5


class GeneticAlgorithm:
    def __init__(self, number_units):
        self.mr = 0.4
        self.nu = number_units
        self.population = [Network(self.mr) for _ in range(self.nu)]
        self.goat = Network(self.mr)

    def play(self, obs):
        # First obstacle is the target
        for ob in obs:
            if ob.alive and ob.x > 99:
                target = ob
        for player in self.population:
            if player.isAlive:
                player.calc_fitness(obs[0])
                player.draw(obs)
                player.prediction(obs)

    def status(self):
        if any(x.isAlive for x in self.population):
            return True
        else:
            return False

    def evolve(self):
        winners = self.selection()
        new_population = []
        if winners[0].fitness == 0 and self.goat.fitness < 50:
            self.population = [Network(self.mr) for _ in range(self.nu)]
        else:
            # New population
            for i in range(self.nu):
                # First member is the greatest
                if i == 0:
                    child = self.goat
                # Second member is child of goat and the best of the generation
                if i == 1:
                    parentA = self.goat
                    parentB = self.population[0]
                    child = parentA.crossover(parentB)
                # Third member is child of the two best
                elif i == 2:
                    parentA = self.population[0]
                    parentB = self.population[1]
                    child = parentA.crossover(parentB)
                # Other members are children of random winners
                elif i < self.nu - 2:
                    parentA = random.choice(winners)
                    parentB = random.choice(winners)
                    child = parentA.crossover(parentB)
                # Last 2 members are children of random previous member
                else:
                    child = random.choice(self.population)
                child.mutate()
                new_population.append(child)
            self.population = new_population

    def selection(self):
        # Greatest Of All Time
        for x in self.population:
            if x.fitness > self.goat.fitness:
                self.goat = x
        # Top 4
        self.population.sort(key=lambda x: x.fitness, reverse=True)
        for i in range(4):
            self.population[i].isWinner = True
        return self.population[0:5]


class Network:
    def __init__(self, mutation_rate, hidden_weights=False, output_weights=False):
        # Player info
        self.x = 250
        self.y = 100
        self.vel = 0
        self.acc = 30
        self.color = random_color()
        # Player genetic
        self.mr = mutation_rate
        self.index = 0
        self.fitness = 0
        self.score = 0
        self.isWinner = False
        self.isAlive = True
        self.SCALE_FACTOR = 200
        # Model
        self.model = Sequential()
        self.model.add(Dense(6, activation="sigmoid", input_dim=3, kernel_initializer=random_initializer, bias_initializer=random_initializer))
        self.model.add(Dense(1, activation="sigmoid", kernel_initializer=random_initializer, bias_initializer=random_initializer))
        if type(hidden_weights) != bool and type(output_weights) != bool:
            self.model.layers[0].set_weights(hidden_weights)
            self.model.layers[1].set_weights(output_weights)

    def prediction(self, obs):
        # Find the target
        targets = []
        for ob in obs:
            if ob.alive and ob.x + 20 > self.x:
                targets.append(ob)
        targets.sort(key=lambda x: x.x)
        target = targets[0]
        # Horizontal and vertical difference between target and player
        pygame.draw.circle(DS, WHITE, (target.x + 25, target.y), 3)
        deltax = (target.x + 25) / W * self.SCALE_FACTOR
        # deltay = normalize((self.y, target.y), 800) * self.SCALE_FACTOR
        deltay = confront(self.y, target.y) * self.SCALE_FACTOR + 20
        target_height = target.x / H * self.SCALE_FACTOR
        inputs = np.array([[deltay, deltax, target_height]])
        output = self.model.predict(inputs)
        if output[0] > 0.5:
            self.vel = -8

    def calc_fitness(self, ob):
        if self.x > ob.x:
            self.fitness += 1

    def draw(self, obs):
        # Draw player
        self.index += 1
        self.rect = pygame.draw.circle(DS, self.color, (self.x, int(self.y)), 8)
        self.vel += self.acc * clock.get_time() / 1000
        self.y += self.vel
        # Check if is alive
        for ob in obs:
            if self.rect.colliderect(ob.rectup) or self.rect.colliderect(ob.rectdn):
                self.isAlive = False
        if self.y > H or self.y < 0:
            self.isAlive = False

    def crossover(self, partner):
        weights_hidden_a, weights_output_a = self.model.layers[0].get_weights(), self.model.layers[1].get_weights()
        weights_hidden_b, weights_output_b = partner.model.layers[0].get_weights(), partner.model.layers[1].get_weights()

        # Hidden Layer
        weights_hidden_child = np.copy(weights_hidden_a)
        # Biases Hidden
        cutpoint = random.randrange(0, len(weights_hidden_child[1]))
        weights_hidden_child[1][cutpoint: -1] = weights_hidden_b[1][cutpoint: -1]
        # Weights Hidden
        for i in range(3):
            cutpoint = random.randrange(0, len(weights_hidden_child[0][i]))
            weights_hidden_child[0][i][cutpoint: -1] = weights_hidden_b[0][i][cutpoint: -1]

        # Output Layer
        weights_output_child = np.copy(weights_output_a)
        # Biases Output
        weights_output_child[1] = random.choice([weights_output_a[1], weights_output_b[1]])
        # Weights Output
        cutpoint = random.randrange(0, len(weights_output_child[1]))
        weights_output_child[0][cutpoint: -1] = weights_output_b[0][cutpoint: -1]

        return Network(self.mr, weights_hidden_child, weights_output_child)

    def mutate(self):
        weights_ih = self.model.layers[0].get_weights()
        weights_ho = self.model.layers[1].get_weights()
        for i in range(2):
            for w in range(len(weights_ih[0][i])):
                if random.random() < self.mr:
                    weights_ih[0][i] = random.uniform(-1, 1)
        for i in range(len(weights_ih[1])):
            if random.random() < self.mr:
                weights_ih[1][i] = random.uniform(-1, 1)
        for i in range(len(weights_ho[0])):
            if random.random() < self.mr:
                weights_ho[0] = random.uniform(-1, 1)
        if random.random() < self.mr:
            weights_ho[1][0] = random.uniform(-1, 1)


def events():
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.freetype.quit()
            pygame.quit()
            sys.exit()


def main():
    obs = [Obstacle()]
    obs_count = 0
    count = 0

    genetic = GeneticAlgorithm(10)

    while True:
        obs_count += 1
        count += 1

        font.render_to(DS, (10, 10), str(Obstacle.ob -1), fgcolor=WHITE)

        if obs_count >= 30:
            obs_count = 0
            Obstacle.path.append(random.randint(50, H - 150))
            obs.append(Obstacle())

        for ob in obs:
            if ob.alive:
                ob.draw()

        genetic.play(obs)

        if not genetic.status():
            count = 0
            obs_count = 0
            Obstacle.ob = 0
            Obstacle.path = [random.randint(50, H - 150)]
            obs = [Obstacle()]
            genetic.evolve()

        events()

        pygame.display.update()
        clock.tick(30)
        DS.fill((20, 30, 50))


if __name__ == '__main__':
    main()
