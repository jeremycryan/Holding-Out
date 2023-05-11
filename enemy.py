import random

import pygame

from particle import Poof
from primitives import Pose
from pyracy.sprite_tools import Sprite, Animation

import constants as c
from sound_manager import SoundManager


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

        self.sounds = [SoundManager.load(f"assets/sound/zombie_hit_{n}.ogg") for n in range(1, 8)]
        for sound in self.sounds:
            sound.set_volume(0.4)

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

        self.land()

    def cleanup(self):
        self.destroyed = True

    def spread(self):
        return 120

    def choose_new_target_position(self):
        start = self.position.copy()
        direction = self.player.position - self.position
        spread = self.spread()
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

    def wait_time(self):
        return 1 + random.random()

    def arrive_at_target(self):
        self.target_position = self.position.copy()
        self.velocity = Pose((0, 0))
        self.arrived = True
        self.since_arrived = self.wait_time()
        if self.last_walk_direction.x > 0:
            self.sprite.start_animation("IdleRight",restart_if_active=False)
        else:
            self.sprite.start_animation("IdleLeft",restart_if_active=False)

    def update_target_motion(self, dt):
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

    def update(self, dt, events):
        self.sprite.set_position(self.position.get_position())
        self.sprite.update(dt, events)

        if self.health < 0:
            if not self.dead:
                self.die()

        self.update_target_motion(dt)


        if self.arrived and not self.dead:
            self.since_arrived -= dt
            if self.since_arrived <= 0:
                self.set_target_position()

        if self.arrived or self.dead:
            self.velocity *= 0.01**dt

        if self.velocity.magnitude() > self.max_speed:
            self.velocity.scale_to(self.max_speed)

        if not self.dead:
            min_y = self.position.y - 50
            max_y = self.position.y + 50
            min_x = self.position.x - 50
            max_x = self.position.x + 50
            for item in self.frame.enemies:
                if item.dead:
                    continue
                if item.position.y > max_y:
                    break
                if item.position.y < min_y or item.position.x < min_x or item.position.x > max_x:
                    continue
                diff = self.position - item.position
                dist = diff.magnitude()
                if dist < self.radius + item.radius:
                    self.collide_with_other(item, dt)
                elif dist < self.radius + item.radius + 5:
                    self.velocity += diff*dt*10
                    item.velocity += diff*-dt*10
            for item in [self.frame.player, self.frame.phone]:
                if item.position.y > max_y:
                    continue
                if item.position.y < min_y or item.position.x < min_x or item.position.x > max_x:
                    continue
                diff = self.position - item.position
                dist = diff.magnitude()
                if dist < self.radius + item.radius:
                    self.collide_with_other(item, dt)
                elif dist <= self.radius + item.radius + 20:
                    if item.is_player:
                        continue
                    fact = 1/(dist - self.radius - item.radius)
                    self.velocity += diff*dt*20*(fact)
                    item.velocity += diff*-dt*20*(fact)
            for bullet in self.frame.bullets:
                if bullet.position.y > max_y:
                    continue
                if bullet.position.y < min_y or bullet.position.x < min_x or bullet.position.x > max_x:
                    continue
                if not bullet.can_hit(self):
                    continue
                diff = bullet.position - self.position
                if diff.magnitude() < self.radius + bullet.radius:
                    self.get_hurt(bullet)

        self.position += self.velocity*dt

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
        self.velocity += bullet.velocity*0.25
        random.choice(self.sounds).play()

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

    def land(self):
        for i in range(12):
            pos = (self.position + Pose((0, 20))).get_position()
            self.frame.particles.append(Poof(pos))

class FastEnemy(Enemy):
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

        self.sounds = [SoundManager.load(f"assets/sound/zombie_hit_{n}.ogg") for n in range(1, 8)]
        for sound in self.sounds:
            sound.set_volume(0.4)

        walk_right = Animation.from_path(
            "assets/images/zombie_2_walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            scale=2.0,
        )
        walk_left = Animation.from_path(
            "assets/images/zombie_2_walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            reverse_x=True,
            scale=2.0,
        )
        idle_right = Animation.from_path(
            "assets/images/zombie_2_forward_idle.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
        )
        idle_left = Animation.from_path(
            "assets/images/zombie_2_forward_idle.png",
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
            "assets/images/zombie_2_death.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
            time_scaling=2.0,
        )
        dead_long = Animation.from_path(
            "assets/images/zombie_2_death_long.png",
            sheet_size=(1, 1),
            frame_count=1,
            scale=2.0,
            time_scaling=0.01,
        )
        take_damage_right = Animation.from_path(
            "assets/images/zombie_2_take_damage.png",
            sheet_size=(2, 1),
            frame_count=2,
            scale=2.0,
            time_scaling = 2.0,
        )
        take_damage_left = Animation.from_path(
            "assets/images/zombie_2_take_damage.png",
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
        self.max_speed = 120

    def wait_time(self):
        return 0.5

    def spread(self):
        return 0