import pygame as _
from pygame.constants import *

#Constants
BACKGROUND_FILENAME = "back_cave_3"
FPS = 60


# insert LEVEL class here; bg (scroll) speed should be a property of this


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


def moveBackground(delta_time, screen, array):
    # These are just simple bg things, so not a big deal
    # but a good technique is to have things be objects
    # and then give them an _update() method that defines
    # their behaviors (which you then call every frame)
    
    # most people call these guys 'actors', which is fine
    # I just call them 'sprites', which is less accurate
    # but also fine, because I say so
        
    for bg in array:
        # always try to use delta_time
        bg.y += bg.speed * delta_time
        bg.rect.y = int(bg.y)
        if (bg.rect.y >= 2000):
            bg.rect.y = y - 2000
        screen.blit(bg.image, bg.rect)

def initBackground(screen, x, y, x_offset=0, y_offset=0):
    bg1 = BackgroundLayer(BACKGROUND_FILENAME, x + x_offset, y + y_offset, .1)
    bg2 = BackgroundLayer(BACKGROUND_FILENAME, x + x_offset, y-2000 + y_offset, .1)
    
    # adjust for the large image..
    CENTER_X = getDisplayCenter()[0]
    bg1.x = CENTER_X - (bg1.rect.width/2)
    bg2.x = CENTER_X - (bg2.rect.width/2)
    
    # implicit conversion is being deprecated (I know
    # it's for the best, but I don't like it!)
    # And pygame rects use ints, so we have
    # to store the real x/y values separately
   
    bg1.rect.x = int(bg1.x)
    bg2.rect.x = int(bg2.x)
    
    return [bg1, bg2]

class BackgroundLayer(_.sprite.Sprite):
    def __init__(self, image, x, y, speed):
        super().__init__()
        
        self.image = _.transform.rotate(loadImageExt(image), 90)
        self.x, self.y = x, y
        self.rect = self.image.get_rect()
        
        self.speed = speed
        


def main():
    _.init()
    if not _.display.get_init():
        print("Display failed to initialized")
        return
    
    CENTER_X, CENTER_Y = getDisplayCenter()
    screen = setDisplay()
    
    backgroundArray = initBackground(screen, 0, 0)

    state = {'AppIsRunning': True}
    
    # define the FPS clock outside the loop..
    fpsClock = _.time.Clock()
    
    while(state['AppIsRunning']):
        # ..then call it at the head of your loop
        # this lets it pause until the next frame
        # 'should' be run..
        delta_time = fpsClock.tick(FPS)
        
        moveBackground(delta_time, screen, backgroundArray)
        processEvents(state)

        _.display.update()
if __name__ == "__main__":
    main()