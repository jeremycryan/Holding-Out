import math
import pygame

DEBUG = False

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

CAPTION = "Please hold while a representative eats your brains"
FRAMERATE = 100

WALKING = 0
IDLE = 1
ROLLING = 2
TAKING_DAMAGE = 3

RIGHT = 0
UP = 1
LEFT = 2
DOWN = 3

ARENA_WIDTH = 1400
ARENA_HEIGHT = 1000
ARENA_SIZE = 4000

BACKGROUND = 0
FOREGROUND = 1

CPS=3000#30

HOLD_TIMES = (5, 30, 30, 1)
DISCONNECT_LINES = ["Hello? Sorry, I think I lost you for a second.","Are you still there? Oh good, you're back."]
COMPANY_NAME = "Company Name"

UPGRADES = (
    "Hell's Shells",
    "Big Pockets",
    "Beefy Bullets",
    "Piercing",
    "Green",
    "Full Auto",
    "Spinning Death",
)

UPGRADE_DESCRIPTIONS = (
    "Shoot three bullets at once",
    "Carry 50% more ammo",
    "Bullets deal more damage",
    "Shots pierce through enemies",
    "Missed shots sometimes refund",
    "Shoot faster",
    "Can shoot while rolling",
)

