import math
import random

import pygame

from image_manager import ImageManager
from primitives import Pose
import constants as c


class Bullet:
    sprite = None

    def __init__(self, position, direction, damage=40, pierce=1, frame=None, homing=False, refundable = False):
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
        self.homing = homing
        self.target = None
        self.refundable = refundable

        self.enemies_hit = set()

        if Bullet.sprite is None:
            Bullet.sprite = ImageManager.load("assets/images/bullet.png")

        if self.homing:
            self.update_target()

    def update_target(self):
        best_target = None
        best_target_score = -999
        unit = self.velocity * (1/(self.velocity.magnitude() + 0.00001))
        side_unit = unit.copy()
        side_unit.rotate_position(90)
        for enemy in self.frame.enemies:
            if enemy.dead:
                continue
            dirness = (enemy.position - self.position).dot(unit)
            if dirness < 0:
                continue
            if dirness > 1200:
                continue
            sideness = abs((enemy.position - self.position).dot(side_unit))
            if sideness > dirness:
                continue
            score = dirness / sideness / (enemy.position - self.position).magnitude()
            if score > best_target_score:
                best_target = enemy
                best_target_score = score
        if best_target:
            self.target = best_target

    def update(self, dt, events):



        self.position += self.velocity*dt
        if self.position.x < -c.ARENA_WIDTH or self.position.y < -c.ARENA_HEIGHT or self.position.x > c.ARENA_WIDTH or self.position.y > c.ARENA_HEIGHT:
            self.destroy()
            if len(self.enemies_hit)==0 and "Green" in self.frame.player.upgrades:
                if self.refundable:
                    if random.random() < 0.5:
                        self.frame.player.ammo += 1

        if self.homing:
            if self.target is not None and not self.target.dead:
                unit = self.velocity * (1/(self.velocity.magnitude() + 0.00001))
                side_unit = unit.copy()
                side_unit.rotate_position(90)
                diff = self.target.position - self.position
                dirness = (diff).dot(unit)
                if dirness < 0:
                    return
                sideness = (diff).dot(side_unit)
                speed = 500
                if sideness > 0:
                    self.velocity.rotate_position(speed*dt)
                else:
                    self.velocity.rotate_position(-speed*dt)



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
        if self.homing:
            self.update_target()

    def draw(self, surface, offset=(0, 0)):
        position = self.position + Pose(offset)

        surf = pygame.transform.rotate(Bullet.sprite, self.velocity.get_angle_of_position()*180/math.pi)

        position += Pose((-surf.get_width()//2, -surf.get_height()//2))
        surface.blit(surf, position.get_position())