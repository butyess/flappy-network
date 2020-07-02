from random import randint

import pygame
from pygame import Vector2


class ObstacleList:
    """Class that manages obstacles."""

    def __init__(self, screen_width: int, screen_height: int,
                 ob_width: int = 30, ob_vspace: int = 150,
                 ob_hspace: int = 200, ob_speed: int = -200,
                 middle=None):
        """Initialize the class.

        :param screen_width: needed for obstacle objects.
        :param screen_height: needed for obstacle objects.
        :param ob_width: width of obstacles.
        :param ob_vspace: space in the middle of the obstacle.
        :param ob_hspace: space in between two consecutive obstacles.
        :param ob_speed: speed to move the obstacles.
        :param middle: the middle of the obstacles, leave default for random.
        """
        self.obstacles = []
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ob_width = ob_width
        self.ob_vspace = ob_vspace
        self.ob_hspace = ob_hspace
        self.ob_speed = ob_speed
        self.middle = middle
        self.add()

    def add(self):
        """Adds an obstacle at the right."""
        if not self.middle:
            middle = randint(self.screen_height // 10,
                             self.screen_height - self.screen_height // 10)
        else:
            middle = self.middle
        self.obstacles.append(Obstacle(self.ob_width,
                                       self.screen_width,
                                       self.screen_height,
                                       middle,
                                       self.ob_vspace))

    def pop(self):
        """Deletes the leftmost obstacle."""
        self.obstacles.pop(0)

    def right(self):
        """Returns the right edge value for the rightmost obstacle."""
        return self.obstacles[-1].up_rect.right

    def left(self):
        """Returns the right edge value for the leftmost obstacle."""
        return self.obstacles[0].up_rect.right

    def next_obstacle(self, bird_x: int):
        """Returns the center of the next obstacle the bird given will fly into.

        :param bird_x: the x coordination of the bird
        """
        for ob in self.obstacles:
            if ob.up_rect.centerx > bird_x:
                return Vector2(ob.up_rect.right, ob.middle)

    def get_rects(self):
        """Yields the rect objects of the obstacles."""
        for ob in self.obstacles:
            yield ob.up_rect, ob.down_rect

    def update(self, dt):
        """Updates every obstacle."""
        for ob in self.obstacles:
            ob.update(dt, self.ob_speed)


class Obstacle:
    """Represents an obstacle: an obstacle is made of a top pygame.Rect and a bottom pygame.Rect;
    those are defined as self.up_rect and self.down_rect.
    """

    def __init__(self, width: int, screen_width: int, screen_height: int,
                 middle: int, vspace: int = 50):
        """Instantiate an obstacle at the right of the screen

        :param width: the width of the obstacle, in pixels.
        :param screen_width: needed to put the obstacle at the right of the screen.
        :param screen_height: needed to calculate the rect of the object.
        :param middle: the middle of the obstacle, where the birds should fly into.
        :param vspace: vertical spacing in the middle of the obstacle.
        """
        self.middle = middle
        self.up_rect = pygame.Rect(screen_width,
                                   0,
                                   width,
                                   self.middle - vspace // 2)
        self.down_rect = pygame.Rect(screen_width,
                                     self.middle + vspace // 2,
                                     width,
                                     screen_height - (self.middle + vspace // 2))

    def update(self, dt: int, speed: Vector2):
        """Move the obstacle, based on its speed.

        :param dt: delta time
        :param speed: speed vector
        """
        self.up_rect.move_ip(speed * dt, 0)
        self.down_rect.move_ip(speed * dt, 0)
