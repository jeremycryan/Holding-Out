import random
import time

import pygame

from image_manager import ImageManager
import constants as c
from sound_manager import SoundManager


class Gary:

    def __init__(self, frame):
        self.frame = frame
        self.gary_surf = ImageManager.load("assets/images/gary.png")
        self.showing = 0
        self.target = 0

        self.dialog_font = pygame.font.Font("assets/fonts/RPGSystem.ttf", 26)
        self.letters = {letter: self.dialog_font.render(letter, 1, (255, 255, 255)) for letter in "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- ()"}
        self.red_letters = {letter: self.dialog_font.render(letter, 1, (0, 255, 120)) for letter in
                        "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz'.,?!|- ()"}

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
            [f"Thanks for calling {c.COMPANY_NAME}, where you value your time so we don't have to.",
             "Oh, you'd like to request another delivery? Sure, I'll take a look...",
             "Hang on, someone just walked into the office with donuts. I'm going to put you on hold for a second."],
            ["(chewing noises)",
             "...oh, I accidentally turned on the customer line. Sorry sir, a few more moments."],
            ["Delicious! Thanks for waiting.",
             "Say... what is your favorite kind of donut? I like maple bars, but glazed are pretty good as well.",
             "Oh, the delivery? I can send it now, it should be there any moment."],
            ["Delivery arriving now!"],
            [f"Thanks for calling {c.COMPANY_NAME}, we put the 'vice' in 'service.'",
             "You again? You know, it's probably not healthy to be chewing through ammunition this quickly.",
             "Oh. Zombies. I forgot.",
             "Anyway, your order history is unusual enough we might want to run it past someone.",
             "Please hold while I transfer you to sales."],
            ["I forgot... I'm sales!",
             "It's probably fine. Could I get your address one more time?",
             "...",
             "You're going to have to speak up, I can't hear you over the undead horde in the background.",
             "...",
             "Okay, I'll start processing the third delivery. Please hold."],
            ["Hello again. The paperwork is all squared away, and the delivery person is en route.",
             "I'll put you on hold until it gets there."],
            ["Your delivery should be arriving now!"],
            [f"Thanks for calling {c.COMPANY_NAME}, we hold you when no one else will.",
             "Ah, welcome back! Let me guess, ammunition and equipment to fight the rotting armies of the dead?",
             "You know, sales people really have an unfairly poor reputation.",
             "I once met a produce salesman who was a great fellow. A truly stand-up guy.",
             "Anyway, this guy would bring an apple into work every day, the kind with a sticker on it?",
             "And every day, without fail, he'd eat the sticker.",
             "Consistently.",
             "The first time, I thought he just missed it. Maybe he was distracted. Happens to the best of us.",
             "The second time, it was concerning. Usually people try to avoid eating stickers.",
             "The third time... I could only assume the guy was just very dense.",
             "That was ten years ago, and after all these years, I think I finally understand him.",
             "He just liked the taste of stickers.",
             "Anyway, your package should be arriving any second now."],
            ["That's the whole game! You win!",
             "'Holding Out' was made in 48 hours for the Ludum Dare 53 Compo.",
             "This game was made with Python and PyGame. The font is RPG System by Axel Lymphos.",
             "If you want to stick around, I've given you every upgrade and infinite ammo.",
             "Thanks for playing!",]
        ]

        self.hold_times = list(c.HOLD_TIMES)
        self.spacebar = ImageManager.load("assets/images/spacebar.png")
        self.lines_read = 0

        self.bip = SoundManager.load("assets/sound/bip.ogg")

        self.skip_to = 0
        self.skipped = False

        self.gary_talk = SoundManager.load("assets/sound/gary_talk.ogg")
        self.through = True

    def update(self, dt, events):
        if not self.skipped:
            self.skipped = True
            for i in range(self.skip_to):
                self.all_lines.pop(0)
                self.next_wave()
                self.frame.delivery.raise_up()

        self.since_start_line += dt
        self.since_blep += dt
        if self.since_blep > 0.16 and self.showing and not self.ready_for_next_line() and self.showing == 1:
            self.gary_talk.play()
            self.since_blep = 0

        if self.target > self.showing:
            self.showing += dt * 3
            if self.showing > self.target:
                self.showing = self.target
        elif self.target < self.showing:
            self.showing -= dt*5
            if self.showing < self.target:
                self.showing = self.target

        for event in events[:]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.target == 1 and self.ready_for_next_line():
                        self.next_line()
                        events.remove(event)
                        self.bip.play()

    def get_next_lines(self):
        if len(self.all_lines):
            self.add_dialog(self.all_lines.pop(0))
        if self.lines_read == 13:
            for enemy in self.frame.enemies:
                enemy.die()

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
        if self.lines_read == 4:
            self.frame.get_delivery()
        if self.lines_read == 6:
            self.frame.spawn_intensity += 1
        if self.lines_read == 8:
            self.frame.get_delivery()
        if self.lines_read == 12:
            self.frame.get_delivery()
            self.frame.spawn_intensity += 1
            self.frame.since_goomba = 12
        if self.lines_read == 13:
            self.frame.get_delivery()
            self.frame.spawn_intensity += 1
        if self.lines_read == 14:
            self.frame.player.god_mode()
            self.frame.spawn_intensity += 1

    def ready_for_next_line(self):
        cps = c.CPS
        chars_showing = self.since_start_line * cps
        current_line = self.current_line()
        if current_line:
            current_line= current_line.replace("|","")
        if current_line and chars_showing > len(current_line):
            return True

    def blocking(self):
        return self.showing != 0

    def add_dialog(self, lines):
        self.lines += lines
        if not self.target == 1:
            self.target = 1
            self.since_start_line = 0