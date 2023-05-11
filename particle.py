from image_manager import ImageManager
from primitives import Pose
import random
import math
import pygame
import constants as c
from pyracy.sprite_tools import Sprite, Animation


class Particle:

    def __init__(self, position=(0, 0), velocity=(0, 0), duration=1):
        self.position = Pose(position)
        self.velocity = Pose(velocity)
        self.destroyed = False
        self.duration = duration
        self.age = 0
        self.layer = c.BACKGROUND

    def update(self, dt, events):
        if self.destroyed:
            return
        self.position += self.velocity * dt
        if self.age > self.duration:
            self.destroy()
        self.age += dt

    def draw(self, surf, offset=(0, 0)):
        if self.destroyed:
            return

    def through(self):
        return min(0.999, self.age/self.duration)

    def destroy(self):
        self.destroyed = True

class SparkParticle(Particle):
    img = None
    frames = []

    def __init__(self, position, velocity=None, duration=0.1):
        if velocity is None:
            velocity = Pose((1, 0))
        self.angle = velocity.get_angle_of_position()*180/math.pi
        self.angle_pos = velocity
        self.angle_pos.scale_to(1)
        super().__init__(position, velocity=(0, 0),duration=duration)
        if SparkParticle.img==None:
            SparkParticle.img=ImageManager.load("assets/images/flash.png")
            SparkParticle.img = pygame.transform.scale(SparkParticle.img, (SparkParticle.img.get_width()*2, SparkParticle.img.get_height()*2))
            SparkParticle.frames = [self.get_frame(i) for i in range(5)]
        self.age = 0
        self.layer = c.FOREGROUND

    def update(self, dt, events):
        super().update(dt, events)

    def get_frame(self,ct=0):
        frame = ct
        slice = pygame.Surface((42, 28))
        slice.fill((255, 0, 0))
        slice.set_colorkey((255, 0, 0))
        slice = slice.convert()
        slice.blit(SparkParticle.img, (0, -frame*28))
        return slice

    def get_frame_cached(self):
        scale = 5/self.duration
        frame = min(int(self.age*scale), 4)
        return SparkParticle.frames[frame]

    def draw(self, surface, offset=(0, 0)):
        if self.destroyed:
            return

        surf = self.get_frame_cached()
        surf = pygame.transform.rotate(surf, self.angle)
        pos = self.position + Pose(offset) - Pose((surf.get_width()//2, surf.get_height()//2)) + self.angle_pos*15
        surface.blit(surf, pos.get_position())

class Poof(Particle):
    def __init__(self, position=(0, 0), duration = 0.4):
        velocity_angle = random.random()*360
        velocity_magnitude = random.random()*200 + 300
        velocity = Pose((velocity_magnitude, 0))
        velocity.rotate_position(velocity_angle)
        super().__init__(position=position, velocity=velocity.get_position(), duration=duration)
        self.poof = ImageManager.load("assets/images/poof.png")
        self.angle = random.random()*360
        self.spin = random.random()*60 - 30

    def update(self, dt, events):
        super().update(dt, events)
        self.velocity.x *= 0.001**dt
        self.velocity.y *= 0.001**dt
        self.angle += self.spin*dt

    def draw(self, surface, offset=(0, 0)):
        if self.destroyed:
            return
        x = self.position.x + offset[0]
        y = self.position.y + offset[1]
        if x < -100 or x > c.WINDOW_WIDTH + 100:
            return
        if y < -100 or y > c.WINDOW_HEIGHT + 100:
            return

        scale = 2 - 2*self.through()
        surf = pygame.transform.scale(self.poof, (self.poof.get_width()*scale, self.poof.get_height()*scale))
        surf = pygame.transform.rotate(surf, self.angle)
        x -= surf.get_width()//2
        y -= surf.get_height()//2

        a = 128*(1 - self.through()**1.5)
        a = 256
        surf.set_alpha(a)

        surface.blit(surf, (x, y))