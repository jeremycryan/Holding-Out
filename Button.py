import pygame
import sys
import random
import time
import math


class Button:
    def __init__(self,
                 surf,
                 pos,
                 text="",
                 on_click=None,
                 hover_surf=None,
                 click_surf=None,
                 disabled_surf=None,
                 enabled=True,
                 grow_percent=5,
                 pulse=True,
                 on_click_args=None):

        self.x, self.y = pos
        self.width, self.height = surf.get_width(), surf.get_height()
        self.text = text
        self.surf = surf
        self.on_click = on_click
        self.hover_surf = hover_surf
        self.click_surf = click_surf
        self.disabled_surf = disabled_surf
        self.enabled = enabled
        self.clicked = False
        self.grow_percent = grow_percent
        self.scale = 1.0
        self.target_scale = 1.0
        self.pulse = pulse
        if on_click_args==None:
            on_click_args=()
        self.on_click_args = on_click_args

    def click(self):
        if not self.enabled:
            return
        self.clicked = False
        if type(self.on_click) is tuple or type(self.on_click) is list:
            for item in self.on_click:
                item(*self.on_click_args)
        else:
            self.on_click(*self.on_click_args)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def toggle(self):
        self.enabled = not self.enabled

    def is_hovered(self):
        mpos = pygame.mouse.get_pos()
        min_x = self.x - self.width/2
        max_x = self.x + self.width/2
        min_y = self.y - self.height/2
        max_y = self.y + self.height/2
        if min_x < mpos[0] < max_x and min_y < mpos[1] < max_y:
            return True
        return False

    def get_surf(self):
        surf = None
        if not self.enabled and self.disabled_surf is not None:
            surf = self.disabled_surf
        elif self.clicked and self.enabled and self.click_surf is not None:
            surf = self.click_surf
        elif self.is_hovered() and self.enabled and self.hover_surf is not None:
            surf = self.hover_surf
        else:
            surf = self.surf
        if self.scale != 1.0:
            width = int(self.width * self.scale)
            height = int(self.height * self.scale)
            surf = pygame.transform.scale(surf, (width, height))
        return surf

    def draw(self, surface, xoff=0, yoff=0):
        x = self.x - self.width * self.scale/2 + xoff
        y = self.y - self.height * self.scale/2 + yoff
        surface.blit(self.get_surf(), (x, y))

    def update(self, dt, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if self.clicked and self.is_hovered():
                        self.click()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.is_hovered():
                        self.clicked = True
        if self.clicked:
            if not self.is_hovered():
                self.clicked = False

        if self.is_hovered() and self.enabled:
            self.target_scale = 1.0 + self.grow_percent/100
        elif self.pulse and self.enabled:
            self.target_scale = 1.0 + 0.02*math.sin(time.time()*4)
        else:
            self.target_scale = 1.0

        ds = self.target_scale - self.scale
        speed = 25
        if abs(ds) < 0.01:
            self.scale = self.target_scale
            ds = 0
        if ds < 0:
            self.scale = max(self.scale + ds * dt * 20, self.target_scale)
        elif ds > 0:
            self.scale = min(self.scale + ds * dt * 20, self.target_scale)

if __name__ == '__main__':

    class Color:
        def __init__(self):
            self.val = (0, 0, 0)

        def randomize(self):
            self.val = (random.random()*255,
                        random.random()*255,
                        random.random()*255)

    screen = pygame.display.set_mode((800, 600))
    then = time.time()

    button_surf = pygame.image.load("button.png")
    button_hover = pygame.image.load("button_hover.png")
    button_disabled = pygame.image.load("button_disabled.png")
    button_clicked = pygame.image.load("button_clicked.png")

    color = Color()
    button = Button(button_surf,
                    (200, 200),
                    on_click=color.randomize,
                    hover_surf=button_hover,
                    click_surf=button_clicked,
                    disabled_surf=button_disabled)

    while True:
        now = time.time()
        dt = now - then
        then = now
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        button.update(dt, events)

        screen.fill(color.val)
        button.draw(screen)
        pygame.display.flip()
