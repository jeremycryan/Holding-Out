from bullet import Bullet
from image_manager import ImageManager
from particle import SparkParticle, Poof
from pyracy.sprite_tools import Sprite, Animation
from primitives import Pose
import pygame
import constants as c
import math
from camera import Camera
import random
from sound_manager import SoundManager

class Player:

    def __init__(self, frame):
        self.frame = frame
        self.position = Pose((-96, 0))
        Camera.position = self.position.copy() - Pose(c.WINDOW_SIZE)*0.5
        self.velocity = Pose((0, 0))
        self.sprite = Sprite(12, (0, 0))

        self.is_player = True

        self.since_damage = 999
        self.dead = False

        self.health = 3
        self.max_health = 3

        self.since_fire = 9

        self.fire_rate = 0.25
        self.destroyed = False

        self.ammo = 120
        self.max_ammo = self.ammo
        self.upgrades = ["Hat"]

        self.gunshot_sound = SoundManager.load("assets/sound/gunshot.ogg")
        self.gunshot_sound.set_volume(0.3)
        self.dodge_sound = SoundManager.load("assets/sound/dodge.ogg")
        self.dodge_sound.set_volume(0.4)

        walk_right = Animation.from_path(
            "assets/images/walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            scale=2.0,

        )
        walk_left = Animation.from_path(
            "assets/images/walk_right.png",
            sheet_size=(6, 1),
            frame_count=6,
            reverse_x=True,
            scale=2.0,
        )
        idle_right = Animation.from_path(
            "assets/images/forward_idle.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
        )
        idle_left = Animation.from_path(
            "assets/images/forward_idle.png",
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
            frame_count=6 ,
            reverse_x=True,
            scale=2.0,
        )
        rolling = Animation.from_path(
            "assets/images/roll.png",
            sheet_size=(6, 1),
            frame_count=6,
            scale=2.0,
        )
        dead = Animation.from_path(
            "assets/images/player death.png",
            sheet_size=(8, 1),
            frame_count=8,
            scale=2.0,
        )
        take_damage_right = Animation.from_path(
            "assets/images/player_take_damage.png",
            sheet_size=(6, 1),
            frame_count=3,
            scale=2.0,
        )
        take_damage_left = Animation.from_path(
            "assets/images/player_take_damage.png",
            sheet_size=(6, 1),
            frame_count=3,
            reverse_x=True,
            scale=2.0,
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
            },
            loop=False
        )

        self.since_roll_finish = 99

        self.sprite.add_animation({"Rolling": rolling})
        self.sprite.add_callback("Rolling", self.stop_rolling)
        self.sprite.add_callback("TakeDamageRight", self.stop_taking_damage)
        self.sprite.add_callback("TakeDamageLeft", self.stop_taking_damage)
        self.sprite.start_animation("WalkRight")

        self.animation_state = c.IDLE
        self.last_lr_direction = c.RIGHT
        self.rolling = False
        self.radius = 20

        self.shadow = pygame.Surface((self.radius*3, self.radius*3//2))
        self.shadow.fill((255, 255, 0))
        self.shadow.set_colorkey((255, 255, 0))
        pygame.draw.ellipse(self.shadow, (0, 0, 0), self.shadow.get_rect())
        self.shadow.set_alpha(60)

        self.holding_phone = False
        self.since_pick_up = 10
        self.hurt_sound = SoundManager.load("assets/sound/player_hurt.ogg")
        self.hurt_sound.set_volume(1)


        self.gun_angle = 0
        self.gun_image = ImageManager.load("assets/images/gun.png")

        self.phone_surf = ImageManager.load("assets/images/phone.png")
        self.phone_surf = pygame.transform.rotate(self.phone_surf, (90))
        self.phone_surf = pygame.transform.scale(self.phone_surf, (self.phone_surf.get_width()*2, self.phone_surf.get_height()*2))

        self.hat = ImageManager.load("assets/images/hat.png")
        self.hat = pygame.transform.scale(self.hat, (self.hat.get_width()*2, self.hat.get_height()*2))

        self.infinite_ammo = False

    def god_mode(self):
        self.upgrades = c.UPGRADES
        self.infinite_ammo = True

    def stop_taking_damage(self):
        self.animation_state = c.IDLE

    def pick_up_phone(self):
        self.holding_phone = True
        self.since_pick_up = 0

    def put_down_phone(self):
        self.holding_phone = False

    def get_hurt(self, direction=None):
        if self.since_damage < 1.25 or self.dead:
            return
        self.hurt_sound.play()
        self.since_damage = 0
        self.animation_state = c.TAKING_DAMAGE
        if self.last_lr_direction == c.RIGHT:
            self.sprite.start_animation("TakeDamageRight")
        else:
            self.sprite.start_animation("TakeDamageLeft")

        self.velocity = direction*500
        Camera.shake(50, direction.get_position())
        self.health -= 1

    def update(self, dt, events):

        self.since_damage += dt
        if self.holding_phone:
            self.since_pick_up += dt

        self.update_gun(dt, events)

        if self.rolling:
            if self.since_roll_finish != 0:
                self.since_roll_finish = 0
        else:
            self.since_roll_finish += dt

        self.process_inputs(dt, events)
        self.sprite.set_position(self.position.get_position())
        self.sprite.update(dt, events)
        mpos = Camera.screen_to_world(pygame.mouse.get_pos())
        Camera.target = self.position.copy() * 0.8 + mpos * 0.2

        if self.health <= 0:
            if not self.dead:
                self.die()

        if self.position.x < -c.ARENA_WIDTH//2 + self.radius:
            self.position.x = -c.ARENA_WIDTH//2 + self.radius
        if self.position.y < -c.ARENA_HEIGHT//2:
            self.position.y = -c.ARENA_HEIGHT//2
        if self.position.x > c.ARENA_WIDTH//2 - self.radius:
            self.position.x = c.ARENA_WIDTH//2 - self.radius
        if self.position.y > c.ARENA_HEIGHT//2 - self.radius*2:
            self.position.y = c.ARENA_HEIGHT//2 - self.radius*2

        if (self.position - self.frame.phone.position).magnitude() < self.frame.phone.radius + self.radius:
            dir = self.position - self.frame.phone.position
            dir.scale_to(self.frame.phone.radius + self.radius)
            self.position = self.frame.phone.position + dir

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_e:
                    if self.dead or self.frame.delivery.blocking():
                        continue
                    self.check_phone_pickup()

        if self.infinite_ammo:
            self.ammo = 999

    def check_phone_pickup(self):
        if not self.holding_phone:
            if self.frame.phone.in_pickup_range(self):
                self.frame.phone.pick_up()
                self.pick_up_phone()
        else:
            self.put_down_phone()
            self.frame.phone.hang_up()

    def die(self):
        self.dead = True
        self.frame.player_died()
        self.put_down_phone()
        self.frame.phone.hang_up()

    def process_inputs(self, dt, events):
        direction = Pose((0, 0))
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_w]:
            direction += Pose((0, -1))
        if pressed[pygame.K_s]:
            direction += Pose((0, 1))
        if pressed[pygame.K_a]:
            direction += Pose((-1, 0))
        if pressed[pygame.K_d]:
            direction += Pose((1, 0))

        old_state = self.animation_state

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if not self.rolling and not self.dead and not self.since_damage < 0.25 and not self.holding_phone and not self.frame.delivery.blocking():
                        self.roll(direction)

        if self.holding_phone or self.dead or self.frame.delivery.blocking():
            direction = Pose((0, 0))

        if self.rolling or self.animation_state == c.TAKING_DAMAGE:
            pass
        else:
            if direction.magnitude() > 0:
                direction.scale_to(1)
                self.velocity += direction * dt * 7500
                self.animation_state = c.WALKING
            else:
                self.velocity *= 0.0001**dt
            if direction.magnitude() == 0:
                self.animation_state = c.IDLE

            if direction.x > 0:
                self.last_lr_direction = c.RIGHT
            elif direction.x < 0:
                self.last_lr_direction = c.LEFT

        if self.animation_state == c.WALKING:
            clear_time = old_state != c.WALKING
            if direction.y >= 0:
                if self.last_lr_direction == c.RIGHT:
                    self.sprite.start_animation("WalkRight", restart_if_active=False, clear_time=clear_time)
                else:
                    self.sprite.start_animation("WalkLeft", restart_if_active=False, clear_time=clear_time)
            else:
                if self.last_lr_direction == c.RIGHT:
                    self.sprite.start_animation("WalkBackRight", restart_if_active=False, clear_time=clear_time)
                else:
                    self.sprite.start_animation("WalkBackLeft", restart_if_active=False, clear_time=clear_time)
        elif self.animation_state == c.IDLE:
            if self.dead:
                self.sprite.start_animation("Dead", restart_if_active=False)
            elif self.last_lr_direction == c.RIGHT:
                self.sprite.start_animation("IdleRight", restart_if_active=False, clear_time=False)
            else:
                self.sprite.start_animation("IdleLeft", restart_if_active=False, clear_time=False)
        elif self.animation_state == c.TAKING_DAMAGE:
            if self.last_lr_direction == c.RIGHT:
                self.sprite.start_animation("TakeDamageRight", restart_if_active=False)
            else:
                self.sprite.start_animation("TakeDamageLeft", restart_if_active=False)

        if self.velocity.magnitude() > 250 and not self.rolling:
            self.velocity.scale_to(250)

        self.position += self.velocity * dt

    def roll(self, direction):
        self.rolling = True
        self.animation_state = c.ROLLING
        animation = "Rolling"
        self.sprite.start_animation(animation, True, clear_time=True)
        if direction.magnitude() == 0:
            direction.y = 0
            direction.x = 1 if self.last_lr_direction == c.RIGHT else -1
        if direction.magnitude() > 1:
            direction.scale_to(1)
        self.velocity = direction * 360
        Camera.shake(10)
        self.dodge_sound.play()

        if "Deadly Dodge" in self.upgrades and self.ammo > 2:
            damage = 40
            pierce = 1
            if "Beefy Bullets" in self.upgrades:
                damage += 20
            if "Cricket" in self.upgrades:
                damage += 80
            if "Piercing" in self.upgrades:
                pierce += 1
            homing = "Seeking" in self.upgrades
            for angle in [0, 60, 120, 180, 240, 300]:
                position = Pose((20, 0))
                position.rotate_position(angle)
                world_position = position + self.position
                self.frame.bullets.append(
                    Bullet(world_position.get_position(), position.get_position(), damage=damage, pierce=pierce,
                           frame=self.frame, homing=homing, refundable=True))
                self.since_fire = 0
                self.velocity -= position * 2
            self.gunshot_sound.play()
            Camera.shake(10, position.get_position())
            self.ammo -= 2
            self.frame.bullets_fired += 6

    def stop_rolling(self):
        self.rolling = False

        self.animation_state = c.IDLE
        self.sprite.start_animation("IdleRight")
        Camera.shake(10)

        for i in range(12):
            pos = (self.position + Pose((0, 20))).get_position()
            self.frame.particles.append(Poof(pos))

    def draw(self, surface, offset=(0, 0)):
        up = "Back" in self.sprite.active_animation_key

        if up:
            self.draw_gun(surface, offset, behind=True)
        self.sprite.draw(surface, offset)
        if not up:
            self.draw_gun(surface, offset, behind=False)

        if self.holding_phone:
            self.draw_phone(surface, offset)

        # if "Hat" in self.upgrades:
        #     self.draw_hat(surface, offset)

    def draw_hat(self, surface, offset):
        if self.rolling:
            return
        x = self.position.x + offset[0] - self.hat.get_width()//2
        y = self.position.y + offset[1] - 32
        surface.blit(self.hat, (x, y))
        pass

    def draw_phone(self, surface, offset):
        if self.dead:
            return
        xoff = min(-16, -28 + self.since_pick_up*400)
        position = self.position + Pose(offset) + Pose((xoff, 0)) + Pose((-self.phone_surf.get_width()//2, -self.phone_surf.get_height()//2))
        surface.blit(self.phone_surf, (position.get_position()))

    def draw_shadow(self, surface, offset=(0, 0)):
        surface.blit(self.shadow, (self.position.x + offset[0] - self.shadow.get_width()//2,
                                   self.position.y + offset[1] - self.shadow.get_height()//2 + 25))

    def update_gun(self, dt, events):
        mpos = pygame.mouse.get_pos()
        mpos_world = Camera.screen_to_world(mpos)
        direction = mpos_world - self.position
        self.gun_angle = direction.get_angle_of_position()*180/math.pi

        self.since_fire += dt

        buttons = pygame.mouse.get_pressed()
        if buttons[0]:
            if not self.rolling or "Spinning Death" in self.upgrades:
                effective_fire_rate = self.fire_rate
                if "Full Auto" in self.upgrades:
                    effective_fire_rate *= 0.6
                if "Cricket" in self.upgrades:
                    effective_fire_rate *= 3
                if self.since_fire > effective_fire_rate and not self.holding_phone and self.ammo and not self.dead and not self.frame.delivery.blocking():
                    self.fire()

    def fire(self):
        self.gunshot_sound.play()

        self.frame.bullets_fired += 1
        gun_angle = self.gun_angle
        position = Pose((35, 0))
        position.rotate_position(gun_angle)
        gun_offset = Pose((0, 10))
        world_position = position + self.position + gun_offset
        damage = 40
        pierce = 1
        homing = "Seeking" in self.upgrades
        if "Beefy Bullets" in self.upgrades:
            damage += 20
        if "Cricket" in self.upgrades:
            damage += 80
        if "Piercing" in self.upgrades:
            pierce += 1

        position.rotate_position(random.random()*10 - 5)
        self.frame.bullets.append(Bullet(world_position.get_position(), position.get_position(), damage=damage, pierce=pierce, frame=self.frame, homing=homing))
        self.since_fire = 0
        self.velocity -= position*2
        shake_amt = 10
        if "Cricket" in self.upgrades:
            shake_amt = 20
        Camera.shake(shake_amt, position.get_position())
        self.ammo -= 1

        up = "Back" in self.sprite.active_animation_key
        for i in range(1):
            self.frame.particles.append(SparkParticle(world_position.get_position(),(position*2)))

        if "Hell's Shells" in self.upgrades and self.ammo>1:
            self.ammo -= 1
            position.rotate_position(15)
            self.frame.bullets.append(Bullet(world_position.get_position(), position.get_position(), damage=damage, pierce=pierce, frame=self.frame, homing=homing))
            position.rotate_position(-30)
            self.frame.bullets.append(Bullet(world_position.get_position(), position.get_position(), damage=damage, pierce=pierce, frame=self.frame, homing=homing))
            self.frame.bullets_fired += 2

        if self.ammo < 0:
            self.ammo = 0

    def draw_gun(self, surface, offset=(0, 0), behind=False):
        if (self.rolling and not "Spinning Death" in self.upgrades) or self.holding_phone or self.dead:
            return
        flipped = self.gun_image
        is_flipped = False
        gun_angle = self.gun_angle
        if self.gun_angle > 90 or self.gun_angle < -90:
            flipped = pygame.transform.flip(self.gun_image,1,0)
            is_flipped = True
            gun_angle += 180
        rotated = pygame.transform.rotate(flipped, gun_angle)

        position = Pose((min(13, -10+self.since_fire*200), 0))

        position.rotate_position(self.gun_angle)
        yoff = 10
        if behind:
            yoff = 10
        position += self.position + Pose(offset) - Pose((rotated.get_width()//2, rotated.get_height()//2 - yoff))

        position = position.get_position()
        surface.blit(rotated, position)

    def camera_target(self):
        mpos = pygame.mouse.get_pos()
        mpos_world = Camera.screen_to_world(mpos)

        weight = 0.25
        if self.holding_phone:
            weight = 0
        return (mpos_world*weight + self.position*(1-weight)).get_position()