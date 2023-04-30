#!/usr/bin/env python

#   Outside libraries
import pygame

#   Python libraries
import time
import sys
from image_manager import ImageManager

class Animation(object):
    """
    Represents a single animation from a sprite sheet.
    """

    def __init__(self, surface, sheet_size=(1, 1), frame_count=1, rect=None,
                 reverse_x=False, reverse_y=False, reverse_animation=False, colorkey=None, scale=1.0, start_frame=0, time_scaling = 1):
        """
        Initializes an Animation.

        surface: pygame surface to pull the sprite sheet from
        sheet_size (default (1,1)): dimensions of sprite sheet in frames as a tuple (x, y)
        frame_count (default 1): number of total frames in the sheet
        rect (default None): a subset of the passed surface to sample as a four-length tuple (X, Y, width, height) or
            pygame Rect. X and Y are the pixel coordinates of the rectangle's top left corner, and width and height
            are the width and height of the rectangle in pixels. Useful for pulling a smaller section of a large sheet.
        """

        #   Save off needed input arguments
        self.surface = surface
        self.reverse_x = reverse_x
        self.reverse_y = reverse_y
        self.reverse_animation = reverse_animation
        self.frame_count = frame_count
        self.colorkey = colorkey
        self.scale = scale

        #   Split the sheet into individual surfaces
        self.frames = self.split(surface, sheet_size, frame_count, rect, scale)[start_frame:]
        self.frame_count -= start_frame
        self.time_scaling = time_scaling

    @staticmethod
    def from_path(path, *args, **kwargs):
        """
        Initializes an Animation from a file path rather than a pygame surface.
        """
        return Animation(ImageManager.load(path), *args, **kwargs)

    def split(self, surface, sheet_size, frame_count, rect=None, scale=1.0):
        """
        Breaks up the source image into a list of frames.

        surface: pygame surface to split into frames
        sheet_size: dimensions of sprite sheet or desired area in frames as a tuple (x, y)
        frame_count: number of frames in the sprite sheet or desired area
        rect (default None): pygame Rect to crop the surface to

        returns: A list of frames as individual pygame Surfaces
        """

        #   Determine frame size, in pixels
        rect = (0, 0, surface.get_width(), surface.get_height()) if rect is None else rect
        rect = pygame.Rect(*rect)
        pixel_width, pixel_height = rect.width, rect.height
        frame_width = pixel_width//sheet_size[0]
        frame_height = pixel_height//sheet_size[1]

        #   Make an empty list to store frames in
        frames = []

        #   Repeat for each frame in animation
        frame_x = 0
        frame_y = 0
        for idx in range(frame_count):

            # Crop the frame number into a pygame subsurface
            x_origin = frame_x * frame_width + rect[0]
            y_origin = frame_y * frame_height + rect[1]
            frame_rect = x_origin, y_origin, frame_width, frame_height
            new_frame = surface.subsurface(frame_rect)

            # Apply frame-specific postprocessing
            if self.reverse_x or self.reverse_y:
                new_frame = pygame.transform.flip(new_frame, self.reverse_x, self.reverse_y)
            else:
                new_frame = new_frame.copy()  # We still don't want to reference original surf, like subsurface does
            if self.colorkey:
                new_frame.set_colorkey(self.colorkey)
            if scale != 1.0:
                width = int(new_frame.get_width() * scale)
                height = int(new_frame.get_height() * scale)
                new_frame = pygame.transform.scale(new_frame, (width, height))

            # Add frame to list
            frames.append(new_frame)

            # Iterate through rows and columns
            frame_x += 1
            if frame_x > sheet_size[0]:
                frame_x = 0
                frame_y += 1

        #   Apply animation-level postprocessing
        if self.reverse_animation:
            frames = frames[::-1]

        return frames

    def reverse(self, x_bool, y_bool):
        """
        Reverses the frames of the animation based on which booleans are True.

        xbool: if true, mirrors frames horizontally
        ybool: if true, mirrors frames vertically
        """

        #   Flip each frame
        for idx, frame in enumerate(self.frames):
            self.frames[idx] = pygame.transform.flip(frame, x_bool, y_bool)


class Sprite(pygame.sprite.Sprite):
    """
    Object for rendering a game sprite onto a screen.

    One Sprite can contain several Animations. A single Animation is just a series of frames; the Sprite includes the
    logic for drawing animations to the screen, chaining animation sequences, and cycling through frames appropriately.
    """

    def __init__(self, fps=12, position=(0, 0), scale=1):
        """ Initialization method for sprite object. """
        super().__init__()

        self.animations = {}  # Stores a string key mapped to each Animation object
        self.animation_fps_overrides = {}  # Stores the string key mapped to a number FPS
        self.animation_chain_mapping = {}  # Maps animation keys to the animations that should follow them by default
        self.animation_callbacks = {}  # Maps animation keys to functions to call when they finish - see add_callback
        self.animation_temporary_callbacks = {}  # Maps animation keys to functions to call when they finish next

        self.image = None
        self.rect = None
        self.x, self.y = position

        self.angle = 0

        #   Set initial flags and values
        self.paused = False
        self.paused_at = 0
        self.active_animation_key = None

        #   Set frames per second
        self.fps = fps
        self.now = 0

    def add_animation(self, anim_dict, fps_override=None, loop=False):
        """
        Adds one or more animations to the sprite's animation dictionary.

        anim_dict: Animations to add, as a dictionary with strings as keys and pyracy Animation objects as values.
        fps_override (default None): if provided, will replace the animation speed of the added Animations only.
        loop (default False): whether the animation should loop when played
        """

        for name in anim_dict:
            self.animations[name] = anim_dict[name]
            if fps_override:
                self.animation_fps_overrides[name] = fps_override
            if loop:
                self.chain_animation(name, name)

    def start_animation(self, name, restart_if_active=True, clear_time=True):
        """
        Starts the animation of the chosen name.

        name: string key for the animation added via add_animation.
        force_restart (default True): if True, start the animation from the first frame even if it's already playing
        """

        self.resume()

        # If we're already playing the correct animation, and not forcing a restart, break early
        if not restart_if_active and name == self.active_animation_key:
            return

        # Remember when this animation started. If clear_time is False, caller should adjust self.now appropriately.
        if clear_time:
            self.now = 0

        # Change active animation
        self.active_animation_key = name

    def get_frame_num(self):
        fps = self.fps
        if self.active_animation_key in self.animation_fps_overrides:
            fps = self.animation_fps_overrides[self.active_animation_key]
        frame_time = 1.0/fps
        frame_number = int(self.now/frame_time)
        return frame_number

    def get_image(self):
        """
        Gets the pygame Surface for the sprite's current frame
        """
        active_animation = self.animations[self.active_animation_key]
        frame_time = 1/self.fps
        frame_number = self.get_frame_num()
        if frame_number >= active_animation.frame_count:
            new_animation_exists = self.on_animation_finished(self.active_animation_key)
            if not new_animation_exists:
                # The animation doesn't loop or chain into a different one, so just return the last frame
                self.pause()
                self.now = frame_time * (len(active_animation.frames) - 0.5)
                return active_animation.frames[-1]
            self.now -= frame_time * active_animation.frame_count
            # Yes, this is lazy, but should only break in ways it would have broken anyways with a while loop
            return self.get_image()

        image = active_animation.frames[frame_number]
        if self.angle != 0:
            image = pygame.transform.rotate(image, self.angle)
        return image

    def update_image(self):
        self.image = self.get_image()

    def set_angle(self, angle):
        self.angle = angle  # degrees CCW from due right

    def draw(self, surface, offset=(0, 0)):
        """
        Draws the current frame onto a surface. Note: this object inherits from pygame.sprite.Sprite, so you can also
        add it to a sprite group which will handle drawing for you.

        surface: surface to draw the Sprite onto
        offset (default (0, 0)): x, y tuple of offsets to add to the Sprite's position before drawing
        """

        #   Raise an error if the active animation isn't in animations
        if self.active_animation_key not in self.animations:
            raise Sprite.InvalidAnimationKeyException(f"Animation key {self.active_animation_key} has not been added.")

        #   Draw the animation on the surface
        if not self.image:
            self.image = self.get_image()
        x = int(self.x - self.image.get_width()/2 + offset[0])
        y = int(self.y - self.image.get_height()/2 + offset[1])
        surface.blit(self.image, (x, y))

    def pause(self):
        """ Pause the active animation. """
        self.paused = True

    def resume(self):
        """ Resume the active animation. """
        self.paused = False

    def update(self, dt, events):
        """ Updates the animation with a time step of dt. """

        time_scaling = self.animations[self.active_animation_key].time_scaling
        if not self.paused:
            self.now += dt*time_scaling

        self.image = self.get_image()
        w = self.image.get_width()
        h = self.image.get_height()
        x = int(self.x - w/2)
        y = int(self.y - h/2)
        self.rect = pygame.Rect(x, y, w, h)

    def set_position(self, pos):
        """ Sets the position of the sprite on the screen. """
        self.x, self.y = pos

    def add_callback(self, animation_key, callback, args=None, kwargs=None, temporary=False):
        """
        Adds a callback to be called when the specified animation finishes. For instance, you can schedule a cleanup
        function to occur when your enemy's dying animation has finished.

        animation_key: the string key for the desired animation, as used in add_animation
        callback: a reference to the function to call
        args (default None): a list of arguments to provide to the function when it is called
        kwargs (default None): a dictionary of keyword arguments to provide to the function when it is called
        temporary (default False): if true, the callback will only be called once: the next time the animation finishes.
            If false, it will call the callback every time that animation finishes or loops.
        """
        args = args if args else ()
        kwargs = kwargs if kwargs else {}
        if temporary:
            callback_dict = self.animation_temporary_callbacks
        else:
            callback_dict = self.animation_callbacks
        if animation_key not in callback_dict:
            callback_dict[animation_key] = []
        callback_dict[animation_key].append((callback, args, kwargs))

    def chain_animation(self, previous_animation, next_animation):
        """
        Connects two animations together such that when one finishes it will start the next one by default.

        previous_animation: string key of first animation
        next_animation: string key of animation to play when previous_animation finishes
        """
        self.animation_chain_mapping[previous_animation] = next_animation

    def on_animation_finished(self, animation_key):
        """
        Handles callbacks and chaining when an animation finishes or loops.

        animation_key: string key of animation that just finished
        returns: True if a new animation was started, or False otherwise
        """
        self.run_callbacks(animation_key)
        next_animation = self.get_next_animation(animation_key)
        if next_animation:
            self.start_animation(next_animation, restart_if_active=True, clear_time=False)
            return True
        return False

    def run_callbacks(self, animation_key):
        """
        Handles callbacks when an animation finishes. Also clears the temporary callbacks after running.

        animation_key: string key of animation that just finished
        """

        # Temporary animation callbacks
        if animation_key in self.animation_temporary_callbacks:
            for callback, args, kwargs in self.animation_temporary_callbacks[animation_key]:
                callback(*args, **kwargs)
            del self.animation_temporary_callbacks[animation_key]  # Temporary callbacks should only be run once

        # Repeat animation callbacks
        if animation_key in self.animation_callbacks:
            for callback, args, kwargs in self.animation_callbacks[animation_key]:
                callback(*args, **kwargs)


    def get_next_animation(self, animation_key):
        """
        Returns the key of the animation that should follow the specified one, or None if none exists.
        """
        if animation_key in self.animation_chain_mapping:
            return self.animation_chain_mapping[animation_key]
        return None

    class InvalidAnimationKeyException(IndexError):
        pass


if __name__ == '__main__':
    #   Example script that draws a hydra on the screen.

    class Counter:
        """
        This is to demonstrate the Sprite callback feature. We'll have it count up every time the sprite animation
        loops.
        """

        def __init__(self):
            self.value = 0
            self.font = pygame.font.SysFont("sans serif", 16, False)

        def count(self):
            self.value += 1

        def draw(self, surface):
            pygame.font.init()
            text = self.font.render(f"{self.value}", False, (255, 255, 255))
            surface.blit(text,
                         (surface.get_width() - text.get_width() - 2,
                          surface.get_height() - text.get_height() - 2))

    pygame.init()
    screen = pygame.display.set_mode((220, 150))
    pygame.display.set_caption("Sprite Tools Test")

    #   This creates the sprite object and adds an idle animation to it
    a = Animation.from_path("TestSprite.png", sheet_size=(4, 1), frame_count=4, colorkey=(255, 0, 255))
    c = Counter()
    b = Sprite(fps=9, position=(110, 75))
    b.add_animation({"Idle": a}, loop=True)
    b.start_animation("Idle")
    b.add_callback("Idle", c.count)

    then = time.time()
    time.sleep(0.01)
    while True:

        #   Calculate time step
        now = time.time()
        dt = now - then
        then = now

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        #   Blank screen
        screen.fill((50, 50, 50))

        #   This draws the current frame on the screen
        b.update(dt, events)
        b.draw(screen)
        c.draw(screen)

        pygame.display.flip()
