import random

import pygame
import constants as c
from camera import Camera
from image_manager import ImageManager

from Button import Button


class DeliveryMenu:

    def __init__(self, frame):
        self.background = pygame.Surface((c.WINDOW_WIDTH - 100, c.WINDOW_HEIGHT - 100))
        self.background.fill((0, 0, 0))
        self.background.set_alpha(148)


        self.big_font = pygame.font.Font("assets/fonts/RPGSystem.ttf", 80)
        self.medium_font = pygame.font.Font("assets/fonts/RPGSystem.ttf", 36)
        self.small_font = pygame.font.Font("assets/fonts/RPGSystem.ttf", 17)


        self.lowered = 0
        self.target = 0
        self.frame = frame

        self.header = self.big_font.render("DELIVERY", 0, (255, 255, 255))
        self.subheader = self.medium_font.render("Choose two", 0, (255, 255, 255))
        self.art = ImageManager.load("assets/images/delivery_art.png")



        bullet = ImageManager.load("assets/images/ammo.png")
        self.bullet_image = bullet#pygame.transform.scale(bullet, (bullet.get_width()*2, bullet.get_height()*2))
        heart = ImageManager.load("assets/images/heart_icon.png")
        self.heart_image = heart#pygame.transform.scale(heart, (heart.get_width()*2, heart.get_height()*2))
        self.upgrade_image = ImageManager.load("assets/images/upgrade_icon.png")
        #self.upgrade_image = pygame.transform.scale(upgrade, (upgrade.get_width()*2, upgrade.get_height()*2))

        self.starting_buttons = [self.make_delivery_button("Health"), self.make_delivery_button("Ammo")]
        self.upgrade_types = list(c.UPGRADES)
        self.buttons = []
        self.upgrade_quota = 2

    def lower(self):
        self.target = 1
        self.buttons = self.starting_buttons.copy()
        used = []
        for i in range(2):
            if self.upgrade_types and len(self.upgrade_types) > len(used):
                valid = self.upgrade_types.copy()
                for item in used:
                    if item in valid:
                        valid.remove(item)
                utype = random.choice(valid)
                self.buttons.append(self.make_delivery_button(utype))
                used.append(utype)
        self.upgrade_quota = 2
        for button in self.buttons:
            button.enable()

    def draw_buttons(self, surface, offset):
        x = 285 + 100
        y = 260 + offset[1] + 45
        x0 = x
        for i, button in enumerate(self.buttons):
            button.x = x
            button.y = y
            button.draw(surface)
            if x == x0:
                x += 220
            else:
                x = x0
                y += 115


    def raise_up(self):
        self.target = 0

    def blocking(self):
        return self.lowered > 0

    def make_delivery_button(self, upgrade):
        if upgrade == "Health":
            header = "Health"
            description = "Fully replenish health"
            icon = self.heart_image
        elif upgrade == "Ammo":
            header = "Ammo"
            description = "Fully replenish ammo"
            icon = self.bullet_image
        else:
            header = "Upgrade"
            index = c.UPGRADES.index(upgrade)
            description = f"{upgrade.upper()}: {c.UPGRADE_DESCRIPTIONS[index]}"
            icon = self.upgrade_image
        surf = pygame.Surface((200, 90)).convert_alpha()
        surf.fill((0, 0, 0, 0))
        color = surf.copy()
        color.set_alpha(50)
        color.fill((100, 100, 100))
        surf.blit(color, (0, 0))
        header = self.medium_font.render(header, 0, (255, 255, 255))
        surf.blit(header, (50, 12))
        description_words = [self.small_font.render(word, 0, (255, 255, 255)) for word in description.split()]
        surf.blit(icon, (5, surf.get_height()//2 - icon.get_height()//2))
        x0 = 53
        y = 45
        x = x0
        while description_words:
            if x + description_words[0].get_width() > surf.get_width() - 7:
                x = x0
                y += 16
                continue
            word = description_words.pop(0)
            surf.blit(word, (x, y))
            x += word.get_width() + 8

        shade = surf.copy()
        shade.fill((0, 0, 0))
        shade.set_alpha(160)
        disabled_surf = surf.copy()
        disabled_surf.blit(shade, (0, 0))

        shade.fill((255, 255, 255))
        shade.set_alpha(160)
        click_surf = surf.copy()
        click_surf.blit(shade, (0, 0))

        shade.fill((255, 255, 255))
        shade.set_alpha(50)
        hover_surf = surf.copy()
        hover_surf.blit(shade, (0, 0))

        button = Button(surf, (0, 0), grow_percent=10, on_click=self.get_upgrade, on_click_args=(upgrade,), disabled_surf=disabled_surf, pulse=False, click_surf=click_surf, hover_surf=hover_surf)
        button.upgrade_type = upgrade
        return button

    def get_upgrade(self, upgrade_type):
        Camera.shake(10)
        if upgrade_type in self.upgrade_types:
            self.upgrade_types.remove(upgrade_type)
        for button in self.buttons:
            if button.upgrade_type == upgrade_type:
                button.disable()
        if upgrade_type == "Ammo":
            self.frame.player.ammo = self.frame.player.max_ammo
        elif upgrade_type == "Health":
            self.frame.player.health = self.frame.player.max_health
        else:
            self.frame.player.upgrades.append(upgrade_type)
            if upgrade_type=="Big Pockets":
                self.frame.player.max_ammo *= 1.5
                self.frame.player.max_ammo = int(self.frame.player.max_ammo)
        self.upgrade_quota -= 1
        if self.upgrade_quota <= 0:
            for item in self.buttons:
                item.disable()
            self.raise_up()


    def draw(self, surface, offset=(0, 0)):
        if self.lowered == 0:
            return
        yoff = -c.WINDOW_HEIGHT + c.WINDOW_HEIGHT*(1 - (1 - self.lowered)**2)

        surface.blit(self.background, (50, 50+yoff))
        surface.blit(self.header, (c.WINDOW_WIDTH//2 - self.header.get_width()//2, 100 + yoff))
        surface.blit(self.subheader, (c.WINDOW_WIDTH//2 - self.subheader.get_width()//2, 166+yoff))
        surface.blit(self.art, (100, 235+yoff))

        self.draw_buttons(surface, (0, yoff))

    def update(self, dt, events):
        speed = 5
        if self.lowered < self.target:
            self.lowered = min(self.target, self.lowered + speed*dt)
        elif self.lowered > self.target:
            self.lowered = max(self.target, self.lowered - speed*dt)
        for button in self.buttons:
            button.update(dt, events)