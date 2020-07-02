from random import randint

import pygame
from pygame import Vector2


class ObstacleList:
    """Class that manages the obstacles."""
    def __init__(self, screen_width, screen_height,
            ob_width=30, ob_vspace=150, ob_hspace=200, ob_speed=-200, middle=None):
        """Initialize the class

        Parameters
        ----------
        screen_width : needed for obstacle objects
        screen_height : needed for obstacle objects
        ob_width : width of obstacles
        ob_vspace : space in the middle of the obstacle
        ob_hspace : space in between two consecutive obstacles
        ob_speed : speed to move the obstacles
        middle : the middle of the obstacles, leave default for random.
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
        """Adds an obstacle at the right of the screen."""
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
        """Deletes the obstacle at the leftmost of the screen."""
        self.obstacles.pop(0)

    def right(self):
        """Returns the right edge value for the rightmost obstacle in the screen."""
        return self.obstacles[-1].up_rect.right

    def left(self):
        """Returns the right edge value for the leftmost obstacle in the screen."""
        return self.obstacles[0].up_rect.right

    def next_obstacle(self, bird_x):
        """Returns the center of the next obstacle the bird will fly into.

        Parameters
        ----------
        bird_x : the x coordination of the birds
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
    """Represents an obstacle: an obstacle is made of a top pygame.Rect
    and a bottom pygame.Rect; those are defined as self.up_rect and self.down_rect.
    """
    def __init__(self, width, screen_width, screen_height, middle, vspace=50):
        """Instanciate an obstacle at the right of the screen

        Parameters
        ----------
        width : the width of the obstacle, in pixels
        screen_width : needed to put the obstacle at the right of the screen.
        screen_height : needed to calculate the rect of the object.
        middle : the middle of the obstacle, where the birds should fly into.
        vspace : vertical spacing in the middle of the obstacle.
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

    def update(self, dt, speed):
        """Move the obstacle, based on its speed."""
        self.up_rect.move_ip(speed * dt, 0)
        self.down_rect.move_ip(speed * dt, 0)

