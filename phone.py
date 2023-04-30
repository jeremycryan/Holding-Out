import math
import time

import pygame

from camera import Camera
from image_manager import ImageManager
from primitives import Pose
from sound_manager import SoundManager


class Phone:

    def __init__(self, frame, position=(0, 0)):
        self.frame = frame
        self.position = Pose(position)
        self.back_surf = pygame.Surface((128, 128))
        self.back_surf.fill((255, 255, 0))
        self.back_surf.set_colorkey((255, 255, 0))
        desk = pygame.transform.scale(ImageManager.load("assets/images/desk.png"), (76, 84))
        self.back_surf.blit(desk, (self.back_surf.get_width()//2 - desk.get_width()//2, self.back_surf.get_height()//2 - desk.get_height()//2))
        cradle = pygame.transform.scale(ImageManager.load("assets/images/cradle.png"), (58, 48))
        self.back_surf.blit(cradle, (self.back_surf.get_width() // 2 - cradle.get_width() // 2 - 1,
                                   self.back_surf.get_height() // 2 - cradle.get_height() // 2 - 24))
        self.phone_surf = ImageManager.load("assets/images/phone.png")
        self.phone_surf = pygame.transform.scale(self.phone_surf, (self.phone_surf.get_width()*2, self.phone_surf.get_height()*2))
        self.e = ImageManager.load("assets/images/e.png")
        self.e = pygame.transform.scale(self.e, (self.e.get_width()*2, self.e.get_height()*2))

        self.hold = ImageManager.load("assets/images/hold.png")
        self.hold = pygame.transform.scale(self.hold, (self.hold.get_width()*2, self.hold.get_height()*2))

        self.phone_on = True

        self.since_hang_up = 10

        self.radius = 32
        self.is_player = False
        self.velocity = Pose((0, 0))

        self.on_hold = False
        self.since_hold = 0
        self.hold_time = 10

        self.ring = SoundManager.load("assets/sound/phone_ring.ogg")
        self.pick_up_sound = SoundManager.load("assets/sound/pick_up.ogg")
        self.pick_up_sound.set_volume(0.05)
        self.hang_up_sound = SoundManager.load("assets/sound/hang_up.ogg")

    def pick_up(self):
        self.phone_on = False
        if not self.frame.gary.lines:
            self.frame.gary.get_next_lines()
        else:
            self.frame.gary.restart_line()
            self.frame.gary.target = 1
        self.pick_up_sound.play()

    def hang_up(self):
        self.phone_on = True
        self.since_hang_up = 0
        Camera.shake(10)
        self.frame.gary.target = 0
        self.hang_up_sound.play()

    def update(self, dt, events):
        if self.phone_on:
            self.since_hang_up += dt
        if self.on_hold:
            self.since_hold += dt
            self.frame.time_on_hold += dt
            if self.since_hold > self.hold_time:
                self.stop_hold()

    def start_hold(self, time=10):
        self.on_hold = True
        self.since_hold = 0
        self.hold_time = time
        self.frame.target_music_volume = 1

    def stop_hold(self):
        self.on_hold = False
        self.frame.target_music_volume = 0
        if 1:#self.since_hold > 0.25:
            self.ring.play()

    def draw(self, surface, offset=(0, 0)):

        center_pos = self.position + Pose(offset)
        position = center_pos - Pose((self.back_surf.get_width()//2, self.back_surf.get_height()//2))
        surface.blit(self.back_surf, position.get_position())

        if self.phone_on:
            yoff = 20
            yoff = max(24, 38 - self.since_hang_up*200)
            phone_position = center_pos - Pose((self.phone_surf.get_width()//2, self.phone_surf.get_height()//2 + yoff))
            surface.blit(self.phone_surf, phone_position.get_position())

        if self.in_pickup_range(self.frame.player) and not self.on_hold:
            e_pos = center_pos - Pose((self.e.get_width()//2, self.e.get_height()//2)) + Pose((0, -70 + 3*math.sin(time.time()*8)))
            surface.blit(self.e, e_pos.get_position())
        elif self.on_hold:
            e_pos = center_pos - Pose((self.hold.get_width()//2, self.hold.get_height()//2)) + Pose((0, -70 + 3*math.sin(time.time()*8)))
            surface.blit(self.hold, e_pos.get_position())

    def draw_shadow(self, surface, offset=(0, 0)):
        pass

    def in_pickup_range(self, player):
        if self.on_hold:
            return False
        return (self.position - player.position).magnitude() < 128