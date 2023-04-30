import math
import random

import pygame

from image_manager import ImageManager
from primitives import Pose
import constants as c


class Bullet:
    sprite = None

    def __init__(self, position, direction, damage=40, pierce=1, frame=None):
        # if Bullet.sprite is None:
        #     Bullet.sprite = ImageManager.load("assets/images/bullet.png")
        self.position = Pose(position)
        self.velocity = Pose(direction)
        self.velocity.scale_to(2500)
        self.destroyed = False
        self.damage = damage
        self.radius = 25
        self.pierce = pierce
        self.frame = frame

        self.enemies_hit = set()

        if Bullet.sprite is None:
            Bullet.sprite = ImageManager.load("assets/images/bullet.png")

    def update(self, dt, events):
        self.position += self.velocity*dt
        if self.position.x < -c.ARENA_WIDTH or self.position.y < -c.ARENA_HEIGHT or self.position.x > c.ARENA_WIDTH or self.position.y > c.ARENA_HEIGHT:
            self.destroy()
            if len(self.enemies_hit)==0 and "Green" in self.frame.player.upgrades:
                if random.random() < 0.5:
                    self.frame.player.ammo += 1


    def destroy(self):
        self.destroyed = True

    def can_hit(self, enemy):
        if self.destroyed:
            return False
        if enemy in self.enemies_hit:
            return False
        return True

    def reduce_durability(self):
        self.pierce -= 1
        if self.pierce <= 0:
            self.destroy()

    def draw(self, surface, offset=(0, 0)):
        position = self.position + Pose(offset)

        surf = pygame.transform.rotate(Bullet.sprite, self.velocity.get_angle_of_position()*180/math.pi)

        position += Pose((-surf.get_width()//2, -surf.get_height()//2))
        surface.blit(surf, position.get_position())