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
        print("PEW PEW")
        inputs["fire"] = isKeyDown


# TODO:Util module
def loadImageExt(name):
    return _.image.load(f"./images/{name}.png").convert_alpha()


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
    background_filename = "back_cave_3"

    def __init__(self, screen, x, y, speed=.1):
        super().__init__()

        self.image = _.transform.rotate(
            loadImageExt(self.background_filename), 90)
        self.x, self.y = x, y
        self.rect = self.image.get_rect()

        self.speed = speed
        self.screen = screen


class Player(_.sprite.Sprite):
    player_image_filename = "Spaceship004"
    bullets = []

    def __init__(self, screen, speed=.5):
        super().__init__()

        self.image = loadImageExt(self.player_image_filename)
        center_x, center_y = getDisplayCenter()
        self.rect = self.image.get_rect()
        self.x, self.y = center_x, center_y * 2 - 10
        self.rect.x, self.rect.y = center_x, center_y * 2 - 50

        self.speed = speed
        self.screen = screen

    def update(self, delta_time, inputs):
        if inputs["right"]:
            self.rect.x += self.calculateSpeed(delta_time)
        if inputs["left"]:
            self.rect.x -= self.calculateSpeed(delta_time)
        if inputs["up"]:
            self.rect.y -= self.calculateSpeed(delta_time)
        if inputs["down"]:
            self.rect.y += self.calculateSpeed(delta_time)
        if inputs["fire"] and len(self.bullets) < 4:
            print("Added bullet")
            self.bullets.append(Bullet(self.screen, self.rect.x, self.rect.y))
        self.screen.blit(self.image, self.rect)
        self.updateBullets(delta_time)

    def calculateSpeed(self, dt):
        return int(dt * self.speed)

    def updateBullets(self, dt):
        for b in self.bullets:
            if b.rect.y < -10:
                self.bullets.remove(b)
                continue
            b.update(dt)


class Bullet(_.sprite.Sprite):
    bullet_image_filename = "bullet"

    def __init__(self, screen, x, y, speed=.65):
        super().__init__()

        self.image = loadImageExt(self.bullet_image_filename)
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = x, y
        self.screen = screen
        self.speed = speed

    def update(self, dt):
        self.rect.y -= int(dt * self.speed)
        self.screen.blit(self.image, self.rect)


def main():
    _.init()
    if not _.display.get_init():
        print("Display failed to initialized")
        return

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    SCREEN = setDisplay()
    backgroundArray = initBackground(SCREEN, 0, 0)
    player = Player(SCREEN)

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
            moveBackground(delta_time, backgroundArray)
            player.update(delta_time, inputs)

        _.display.update()


if __name__ == "__main__":
    main()
