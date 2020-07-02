import pygame
import numpy as np

from gameobjects.game import Game, WHITE, GREEN
from gameobjects.obstacles import ObstacleList
from genetics.population import Population


class Simulation:
    def __init__(self, obstacles: ObstacleList, population: Population):
        """Initialize simulation.

        :param obstacles: List of obstacles to be used in simulation.
        :param population: Population of birds and networks.
        """
        self.population = population
        self.obstacles = obstacles
        self.done = False

    def update(self, surface: pygame.Surface, dt: float):
        """To be called every frame of the simulation.

        :param surface: screen surface where to draw.
        :param dt: delta time.
        """
        self.update_obstacles(surface, dt)
        self.population.predict(self.get_bird_state())
        self.update_bird(surface, dt)
        self.population.calculate_fitness(
            self.obstacles.next_obstacle(self.population.birds[0].position.x)
        )
        if not any(map(lambda x: x.alive, self.population.birds)):
            self.done = True

    def update_obstacles(self, surface: pygame.Surface, dt: float):
        """Updates obstacles state and draws them on the screen."""
        self.obstacles.update(dt)

        for up_rect, down_rect in self.obstacles.get_rects():
            pygame.draw.rect(surface, WHITE, up_rect)
            pygame.draw.rect(surface, WHITE, down_rect)

        if self.obstacles.left() < 0: self.obstacles.pop()
        if self.obstacles.right() < surface.get_width() - self.obstacles.ob_hspace:
            self.obstacles.add()

    def update_bird(self, surface, dt):
        """Updates birds positions and checks if they are still alive."""
        for _, bird in self.population:
            if bird.alive:
                bird.update(dt)
                bird.rect = pygame.draw.circle(surface,
                                               bird.color,
                                               bird.position,
                                               bird.radius)
                if bird.rect.collidelist([rect for rects in self.obstacles.get_rects() for rect in rects]) != -1:
                    bird.alive = False

                if bird.position.y < 0 or bird.position.y > surface.get_height():
                    bird.alive = False

    def get_bird_state(self):
        """Calculates bird state to be given as inputs to prediction.
        In this case the inputs to the network are:
        - the vertical distance of the bird from the target
        - the horizontal distance of the birds from the target
        """
        inputs = []
        for _, bird in self.population:
            target = self.obstacles.next_obstacle(bird.position.x)
            inputs.append(np.array([
                target.y - bird.position.y,
                target.x - bird.position.x
            ]))
        return inputs


def main():
    game = Game(width=800, height=450)
    population = Population(size=10, layers=(2, 6, 1), mutation_rate=0.4)
    while not game.exit:
        obstacles = ObstacleList(screen_width=game.screen.get_width(),
                                 screen_height=game.screen.get_height(),
                                 ob_width=30, ob_vspace=100, ob_hspace=200, ob_speed=-300)
        sim = Simulation(obstacles, population)
        game.run(sim)
        population.evolve()
    game.quit()


if __name__ == '__main__':
    main()


