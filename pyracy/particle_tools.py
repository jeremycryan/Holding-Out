#!/usr/bin/env python

#   Outside libraries
import pygame

#   Python libraries
import random
import time
from math import sin, cos, pi

################################################################################
########################## PARTICLE DEFINITION #################################
################################################################################

class Particle(object):
    """ A single particle from a system, drawn on the screen. """

    def __init__(self, pos = (0, 0), path = "square", width = 10, height = 10,
        color = (255, 255, 255)):
        """ Initialization function for particle """

        #   Type of particle --- either str 'square', 'circle', or an image path
        self.path = path

        #   Initial position of the particle
        self.pos = pos

        #   Some initial values
        self.created_at = time.time()
        self.anim_speed = 1.0   #   Alter this to slow/speed the animation
        self.behaviors = []

        #   Default values that can be modified by particle behaviors
        self.opacity = 1.0
        self.color = color
        #   TODO make width and height variable on image used
        self.width = width     #   Width of particle in pixels
        self.height = height    #   Height pf particle in pixels

        #   Potential parameters:
        #   - Initial position
        #   - Initial velocity
        #   - Acceleration/deceleration
        #   - Curvature in motion
        #   - Initial scale, growth/shrinking
        #   - Initial opacity, fading
        #   - Duration of particle
        #   - Death condition of particle (e.g. at opacity 0 or scale 0)
        #   - Color/value shift
        #   - "Chaos" attribute for each of these... how much variation there
        #       is for each behavior
        #   - Particle shape/source image/physical appearance
        #   - It's sounding increasingly like "ParticleAttribute" should be a
        #       class of its own...

        #   Important attributes:
        #   - Current all of those things
        #   - Time of creation

    def create(self, pos):
        """ Returns a particle instance with the same attributes at a given
        position. """

        #   Instantiate the particle
        particle = Particle(pos, self.path, self.width, self.height, self.color)

        #   Add all of the original particles behaviors
        particle.behaviors = self.behaviors[:]

        #   Initialize behaviors with on apply effects
        for item in particle.behaviors:
            item.on_apply(particle)

        return particle

    def update_particle(self, dt):
        """ Updates the particle based on the amount of time that has passed."""

        #   Calls the update function for each behavior attached to this particle
        for item in self.behaviors:
            item.update(self, dt)

    def apply_behavior(self, behavior):
        """ Applies a particle behavior to the particle. """

        self.behaviors.append(behavior)

    def draw(self, screen):
        """ Draws the particle on the screen at its current position """

        #   Draw method for square particle
        if self.path == "square":
            self.draw_square(screen)
        elif self.path == "circle":
            self.draw_circle(screen)
        else:
            print("Unable to draw particle of type %s." % self.path)

    def draw_square(self, screen):
        """ Draws the particle as a square, centered at the position self.pos"""

        #   Create values for width and height
        w = int(self.width)
        h = int(self.height)
        half_w = 0.5 * w
        half_h = 0.5 * h

        #   Determine position of blit based on width and height
        x = int(self.pos[0] - half_w)
        y = int(self.pos[1] - half_h)
        blit_pos = (x, y)

        #   Create pygame surface
        square = pygame.Surface((w, h))
        square.fill(self.color)
        alpha = int(self.opacity * 255)
        square.set_alpha(alpha)

        #   Blit to screen
        screen.blit(square, (x, y))

    def draw_circle(self, screen):
        """ Draws the particle as a circle, centered at the position self.pos"""

        #   Create values for width and height
        w = int(self.width)
        h = int(self.height)
        half_w = 0.5 * w
        half_h = 0.5 * h

        #   Determine position of blit based on width and height
        x = int(self.pos[0] - half_w)
        y = int(self.pos[1] - half_h)
        blit_pos = (x, y)

        #   Create a surface and draw a circle on it
        trans_color = (0, 255, 0)
        surf = pygame.Surface((w, h))
        surf.fill(trans_color)
        pygame.draw.ellipse(surf, self.color, (0, 0, w, h))
        surf.set_colorkey(trans_color)

        alpha = int(self.opacity * 255)
        if alpha < 0: alpha = 0
        surf.set_alpha(alpha)

        screen.blit(surf, (x, y))


    def on_apply(self, particle):
        """ Applies any immediate alterations to the particle when the effect is
        added. """
        pass


    def update(self):
        """ Updates all of the particles attributes based on the initial
        conditions and elapsed time """
        pass


    def is_active(self):
        """ Returns true if the particle is in a state where it is still visible
        and animated. """

        #   Particle is not useful if it is invisible
        if self.opacity <= 0:
            return False

        #   Particle is not useful if it has zero size
        elif self.width <= 0 or self.height <= 0:
            return False

        #   Otherwise, particle is probably still active
        else:
            return True


class ParticleBehavior(object):
    """ Defines a single behavior of a particle, such as a change in opacity
    over time. """

    def __init__(self, *args, **kwargs):
        """ Init function for particle behavior """
        pass

    def on_apply(self, particle):
        """ Method to occur when the effect is added to a particle """
        pass

    def update(self, particle, dt):
        """ Applies the animation effect to the particle. """
        pass


################################################################################
######################### PARTICLE BEHAVIORS ###################################
################################################################################

class OpacityEffect(ParticleBehavior):
    """ Defines an opacity animation for a particle """


    def __init__(self, init_opacity = 0.8, decay = 0.2):
        """ Initializes the opacity effect.

        init_opacity is the initial opacity of the particle, with 1.0 being
            completely opaque.
        decay is the opacity reduction per second for the particle. """

        #   Initialize the superclass
        super(OpacityEffect, self).__init__(init_opacity = 0.8, decay = 0.2)

        #   Set the parameters of the effect
        self.init_opacity = init_opacity
        self.decay = decay


    def on_apply(self, particle):
        """ Applies any immediate alterations to the particle when the effect is
        added. """

        #   Set the initial opacity
        particle.opacity = self.init_opacity


    def update(self, particle, dt):
        """ Applies the animation effect to the particle.

        particle: the particle object to apply the change
        dt: the time since last update, in seconds """

        #   Modify the particle's opacity basaed on the decay rate
        particle.opacity -= dt * self.decay


class ScaleEffect(ParticleBehavior):
    """ Defines an animation changing the particle's scale """


    def __init__(self, init_scale = 1.0, growth = 0.2):
        """ Initializes the scale effect.

        init_scale: the initial multiplicative scale applied to the particle;
            a scale of 1.0 means it doesn't change size.
        growth: the change in scale in terms of proportion per second. This
            compounds.
        """

        self.init_scale = init_scale
        self.growth = growth


    def on_apply(self, particle):
        """ Applies any immediate alterations to the particle when the effect is
        added. """

        particle.width *= self.init_scale
        particle.height *= self.init_scale


    def update(self, particle, dt):
        """ Applies the animation effect to the particle.

        particle: the particle object to apply the change
        dt: the time since last update, in seconds """

        growth_prop = (1.0 + self.growth) ** dt

        particle.width *= growth_prop
        particle.height *= growth_prop



class LinearMotionEffect(ParticleBehavior):
    """ Defines an animation for a particle moving in a straight line. """


    def __init__(self, direction = 0, init_speed = 50.0, accel = 0):
        """ Initializes the motion effect.

        direction: proportional angle counterclockwise from the positive X axis,
            i.e. 0 is due right, 0.5 is due left, etc
        init_speed: initial speed of the particle's motion in pixels per second
        accel: change to speed, in pixels per second per second. If a negative
            acceleration would reduce the speed to below zero, the speed is
            set to zero instead. """

        #   Initialize the superclass
        super(LinearMotionEffect, self).__init__(direction = direction,
            init_speed = init_speed,
            accel = accel)

        self.direction = direction
        self.init_speed = init_speed
        self.accel = accel
        self.speed = init_speed


    def update(self, particle, dt):
        """ Applies the animation effect to the particle.

        particle: the particle object to apply the change
        dt: the time since last update, in seconds """

        #   Change the particle's position based on the speed. Uses an average
        #   of speeds before and after the tick to help mitigate changes in
        #   behavior at different loop speeds.
        old_speed = self.speed
        new_speed = old_speed + self.accel*dt
        avg_speed = 0.5 * (old_speed + new_speed)
        self.speed = new_speed

        #   Apply position change to x and y positions
        dir_rad = 2 * pi * self.direction
        x_prop, y_prop = cos(dir_rad), sin(dir_rad)
        dx, dy = x_prop * avg_speed * dt, y_prop * avg_speed * dt
        x = particle.pos[0] + dx
        y = particle.pos[1] + dy
        particle.pos = (x, y)



class CircularMotionEffect(ParticleBehavior):
    """ Defines an animation for a particle moving in a circle. """


    def __init__(self, init_freq = 1.0, init_radius = 50.0,
        accel = 0, growth = 0, init_angle = 0):

        """ Initializes the motion effect.

        init_freq: the initial frequency, in Hertz, of the circular motion
        init_radius: the initial radius of the circular motion, in pixels
        accel: acceleration, in Hz/s, of the circular motion
        growth: change in size, in pixels/s/s, of the path's radius
        init_angle: initial angle, as a proportion of a full circle, CCW from
            the positive X """

        #   Initialize the superclass
        super(CircularMotionEffect, self).__init__(init_freq = init_freq,
            init_radius = init_radius,
            accel = accel,
            growth = growth,
            init_angle = init_angle)

        #   Save parameters
        self.freq = init_freq
        self.radius = init_radius
        self.accel = accel
        self.growth = growth
        self.angle = init_angle


    def on_apply(self, particle):
        """ Applies any immediate alterations to the particle when the effect is
        added. """

        particle.circ_mot_angle = self.angle
        particle.circ_mot_rad = self.radius
        particle.circ_mot_freq = self.freq


    def update(self, particle, dt):
        """ Applies the animation effect to the particle.

        particle: the particle object to apply the change
        dt: the time since last update, in seconds """

        #   Save current values
        old_angle = particle.circ_mot_angle
        old_radius = particle.circ_mot_rad
        old_x, old_y = particle.pos

        #   Update values based on time passed
        particle.circ_mot_angle += particle.circ_mot_freq * dt
        particle.circ_mot_freq += self.accel * dt
        particle.circ_mot_rad += self.growth * dt

        #   Determine position of circle center based on old angle and radius
        x_off = -cos(old_angle * 2 * pi) * old_radius
        y_off = -sin(old_angle * 2 * pi) * old_radius
        center_x = old_x + x_off
        center_y = old_y + y_off

        #   Determine new position of particle after time step
        new_x_off = cos(particle.circ_mot_angle * 2 * pi) \
            * particle.circ_mot_rad
        new_y_off = sin(particle.circ_mot_angle * 2 * pi) * \
            particle.circ_mot_rad
        new_x = center_x + new_x_off
        new_y = center_y + new_y_off

        #   Change the particle's position
        particle.pos = (new_x, new_y)



################################################################################
####################### PARTICLE EFFECT DEFINITION #############################
################################################################################



class ParticleEffect(object):
    """ This class manages a 'cloud' of particles. It acts as a container that
    holds one or more particle types and spawn them periodically. It can move
    as a source, but individual particles maintain their individual positions on
    the screen. """

    #TODO this whole class

    def __init__(self, pos = (0, 0), width = 50, height = 50,
        duration = -1):
        """ Init method for particle effect class.

        pos: initial position of particle effect object, measured from center
            of field, in pixels
        width: width of the field that can spawn particles (pixels)
        height: height of the region that can spawn particles (pixels)
        duration: time after which the field will expire --- useful for making
            short bursts"""

        #   Save initial inputs
        self.pos = pos
        self.width = width
        self.height = height
        self.duration = duration
        self.time = 0               #   Time particle effect has been active

        #   List of particle objects managed by this particle effect object
        self.particle_types = []
        self.periods = []
        self.cooldowns = []

        #   List of actual particle instances
        self.particles = []


    def add_particle_type(self, particle, period = 0.2, num = 1):
        """ Adds a particle type for the particle effect object to periodically
        spawn.

        particle: a particle object
        period: the delay between spawning consecutive particles, in seconds
        num: number of instances of the particle type to add """

        #   Repeat num times
        for i in range(num):

            #   Add the particle and period to the list
            self.particle_types.append(particle)
            self.periods.append(period)

            #   These keep track of how long it has been since spawning a
            #   particle of that type
            self.cooldowns.append(0)


    def spawn_particle(self, particle):
        """ Spawns a particle of the chosen type at a random point within the
        field. """

        #   Determine a random position for the particle to spawn
        x_off = int(random.random() * self.width)
        y_off = int(random.random() * self.height)
        half_width = self.width * 0.5
        half_height = self.height * 0.5
        x = self.pos[0] - half_width + x_off
        y = self.pos[1] - half_height + y_off

        #   Create the particle
        self.particles.append(particle.create((x, y)))


    def draw(self, screen):
        """ Draws each particle instance associated with the object. """

        #   Iterate through particles and draw each
        for item in self.particles:
            item.draw(screen)


    def update(self, dt):
        """ Updates each particle in the effect, and spawns new particles
        periodically. """

        #   Count up time active, and don't show animation if time is up
        self.time += dt

        #   Iterate through particles assigned to object
        for item in self.particles:

            #   If the particle has expired somehow, remove it.
            if not item.is_active():
                self.particles.remove(item)

            #   Otherwise, update the particle
            else:
                item.update_particle(dt)

        #   Don't spawn new particles if effect has expired
        if self.time >= self.duration and self.duration > 0:
            return

        #   Iterate through particle types and spawn new particles where
        #   necessary
        for idx, item in enumerate(self.particle_types):

            #   Increment time on counters
            self.cooldowns[idx] += dt

            #   Spawn a particle if time is greater than the period
            if self.cooldowns[idx] > self.periods[idx]:
                self.cooldowns[idx] -= self.periods[idx]
                self.spawn_particle(item)


################################################################################
############################### DEMO SCRIPT ####################################
################################################################################

if __name__ == '__main__':

    pygame.init()
    screen = pygame.display.set_mode((600, 200))
    pygame.display.set_caption("Particle Tools Test")

    #   DEFINE BUBBLES
    #   Define particle instance
    a = Particle(pos = (100, 100), path = "circle",
        width = 14, height = 14, color = (160, 190, 255))
    a2 = Particle(pos = (100, 100), path = "circle",
        width = 20, height = 20, color = (100, 110, 245))

    #   Add some behaviors to the particle
    a.apply_behavior(OpacityEffect(decay = 0.6))
    a.apply_behavior(ScaleEffect(growth = -0.7))
    a.apply_behavior(LinearMotionEffect(direction = -0.25, init_speed = 100))
    a.apply_behavior(CircularMotionEffect(init_radius = 10, init_freq = 1.5))

    a2.apply_behavior(OpacityEffect(decay = 0.6))
    a2.apply_behavior(ScaleEffect(growth = -0.6))
    a2.apply_behavior(LinearMotionEffect(direction = -0.25, init_speed = 90))
    a2.apply_behavior(CircularMotionEffect(init_radius = 10, init_freq = 1.5))


    #   Define particle effect instance
    bubbles = ParticleEffect(pos = (100, 150), width = 80, height = 60)
    bubbles.add_particle_type(a, period = 0.01)
    bubbles.add_particle_type(a2, period = 0.02)

    #   DEFINE FIRE
    #   Define particle types
    b = Particle(pos = (300, 100), path = "square", width = 12, height = 12,
        color = (245, 80, 70))
    c = Particle(pos = (300, 100), path = "square", width = 9, height = 9,
        color = (245, 160, 60))
    d = Particle(pos = (300, 100), path = "square", width = 7, height = 7,
        color = (235, 210, 90))
    e = Particle(pos = (300, 100), path = "square", width = 8, height = 8,
        color = (255, 255, 255))

    #   Add behaviors to particles
    b.apply_behavior(OpacityEffect(decay = 0.5))
    b.apply_behavior(LinearMotionEffect(direction = -0.25, init_speed = 60))
    c.apply_behavior(OpacityEffect(decay = 0.6))
    c.apply_behavior(LinearMotionEffect(direction = -0.25, init_speed = 80))
    d.apply_behavior(OpacityEffect(decay = 0.7))
    d.apply_behavior(LinearMotionEffect(direction = -0.25, init_speed = 100))
    e.apply_behavior(OpacityEffect(decay = 1))

    #   Define particle effect instance
    fire = ParticleEffect(pos = (300, 150), width = 50, height = 60)
    fire.add_particle_type(b, period = 0.03)
    fire.add_particle_type(c, period = 0.025)
    fire.add_particle_type(d, period = 0.015)
    fire.add_particle_type(e, period = 0.01)

    #   DEFINE GRASS
    #   Define particle types
    g1 = Particle(pos = (100, 300), path = "square", width = 20, height = 20,
        color = (40, 145, 50))
    g2 = Particle(pos = (100, 300), path = "square", width = 14, height = 14,
        color = (160, 225, 90))

    #   Add behaviors to particles
    g1.apply_behavior(CircularMotionEffect(init_radius = 20, init_freq = 0.6,
        growth = 20))
    g1.apply_behavior(OpacityEffect(decay = 0.5))
    g2.apply_behavior(CircularMotionEffect(init_radius = 20, init_freq = 0.7,
        growth = 45))
    g2.apply_behavior(OpacityEffect(decay = 0.45))

    #   Define particle effect instance
    grass = ParticleEffect(pos = (500, 100), width = 20, height = 20)
    grass.add_particle_type(g1, period = 0.02)
    grass.add_particle_type(g2, period = 0.03)

    effects = [bubbles, fire, grass]
    then = time.time()
    time.sleep(0.01)
    while True:
        now = time.time()
        dt = now - then
        then = now

        #   Print frames per second
        print("FPS: %s" % (1.0/dt))

        #   Update cloud and draw to display
        screen.fill((0, 0, 0))

        for effect in effects:
            effect.update(dt)
            effect.draw(screen)

        fire_x = int(20 * sin(now * pi) + 300)
        fire.pos = (fire_x, fire.pos[1])

        pygame.display.flip()
