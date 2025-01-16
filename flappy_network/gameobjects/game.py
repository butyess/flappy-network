import pygame


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
        """Initialize pygame and basic game information.

        :param width: window width.
        :param height: window height.
        :param fps: target fps for the game.
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        self.clock = pygame.time.Clock()
        self.fps = fps
        self.exit = False

    def run(self, runnable):
        """Runs a runnable object.

        :param runnable: an object that has an 'update()' method
                         and a 'done' attribute.
        """
        while not runnable.done and not self.exit:
            dt = self.clock.get_time() / 1000

            self.listen_events(pygame.event.get())
            self.screen.fill(GRAY)

            runnable.update(self.screen, dt)

            pygame.display.flip()
            self.clock.tick(self.fps)

    def listen_events(self, events):
        """Listen to pygame events."""
        for e in events:
            if e.type == pygame.QUIT:
                self.exit = True

    def quit(self):
        """Quits pygame."""
        pygame.quit()
