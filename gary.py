import random
import time

import pygame

from image_manager import ImageManager
import constants as c


class Gary:

    def __init__(self, frame):
        self.frame = frame
        self.gary_surf = ImageManager.load("assets/images/gary.png")
        self.showing = 0
        self.target = 0

        self.dialog_font = pygame.font.Font("assets/fonts/RPGSystem.ttf", 26)
        self.letters = {letter: self.dialog_font.render(letter, 1, (255, 255, 255)) for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- "}
        self.red_letters = {letter: self.dialog_font.render(letter, 1, (0, 255, 120)) for letter in
                        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- "}

        self.back = pygame.Surface((c.WINDOW_WIDTH, 150))
        self.back.fill((0, 0, 0))
        self.back.set_alpha(0)

        self.lines = []
        self.since_start_line = 0
        self.since_blep = 999

        self.lines = [
        ]

        self.all_lines = [
            [f"Thanks for calling {c.COMPANY_NAME}! Please hold.",
             ],
            ["Sorry for the wait! I'm Gary, and I'll be your customer service representative this evening.",
             "How can I help you today?",
             "...",
             "You're |trapped| |in| |a| |warehouse|, with |dwindling| |supplies|, during a |zombie| |outbreak|?",
             "Hoo, boy. We've certainly all been there.",
             "I'll get a rush delivery lined up for you right away.",
             "Let me put you on hold for a moment while I get started on the paperwork.",
             "Oh, and watch out for |the| |zombies|.",
             ],
            ["Hello again! Just wanted to make sure I had everything correct.",
             "Oh, and by the way, you can |pause| |our| |conversation| at any time by |pressing| |E|.",
             "About that rush order... could I interest you in a special promotional offer?",
             "...",
             "No? You just want the ammunition and equipment as soon as possible? Okey-dokey.",
             "We'll send someone out right away. I'll put you on hold until we can confirm receipt."],
            ["Eyes up... your delivery is inbound!"],
        ]

        self.hold_times = list(c.HOLD_TIMES)
        self.spacebar = ImageManager.load("assets/images/spacebar.png")
        self.lines_read = 0

    def update(self, dt, events):
        self.since_start_line += dt
        self.since_blep += dt
        if self.target > self.showing:
            self.showing += dt * 3
            if self.showing > self.target:
                self.showing = self.target
        elif self.target < self.showing:
            self.showing -= dt*5
            if self.showing < self.target:
                self.showing = self.target

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.target == 1 and self.ready_for_next_line():
                        self.next_line()

    def get_next_lines(self):
        if len(self.all_lines):
            self.add_dialog(self.all_lines.pop(0))

    def restart_line(self):
        self.since_start_line = 0
        if not self.lines or self.lines[0] not in c.DISCONNECT_LINES:
            self.lines = [random.choice(c.DISCONNECT_LINES)] + (self.lines if self.lines else [])

    def draw(self, surface, offset=(0, 0)):

        self.back.set_alpha(self.showing*160)
        surface.blit(self.back, (0, c.WINDOW_HEIGHT - self.back.get_height()))

        cps = c.CPS
        chars_showing = self.since_start_line * cps
        text = self.current_line()
        words = text.split() if text else []
        max_width = 400
        x0 = 300
        y0 = 480
        x = x0
        y = y0
        drawn = 0
        for word in words:
            width = sum([self.letters[letter].get_width() for letter in word])
            if x + width > x0 + max_width:
                x = x0
                y += 26
            red = False
            for letter in word:
                if letter == "|":
                    red = True
                    continue
                self.letters[letter].set_alpha(255 * self.showing)
                if not red:
                    surface.blit(self.letters[letter], (x, y))
                else:
                    surface.blit(self.red_letters[letter], (x, y))
                drawn += 1
                x += self.letters[letter].get_width()
                if drawn >= chars_showing:
                    break
            if drawn >= chars_showing:
                break
            x += self.letters[" "].get_width()
            drawn += 1

        surf = self.spacebar
        x = c.WINDOW_WIDTH - surf.get_width() - 25
        y = c.WINDOW_HEIGHT - surf.get_height() - 25
        if self.ready_for_next_line() and time.time()%1 < 0.75:
            surface.blit(surf, (x, y))

        x = -self.gary_surf.get_width() + self.gary_surf.get_width()*self.showing**0.5
        y = c.WINDOW_HEIGHT - self.gary_surf.get_height()
        surface.blit(self.gary_surf, (x, y))

    def current_line(self):
        if not self.lines:
            return None
        return self.lines[0]

    def next_line(self):
        if len(self.lines):
            self.lines.pop(0)
            self.since_start_line = 0
        if not self.lines:
            self.target = 0
            self.next_wave()

    def next_wave(self):
        self.frame.phone.hang_up()
        self.frame.player.put_down_phone()
        if self.hold_times:
            self.frame.phone.start_hold(self.hold_times.pop(0))
        self.lines_read +=1
        if self.lines_read == 2:
            self.frame.spawn_intensity += 1

    def ready_for_next_line(self):
        cps = c.CPS
        chars_showing = self.since_start_line * cps
        current_line = self.current_line()
        if current_line and chars_showing > len(current_line):
            return True

    def blocking(self):
        return self.showing != 0

    def add_dialog(self, lines):
        self.lines += lines
        if not self.target == 1:
            self.target = 1
            self.since_start_line = 0