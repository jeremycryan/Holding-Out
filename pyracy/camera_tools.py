#!/usr/bin/env python

#   outside libraries
import pygame

#   python libraries
import time
import random

class Camera(object):
    """ Camerawork class for pygame. This object supports camera effects like
    slowdowns and zooms. """

    def __init__(self, output_display):
        """ Init function for camera class """

        self.speed = 1.0    #   Proportional speed of capture
        self.zoom = 1.0     #   Amount the image is enlarged by camera object
        self.target_zoom = 1.0      #   Amount camera is trying to zoom to
        self.output_display = output_display

        #   Determine dimensions of output surface
        self.output_width = output_display.get_width()
        self.output_height = output_display.get_height()

        #   Width and height of the screen segment you're zooming into
        self.zoom_width = self.output_width
        self.zoom_height = self.output_height

        #   Position of the camera center on the screen, and panning attributes
        x_pos = int(self.output_width/2)
        y_pos = int(self.output_height/2)
        self.pos = (x_pos, y_pos)
        self.target_pos = self.pos

        #   PID terms for smooth camera pan
        self.pan_p = 10.0
        self.pan_i = 2.0
        self.pan_d = -0.2

        #   PID terms for smooth zooming
        self.zoom_p = 8.0
        self.zoom_i = 1.0
        self.zoom_d = -0.2

        #   All PID constants
        self.pids = {'x': (self.pan_p, self.pan_i, self.pan_d),
            'y': (self.pan_p, self.pan_i, self.pan_d),
            'zoom': (self.zoom_p, self.zoom_i, self.zoom_d)}

        self.integral = {'x': 0, 'y': 0, 'zoom': 0}
        self.derivative = {'x': 0, 'y': 0, 'zoom': 0}


    def set_pan_pid(self, p, i, d):
        """ Modify default pid constants for camera pan """

        #   Update constants
        self.pan_p = p
        self.pan_i = i
        self.pan_d = d

        #   Update pids dictionary
        self.pids['x'] = (p, i, d)
        self.pidx['y'] = (p, i, d)

    def set_zoom_pid(self, p, i, d):
        """ Modify default pid constants for camera zoom """

        #   Update constants
        self.zoom_p = p
        self.zoom_i = i
        self.zoom_d = d

        #   Update pids dictionary
        self.pids['zoom'] = (p, i, d)

    def time_step(self, dt):
        """ Applies any slow or speed to the camera object by modifying the
        time step appropriately.

        dt: time step since last call to update animations and effects, seconds

        returns new_dt: modified time step to pass into update calls, seconds"""

        #   Update camera according to actual time step
        self.update_zoom(dt)
        self.update_pan(dt)

        #   Return modified time step
        new_dt = dt * self.speed
        return new_dt


    def set_speed(self, speed):
        """ Sets the capture speed of the camera. 1.0 is normal speed, and
        higher speeds will make animations and particle effects move faster. """

        #   Change capture speed
        self.speed = speed


    def zoom_to(self, zoom_amt):
        """ Applies a zoom to the specified amount.

        zoom_amt: float specifying enlargement ratio; 1.0 is no zoom """

        #   Apply zoom
        self.zoom = zoom_amt

        #   Change the zoom rectangle width and height
        self.zoom_width = self.output_width / zoom_amt
        self.zoom_height = self.output_height / zoom_amt

    def set_center(self, pos):
        """ Sets the position of the camera's center of focus. """

        self.pos = pos

    def set_target_center(self, pos):
        """ Sets the position the camera will try to pan to. """

        self.target_pos = pos
        self.integral['x'] = 0
        self.integral['y'] = 0

    def update_pan(self, dt):
        """ Updates the camera's pan, using a PID controller defined by
        constants on the camera object. """

        #   Gather current and target position
        current_x, current_y = self.pos
        target_x, target_y = self.target_pos

        #   Determine new values
        new_x = self.apply_pid(dt, current_x, target_x, 'x')
        new_y = self.apply_pid(dt, current_y, target_y, 'y')

        #   Update camera position
        self.pos = (new_x, new_y)


    def set_target_zoom(self, zoom):
        """ Sets the camera's target zoom level. """

        self.target_zoom = zoom
        self.integral['zoom'] = 0

    def update_zoom(self, dt):
        """ Updates the camera's amount of zoom """

        #   Determine new zoom value
        new_zoom = self.apply_pid(dt, self.zoom, self.target_zoom, 'zoom')

        self.zoom_to(new_zoom)

        # zoom_amt = self.zoom * self.max_zoom_speed * dt
        # zoom = self.zoom
        #
        # #   If you need to zoom out, subtract from zoom
        # if self.zoom > self.target_zoom:
        #     zoom = max(self.target_zoom, self.zoom - zoom_amt)
        #
        # #   If you need to zoom in, add to zoom
        # elif self.zoom < self.target_zoom:
        #     zoom = min(self.target_zoom, self.zoom + zoom_amt)
        #
        # #   Apply zoom
        # self.zoom_to(zoom)


    def apply_pid(self, dt, current_val, target_val, axis):
        """ Returns a new current value based on PID constants and time step.

        dt: timestep in seconds
        current_val: current value of x or y position
        target_val: target value for x or y position
        axis: string either 'x' or 'y'

        """

        p, i, d = self.pids[axis]

        #   Term to be multiplied by proportion constant
        p_val = target_val - current_val

        #   Term to be multiplied by integral constant
        self.integral[axis] += p_val * dt
        i_val = self.integral[axis]

        #   Term to be multiplied by derivative constant
        d_val = self.derivative[axis]

        #   Calculate change in position
        delta = p*p_val + i*i_val + d*d_val

        #   Update derivative
        self.derivative[axis] = delta

        #   Return new value
        return current_val + delta*dt


    def capture(self, surface):
        """ Captures the surface and blits it onto the screen, applying any
        effects or zooms. """

        #   Create a surface the size of the zoom rectangle, and blit the
        #   captured surface onto it in the right spot.
        zoom_surf = pygame.Surface((self.zoom_width, self.zoom_height))

        #   Blit zoomed surface to the zoom surface
        x_blit = int(self.zoom_width/2 - self.pos[0])
        y_blit = int(self.zoom_height/2 - self.pos[1])
        zoom_surf.blit(surface, (x_blit, y_blit))

        #   Scale the zoom surface to the same size as the output
        zoom_surf = pygame.transform.scale(zoom_surf,
            (self.output_width, self.output_height))

        #   Draw the screen onto the output
        self.output_display.blit(zoom_surf, (0, 0))


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Camera Tools Test")
    temp_screen = pygame.Surface((400, 400))
    camera = Camera(screen)

    timer = 0
    then = time.time()
    time.sleep(0.01)
    while True:
        now = time.time()
        dt = now - then
        then = now

        dt = camera.time_step(dt)

        temp_screen.fill((75, 75, 75))

        timer += dt

        #   Draw a checkerboard on the screen for reference
        poses = [0, 2, 4, 6, 9, 11, 13, 15,
                16, 18, 20, 22, 25, 27, 29, 31]
        poses += [p + 32 for p in poses]
        for p in poses:
            x = p%8 * 50
            y = int(p/8) * 50
            sq = pygame.Surface((50, 50))
            sq.fill((150, 150, 150))
            temp_screen.blit(sq, (x, y))

        #   Change zoom and pan to random values every two seconds
        if timer > 2:
            timer -= 2
            camera.set_target_zoom((random.random() + 0.25))
            camera.set_target_center((random.random() * 400,
                random.random() * 400))

        camera.capture(temp_screen)
        pygame.display.flip()
