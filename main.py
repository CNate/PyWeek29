import os
import pygame as _
from pygame.constants import *

# Constants
FPS = 60


# insert LEVEL class here; bg (scroll) speed should be a property of this


def setDisplay():
    screenInfo = _.display.Info()
    return _.display.set_mode((screenInfo.current_w//3, screenInfo.current_h - 100))


def processEvents(state, inputs):
    for e in _.event.get():
        if e.type == _.NOEVENT:
            return

        if e.type == _.KEYDOWN:
            processKeyEvent(e.key, state, inputs)

        if e.type == _.KEYUP:
            processKeyEvent(e.key, state, inputs, False)

        if e.type == _.QUIT:
            state['AppIsRunning'] = False


def processKeyEvent(keycode, state, inputs, isKeyDown=True):
    if (keycode == _.K_ESCAPE) and isKeyDown:
        state["IsPaused"] = not state["IsPaused"]
        return

    if keycode == _.K_UP:
        inputs["up"] = isKeyDown
    if keycode == _.K_DOWN:
        inputs["down"] = isKeyDown
    if keycode == _.K_LEFT:
        inputs["left"] = isKeyDown
    if keycode == _.K_RIGHT:
        inputs["right"] = isKeyDown
    if keycode == _.K_SPACE:
        inputs["fire"] = isKeyDown


# TODO:Util module
def loadImageExt(name):
    return _.image.load(f"./images/{name}.png").convert_alpha()


def scaleImage(surface, multiplier):
    rect = surface.get_rect()
    w, h = int(rect.w * multiplier), int(rect.h * multiplier)
    return _.transform.scale(surface, (w, h))


# TODO:Util module
def getDisplayCenter():
    di = _.display.Info()
    return (di.current_w//2, di.current_h//2)


def moveBackground(delta_time, array):
    for bg in array:
        bg.y += bg.speed * delta_time
        bg.rect.y = int(bg.y)
        if (bg.rect.y >= 2000):
            y = getDisplayCenter()[1]
            bg.y = y - 2000
            bg.rect.y = int(bg.y)
        bg.screen.blit(bg.image, bg.rect)


def initBackground(screen, x, y, x_offset=0, y_offset=0):
    bg1 = BackgroundLayer(screen, x + x_offset, y + y_offset)
    bg2 = BackgroundLayer(screen, x + x_offset, y-2000 + y_offset)

    # adjust for the large image..
    center_x = getDisplayCenter()[0]
    bg1.x = center_x - (bg1.rect.width/2)
    bg2.x = center_x - (bg2.rect.width/2)

    bg1.rect.x = int(bg1.x)
    bg2.rect.x = int(bg2.x)

    return [bg1, bg2]


class BackgroundLayer(_.sprite.Sprite):
    filename = "back_cave_3"

    def __init__(self, screen, x, y, speed=.1):
        super().__init__()

        self.image = _.transform.rotate(loadImageExt(self.filename), 90)
        self.x, self.y = x, y
        self.rect = self.image.get_rect()

        self.speed = speed
        self.screen = screen


class Player(_.sprite.Sprite):
    filename = "butterfly_01"
    bullets = []
    powerup_count = 0

    def __init__(self, screen, speed=.5):
        super().__init__()

        self.image = scaleImage(loadImageExt(self.filename), 3.5)
        center_x, center_y = getDisplayCenter()
        self.rect = self.image.get_rect()
        self.x, self.y = center_x, center_y * 2 - 10
        self.rect.x, self.rect.y = center_x, center_y * 2 - 50

        self.speed = speed
        self.screen = screen
        self.fire_cooldown = 0
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()

    def update(self, delta_time, inputs):
        center_x = self.rect.x + int(self.rect.w/2)
        center_y = self.rect.y + int(self.rect.h/2)
        if center_x < self.screen_w and inputs["right"]:
            self.rect.x += self.calculateSpeed(delta_time)
        if center_x > 0 and inputs["left"]:
            self.rect.x -= self.calculateSpeed(delta_time)
        if center_y > 30 and inputs["up"]:
            self.rect.y -= self.calculateSpeed(delta_time)
        if center_y < self.screen_h and inputs["down"]:
            self.rect.y += self.calculateSpeed(delta_time)
        if self.fire_cooldown < 0 and inputs["fire"] and len(self.bullets) < 4:
            self.fire_cooldown = 275
            self.powerup_count += 1
            self.bullets.append(Bullet(self.screen, self.rect.x, self.rect.y))

        self.fire_cooldown -= delta_time
        self.screen.blit(self.image, self.rect)
        self.updateBullets(delta_time)

    def calculateSpeed(self, dt):
        return int(dt * self.speed)

    def updateBullets(self, dt):
        for b in self.bullets:
            if b.rect.y < -50:
                self.bullets.remove(b)
                continue
            b.update(dt)


class Bullet(_.sprite.Sprite):
    filename = "bullet"

    def __init__(self, screen, x, y, speed=.5):
        super().__init__()

        self.image = scaleImage(loadImageExt(self.filename), 3.5)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.screen = screen
        self.speed = speed
        self.animation_cooldown = 0

    def update(self, dt):
        self.rect.y -= int(dt * self.speed)
        if self.animation_cooldown < 0:
            self.image = _.transform.flip(self.image, True, False)
            self.animation_cooldown = 50
        self.animation_cooldown -= dt
        self.screen.blit(self.image, self.rect)


class PowerUp(_.sprite.Sprite):
    filename = "powerup"

    def __init__(self, screen, x, y):
        self.original_image = scaleImage(loadImageExt(self.filename), 2)
        self.image = self.original_image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.screen = screen
        self.animation_cooldown = 0
        self.angle = 0

    def update(self, dt):
        if self.animation_cooldown <= 0:
            self.animation_cooldown = 100
            self.angle += 45 % 360
            self.image = _.transform.rotate(self.original_image, self.angle)
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)

        self.animation_cooldown -= dt
        self.screen.blit(self.image, self.rect)


class UI():
    powerups = []
    score = 0
    powerup_x, powerup_y = 20, 20

    def __init__(self, screen):
        self.screen = screen

    def update(self, dt, count):
        if len(self.powerups) < count:
            self.powerups.append(PowerUp(self.screen,
                                 self.powerup_x * count,
                                 self.powerup_y))
        self.renderPowerups(dt)

    def renderPowerups(self, dt):
        for pu in self.powerups:
            pu.update(dt)


def main():
    _.init()
    if not _.display.get_init():
        print("Display failed to initialized")
        return

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    SCREEN = setDisplay()
    backgroundArray = initBackground(SCREEN, 0, 0)
    player = Player(SCREEN)
    ui = UI(SCREEN)

    state = {
        "AppIsRunning": True,
        "IsPaused": False,
    }

    inputs = {
        "up": False,
        "down": False,
        "left": False,
        "right": False,
        "fire": False,
    }

    fpsClock = _.time.Clock()
    while(state['AppIsRunning']):
        delta_time = fpsClock.tick(FPS)
        processEvents(state, inputs)
        if not state["IsPaused"]:
            SCREEN.fill((0, 0, 0))
            moveBackground(delta_time, backgroundArray)
            player.update(delta_time, inputs)
            ui.update(delta_time, player.powerup_count)

        _.display.update()


if __name__ == "__main__":
    main()
