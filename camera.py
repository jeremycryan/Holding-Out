from primitives import Pose
import constants as c
import math

class Camera:
    position = None
    target = None
    shake_amt = 0
    shake_direction = (1, 1)
    since_shake = 0

    @classmethod
    def init(cls, position=(0, 0)):
        cls.position = Pose(position)
        cls.set_target(position)

    @classmethod
    def set_target(cls, position=(0, 0)):
        cls.target = Pose(position)

    @classmethod
    def update(cls, dt, events):
        d = cls.target - cls.position - Pose(c.WINDOW_SIZE) * 0.5
        speed = d*dt*4
        cls.position += speed

        cls.since_shake += dt
        cls.shake_amt *= 0.08**dt
        cls.shake_amt -= 100*dt
        if cls.shake_amt < 0:
            cls.shake_amt = 0

    @classmethod
    def snap_to_target(cls):
        d = cls.target - cls.position - Pose(c.WINDOW_SIZE) * 0.5
        cls.position += d


    @classmethod
    def screen_to_world(cls, position):
        return Pose(position) + cls.position

    @classmethod
    def world_to_screen(cls, position):
        return Pose(position) - cls.position

    @classmethod
    def get_draw_offset(cls):
        off = cls.world_to_screen((0, 0))
        shake_amt = math.cos(cls.since_shake*35)*cls.shake_amt
        shake_pos = Pose(cls.shake_direction)*shake_amt
        off += shake_pos
        return off

    @classmethod
    def shake(cls, amt=10, direction=None):
        if direction==None:
            direction = (1, 1)
        direction = Pose(direction)
        direction.scale_to(1)
        cls.shake_direction = direction.get_position()
        if amt > cls.shake_amt:
            cls.shake_amt = amt
            cls.since_shake = 0
