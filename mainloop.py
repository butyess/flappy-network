import pygame
import numpy as np

import game
from obstacles import ObstacleList
from bird import Bird
from genetic_algorithm import Population


class Simulation(game.Game):
    """Subclass of game.Game, represent the simulation. Once a generation
    is dead, and a new generation is calculated, the simulation needs to be
    restarted: to do so call setup() with the new parameters, and then run().
    """
    def setup(self, obstacles, population):
        """To be called before main loop.

        Parameters
        ----------
        obstacles : instance of ObstacleList
        population : instance of Population
        """
        self.population = population
        self.obstacles = obstacles

    def update(self, dt):
        """To be called every frame."""
        self.update_obstacles(dt)
        self.population.predict(self.get_bird_state())
        self.update_bird(dt)
        self.population.calculate_fitness(
            self.obstacles.next_obstacle(self.population.birds[0].position.x)
        )
        if not any(self.population.birds):
            self.done = True

    def update_obstacles(self, dt):
        """Updates obstacles state and draws them on the screen."""
        self.obstacles.update(dt)

        for up_rect, down_rect in self.obstacles.get_rects():
            pygame.draw.rect(self.screen, game.WHITE, up_rect)
            pygame.draw.rect(self.screen, game.WHITE, down_rect)

        if self.obstacles.left() < 0: self.obstacles.pop()
        if self.obstacles.right() < self.screen.get_width() - self.obstacles.ob_hspace:
            self.obstacles.add()

    def get_bird_state(self):
        """Calculates bird state to be given as inputs to prediction.
        It is important to normalize the inputs and give the right ones.
        In this case the inputs to the network are:
        - the vertical distance of the bird from the target
        - the horizontal distance of the birds from the target
        """
        inputs = []
        for _, bird in self.population:
            target = self.obstacles.next_obstacle(bird.position.x)
            pygame.draw.circle(self.screen, game.GREEN, target, 3)
            inputs.append(np.array([
                target.y - bird.position.y,
                target.x - bird.position.x
            ]))
        return inputs

    def update_bird(self, dt):
        """Updates bird position and check his state."""
        for _, bird in self.population:
            if bird.alive:
                bird.update(dt)
                bird.rect = pygame.draw.circle(self.screen,
                                               bird.color,
                                               bird.position,
                                               bird.radius)
                if bird.rect.collidelist([x for y in self.obstacles.get_rects() for x in y]) != -1:
                    bird.alive = False

                if bird.position.y < 0 or bird.position.y > self.screen.get_height():
                    bird.alive = False


def main():
    W, H = 800, 450
    pop_size = 10
    layers_size = (2, 6, 1)
    mutation_rate = 0.4
    pop = Population(pop_size, layers_size, mutation_rate)
    sim = Simulation(W, H)
    while not sim.exit:
        del sim
        sim = Simulation(W, H)
        obs = ObstacleList(W, H, ob_vspace=100, ob_hspace=200, ob_speed=-300)
        sim.setup(obs, pop)
        sim.run()
        pop.evolve()
    sim.quit()


if __name__ == '__main__':
    main()


