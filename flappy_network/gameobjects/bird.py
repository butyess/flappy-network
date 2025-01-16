from typing import Tuple

import random

import pygame
from pygame import Vector2


def random_color():
    return tuple(random.randrange(0, 255) for _ in range(3))


class Bird:
    """Class to represent a bird in the game."""

    initial_position = (300, 300)
    radius = 10
    gravity = Vector2(0, 900)
    jump_speed = (0, -300)

    def __init__(self, color: Tuple = None):
        """Initializes the bird.

        :param color: color of the bird.
        """
        self.color = color if color else random_color()
        self.position = Vector2(self.initial_position)
        self.velocity = Vector2(0, 0)
        self.rect: pygame.Rect
        self.alive = True

    def update(self, dt):
        """Update physical information about the Bird.

        :param dt: the time delta.
        """
        self.position += self.velocity * dt
        self.velocity += self.gravity * dt

    def jump(self):
        """Call this when the Bird performs a jump."""
        self.velocity = Vector2(self.jump_speed)
