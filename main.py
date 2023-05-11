import pygame

import constants as c
import frame as f
import sys
from sound_manager import SoundManager
from image_manager import ImageManager
import asyncio

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.set_num_channels(12)
        SoundManager.init()
        ImageManager.init()
        self.screen = pygame.display.set_mode(c.WINDOW_SIZE)
        pygame.display.set_caption(c.CAPTION)
        self.clock = pygame.time.Clock()
        self.windowed = False
        self.clicked = False
        asyncio.run(self.main())

    async def main(self):
        current_frame = f.GameFrame(self)
        current_frame.load()
        self.clock.tick(60)

        try:
            pygame.mouse.set_cursor((13,13),ImageManager.load("assets/images/crosshairs.png"))
        except:
            pass

        while True:
            dt, events = self.get_events()
            await asyncio.sleep(0)
            if dt == 0:
                dt = 1/100000
            pygame.display.set_caption(f"{c.CAPTION} ({int(1/dt)} FPS)")
            if dt > 0.05:
                dt = 0.05
            current_frame.update(dt, events)
            current_frame.draw(self.screen, (0, 0))
            pygame.display.flip()

            if current_frame.done:
                current_frame = current_frame.next_frame()
                current_frame.load()

    def get_events(self):
        dt = self.clock.tick(c.FRAMERATE)/1000

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F4:
                    pygame.display.toggle_fullscreen()

        pressed = pygame.mouse.get_pressed()
        try:
            if pressed[0] and not self.clicked:
                self.clicked = True
                pygame.mouse.set_cursor((12, 12), ImageManager.load("assets/images/small_cursor.png"))
            elif not pressed[0] and self.clicked:
                self.clicked = False
                pygame.mouse.set_cursor((12, 12), ImageManager.load("assets/images/crosshairs.png"))
        except:
            pass

        return dt, events


if __name__=="__main__":
    Game()
