import os
import pygame as _
from pygame.constants import *

#Constants
FPS = 60


# insert LEVEL class here; bg (scroll) speed should be a property of this


def setDisplay():
    screenInfo = _.display.Info()
    return _.display.set_mode((screenInfo.current_w//3, screenInfo.current_h - 100))


def processEvents(state, inputDirections):
    for e in _.event.get():
        if e.type == _.NOEVENT:
            return

        if e.type == _.KEYDOWN:
            processKeyEvent(e.key, state, inputDirections)

        if e.type == _.KEYUP:
            processKeyEvent(e.key, state, inputDirections, False)

        if e.type == _.QUIT:
            state['AppIsRunning'] = False


def processKeyEvent(keycode, state, inputDirections, isKeyDown = True):
    if (keycode == _.K_ESCAPE):
        state['AppIsRunning'] = False
        return

    if keycode == _.K_UP:
        inputDirections["up"] = isKeyDown
    if keycode == _.K_DOWN:
        inputDirections["down"] = isKeyDown
    if keycode == _.K_LEFT:
        inputDirections["left"] = isKeyDown
    if keycode == _.K_RIGHT:
        inputDirections["right"] = isKeyDown
    if keycode == _.K_SPACE and isKeyDown:
        print("PEW PEW")

#TODO:Util module
def loadImageExt(name):
    return _.image.load(f"./images/{name}.png").convert_alpha()


#TODO:Util module
def getDisplayCenter():
    di = _.display.Info()
    return (di.current_w//2, di.current_h//2)


def moveBackground(delta_time, screen, array):
    for bg in array:
        bg.y += bg.speed * delta_time
        bg.rect.y = int(bg.y)
        if (bg.rect.y >= 2000):
            y = getDisplayCenter()[1]
            bg.y = y - 2000
            bg.rect.y = int(bg.y)
        screen.blit(bg.image, bg.rect)


def initBackground(screen, x, y, x_offset=0, y_offset=0):
    bg1 = BackgroundLayer(x + x_offset, y + y_offset)
    bg2 = BackgroundLayer(x + x_offset, y-2000 + y_offset)

    # adjust for the large image..
    center_x = getDisplayCenter()[0]
    bg1.x = center_x - (bg1.rect.width/2)
    bg2.x = center_x - (bg2.rect.width/2)

    bg1.rect.x = int(bg1.x)
    bg2.rect.x = int(bg2.x)

    return [bg1, bg2]


class BackgroundLayer(_.sprite.Sprite):
    background_filename = "back_cave_3"
    def __init__(self, x, y, speed = .1):
        super().__init__()
        
        self.image = _.transform.rotate(loadImageExt(self.background_filename), 90)
        self.x, self.y = x, y
        self.rect = self.image.get_rect()
        
        self.speed = speed


class Player(_.sprite.Sprite):
    player_image_filename = "Spaceship004"
    def __init__(self, speed = .5):
        super().__init__()

        self.image = loadImageExt(self.player_image_filename)
        center_x, center_y = getDisplayCenter()
        self.rect = self.image.get_rect()
        self.x, self.y = center_x, center_y * 2 - 10
        self.rect.x, self.rect.y = center_x, center_y * 2 - 50

        self.speed = speed

    def update(self, screen, delta_time, inputDirections):
        if inputDirections["right"]:
            self.rect.x += int(delta_time * self.speed)
        if inputDirections["left"]:
            self.rect.x -= int(delta_time * self.speed)
        if inputDirections["up"]:
            self.rect.y -= int(delta_time * self.speed)
        if inputDirections["down"]:
            self.rect.y += int(delta_time * self.speed)
        screen.blit(self.image, self.rect)

def main():
    _.init()
    if not _.display.get_init():
        print("Display failed to initialized")
        return

    os.environ['SDL_VIDEO_CENTERED'] = '1' 
    SCREEN = setDisplay()
    backgroundArray = initBackground(SCREEN, 0, 0)
    player = Player()

    state = {'AppIsRunning': True}
    inputDirections = {
        "up": False,
        "down": False,
        "left": False,
        "right": False
    }

    fpsClock = _.time.Clock()
    while(state['AppIsRunning']):
        delta_time = fpsClock.tick(FPS)
        processEvents(state, inputDirections)
        moveBackground(delta_time, SCREEN, backgroundArray)
        player.update(SCREEN, delta_time, inputDirections)

        _.display.update()


if __name__ == "__main__":
    main()