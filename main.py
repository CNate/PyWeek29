import pygame as _
from pygame.constants import *

#Constants
BACKGROUND_FILENAME = "back_cave_3"


def setDisplay():
    screenInfo = _.display.Info()
    return _.display.set_mode((screenInfo.current_w//3, screenInfo.current_h - 100))


def processEvents(state):
    event = _.event.poll()
    if event.type == _.NOEVENT:
        return

    if event.type == _.QUIT:
        state['AppIsRunning'] = False

#TODO:Util module
def loadImageExt(name):
    return _.image.load(f"./images/{name}.png").convert()


#TODO:Util module
def getDisplayCenter():
    di = _.display.Info()
    return (di.current_w//2, di.current_h//2)


def moveBackground(screen, array, center_y):
    for image, rect in array:
        rect.centery = rect.centery + 1
        if (rect.centery > center_y + 2000):
            rect.centery = center_y - 2000
        screen.blit(image, rect)

def initBackground(screen, center_x, center_y):
    bgImg = _.transform.rotate(loadImageExt(BACKGROUND_FILENAME), 90)
    bgRect1 = bgImg.get_rect()
    bgRect1.center = center_x, center_y
    bgRect2 = bgImg.get_rect()
    bgRect2.center = bgRect1.centerx, bgRect1.centery - 2000
    screen.blit(bgImg, bgRect1)
    return [(bgImg, bgRect1), (bgImg, bgRect2)]


def main():
    _.init()
    if not _.display.get_init():
        print("Display failed to initialized")
        return

    screen = setDisplay()
    CENTER_X, CENTER_Y = getDisplayCenter()
    backgroundArray = initBackground(screen, CENTER_X, CENTER_Y)

    state = {'AppIsRunning': True}
    while(state['AppIsRunning']):
        _.display.update()
        _.time.Clock().tick(60)
        moveBackground(screen, backgroundArray, CENTER_Y)
        processEvents(state)

if __name__ == "__main__":
    main()