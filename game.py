from random import randint

import pygame
from pygame import Vector2


WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
RED = (255, 10, 10)
BLUE = (10, 10, 255)
YELLOW = (10, 255, 255)
ORANGE = (100, 200, 200)
GREEN = (10, 255, 10)


class Game:
    """Represents a basic game."""
    def __init__(self, width, height, fps=60):
        """Initialize pygame and basic game informations."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.done = False
        self.exit = False

    def run(self):
        """Wrapper for update method. It update in a loop."""
        while not self.done and not self.exit:
            dt = self.clock.get_time() / 1000

            self.listen_events(pygame.event.get())
            self.screen.fill(GRAY)

            self.update(dt)

            pygame.display.flip()
            self.clock.tick(self.fps)

        if self.exit:
            self.quit

    def quit(self):
        """Quits pygame."""
        pygame.quit()

    def listen_events(self, events):
        """Listen to pygame events."""
        for e in events:
            if e.type == pygame.QUIT:
                self.exit = True

    def update(self, dt):
        pass

    def setup(self):
        pass

