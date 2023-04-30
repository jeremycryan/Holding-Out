import random

import pygame

from primitives import Pose
from pyracy.sprite_tools import Sprite, Animation

import constants as c


class Enemy:

    def __init__(self, frame, position=(0, 0)):
        self.frame = frame
        self.player = self.frame.player

        self.position = Pose(position)
        self.velocity = Pose((0, 0))
        self.target_velocity = Pose((0, 0))
        self.sprite = Sprite(6, (0, 0))

        self.last_walk_direction = Pose((1, 0))

        self.is_player = False

        self.dead = False

        self.health = 100
        self.max_health = 100
        self.radius = self.player.radius

        self.target_position = self.position.copy()
        self.destroyed = False

        self.arrived = True
        self.since_arrived = random.random()

        walk_right = Animation.from_path(
            "assets/images/zombie_walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            scale=2.0,
        )
        walk_left = Animation.from_path(
            "assets/images/zombie_walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            reverse_x=True,
            scale=2.0,
        )
        idle_right = Animation.from_path(
            "assets/images/zombie_forward_idle.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
        )
        idle_left = Animation.from_path(
            "assets/images/zombie_forward_idle.png",
            sheet_size=(8, 1),
            frame_count=8,
            reverse_x=True,
            scale=2.0,
        )
        walk_back_right = Animation.from_path(
            "assets/images/walk_right_back.png",
            sheet_size=(6, 1),
            frame_count=6,
            scale=2.0,

        )
        walk_back_left = Animation.from_path(
            "assets/images/walk_right_back.png",
            sheet_size=(6, 1),
            frame_count=6,
            reverse_x=True,
            scale=2.0,
        )
        dead = Animation.from_path(
            "assets/images/zombie_death.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
            time_scaling=2.0,
        )
        dead_long = Animation.from_path(
            "assets/images/zombie_death_long.png",
            sheet_size=(1, 1),
            frame_count=1,
            scale=2.0,
            time_scaling=0.01,
        )
        take_damage_right = Animation.from_path(
            "assets/images/zombie_take_damage.png",
            sheet_size=(2, 1),
            frame_count=2,
            scale=2.0,
            time_scaling = 2.0,
        )
        take_damage_left = Animation.from_path(
            "assets/images/zombie_take_damage.png",
            sheet_size=(2, 1),
            frame_count=2,
            reverse_x=True,
            scale=2.0,
            time_scaling = 2.0,
        )

        self.sprite.add_animation(
            {
                "WalkRight": walk_right,
                "WalkLeft": walk_left,
                "IdleRight": idle_right,
                "IdleLeft": idle_left,
                "WalkBackRight": walk_back_right,
                "WalkBackLeft": walk_back_left,
            },
            loop=True
        )
        self.sprite.add_animation(
            {
                "Dead": dead,
                "TakeDamageRight": take_damage_right,
                "TakeDamageLeft": take_damage_left,
                "DeadLong": dead_long,
            },
            loop=False
        )

        self.sprite.start_animation("IdleRight")
        self.sprite.add_callback("TakeDamageRight",self.arrive_at_target)
        self.sprite.add_callback("TakeDamageLeft",self.arrive_at_target)
        self.sprite.add_callback("DeadLong",self.cleanup)
        self.sprite.chain_animation("TakeDamageRight","IdleRight")
        self.sprite.chain_animation("TakeDamageLeft","IdleLeft")
        self.sprite.chain_animation("Dead","DeadLong")

        self.shadow = pygame.Surface((self.radius*3, self.radius*3//2))
        self.shadow.fill((255, 255, 0))
        self.shadow.set_colorkey((255, 255, 0))
        pygame.draw.ellipse(self.shadow, (0, 0, 0), self.shadow.get_rect())
        self.shadow.set_alpha(60)

        self.max_speed = 80
        self.since_start_walking = 10

    def cleanup(self):
        self.destroyed = True

    def choose_new_target_position(self):
        start = self.position.copy()
        direction = self.player.position - self.position
        spread = 120
        direction.rotate_position(random.random()*spread - spread/2)
        direction.scale_to(70 + 50*random.random())
        return start + direction

    def set_target_position(self):
        self.target_position = self.choose_new_target_position()
        self.arrived = False
        self.last_walk_direction = self.target_position - self.position
        if self.last_walk_direction.x > 0:
            self.sprite.start_animation("WalkRight")
        else:
            self.sprite.start_animation("WalkLeft")
        self.since_start_walking = 0

    def die(self):
        self.dead = True
        self.sprite.start_animation("Dead")
        self.frame.zombies_killed += 1

    def draw(self, surface, offset=(0, 0)):
        self.sprite.draw(surface, offset)

    def arrive_at_target(self):
        self.target_position = self.position.copy()
        self.velocity = Pose((0, 0))
        self.arrived = True
        self.since_arrived = 1 + random.random()
        if self.last_walk_direction.x > 0:
            self.sprite.start_animation("IdleRight",restart_if_active=False)
        else:
            self.sprite.start_animation("IdleLeft",restart_if_active=False)

    def update(self, dt, events):
        self.sprite.set_position(self.position.get_position())
        self.sprite.update(dt, events)

        if self.health < 0:
            if not self.dead:
                self.die()

        if not self.dead:
            target_direction = self.target_position - self.position
            if target_direction.magnitude() > 20:
                target_direction.scale_to(self.max_speed)
                self.target_velocity = target_direction
                dv = self.target_velocity - self.velocity
                if not self.arrived:
                    self.velocity += dv * 5
                self.since_start_walking += dt
                if self.since_start_walking > 4:
                    self.arrive_at_target()
            elif not self.arrived:
                self.arrive_at_target()


        if self.arrived and not self.dead:
            self.since_arrived -= dt
            if self.since_arrived <= 0:
                self.set_target_position()

        if self.arrived or self.dead:
            self.velocity *= 0.01**dt

        if self.velocity.magnitude() > self.max_speed:
            self.velocity.scale_to(self.max_speed)

        self.position += self.velocity*dt
        if not self.dead:
            for item in self.frame.collideables():
                diff = self.position - item.position
                if diff.magnitude() < self.radius + item.radius:
                    self.collide_with_other(item, dt)
                elif diff.magnitude() < self.radius + item.radius + 5:
                    if item.is_player:
                        continue
                    self.velocity += diff*dt*10
                    item.velocity += diff*-dt*10
            for bullet in self.frame.bullets:
                diff = bullet.position - self.position
                if diff.magnitude() < self.radius + bullet.radius and bullet.can_hit(self):
                    self.get_hurt(bullet)

        if self.position.x < -c.ARENA_WIDTH//2 + self.radius:
            self.position.x = -c.ARENA_WIDTH//2 + self.radius
        if self.position.y < -c.ARENA_HEIGHT//2:
            self.position.y = -c.ARENA_HEIGHT//2
        if self.position.x > c.ARENA_WIDTH//2 - self.radius:
            self.position.x = c.ARENA_WIDTH//2 - self.radius
        if self.position.y > c.ARENA_HEIGHT//2 - self.radius*2:
            self.position.y = c.ARENA_HEIGHT//2 - self.radius*2

    def get_hurt(self, bullet):
        bullet.enemies_hit.add(self)
        self.health -= bullet.damage

        if self.last_walk_direction.x > 0:
            self.sprite.start_animation("TakeDamageRight")
        else:
            self.sprite.start_animation("TakeDamageLeft")

        bullet.reduce_durability()
        self.velocity += bullet.velocity

    def collide_with_other(self, other, dt):
        if other is self:
            return

        if other.is_player:
            if other.rolling:
                return
            other.get_hurt(other.position - self.position)

        diff = self.position - other.position
        if diff.magnitude() < self.radius + other.radius:
            delta = diff.copy()
            delta.scale_to(self.radius + other.radius - diff.magnitude())
            diff.scale_to(self.radius + other.radius)
            self.position += delta * dt * 100


    def draw_shadow(self, surface, offset=(0, 0)):
        surface.blit(self.shadow, (self.position.x + offset[0] - self.shadow.get_width()//2,
                                   self.position.y + offset[1] - self.shadow.get_height()//2 + 25))