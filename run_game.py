import os
import random
import pygame as _
from pygame.constants import *

# Constants
FPS = 60
COLORS = {
    "white": (255, 255, 255)
}


STATE = {
    "AppIsRunning": True,
    "IsPaused": False,
    "IsGameOver": False,
}

INPUTS = {
    "up": False,
    "down": False,
    "left": False,
    "right": False,
    "fire": False,
    "super": False,
    "reset": False,
}

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
    if keycode == _.K_z:
        inputs["super"] = isKeyDown
    if keycode == _.K_r:
        inputs["reset"] = isKeyDown


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


def renderBackground(array):
    for bg in array:
        bg.screen.blit(bg.image, bg.rect)


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
    fire_cooldown_max = 275
    powerup_max = 4
    life_count = 3
    is_invulnerable = False
    invulnerable_cooldown = 0
    invulnerable_cooldown_max = 500

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
        self.life_count = 3
        self.screen_w = screen.get_width()
        self.screen_h = screen.get_height()
        self.bullet_sound = _.mixer.Sound("./audio/bullet.wav")

    def update(self, delta_time, inputs, enemies):
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
            self.fire_cooldown = self.fire_cooldown_max
            self.bullets.append(Bullet(self.screen, self.rect.x, self.rect.y))
            self.bullet_sound.play()
        if inputs["super"] and self.powerup_count == self.powerup_max:
            self.powerup_count = 0
            self.bullets.append(Bullet(self.screen,
                                       self.rect.x,
                                       self.rect.y,
                                       speed=1,
                                       scale_multiplier=self.powerup_max))
            self.bullet_sound.play()

        self.handleEnemyCollisions(enemies)
        self.fire_cooldown -= delta_time
        self.invulnerable_cooldown -= delta_time
        if self.invulnerable_cooldown < 0:
            self.is_invulnerable = False
        self.screen.blit(self.image, self.rect)
        self.updateBullets(delta_time, enemies)

    def calculateSpeed(self, dt):
        return int(dt * self.speed)

    def updateBullets(self, dt, enemies):
        for b in self.bullets:
            y = -50 if not b.is_super else -200
            if b.rect.y < y:
                self.bullets.remove(b)
                continue

            is_hit = False
            for e in enemies:
                if b.is_super:
                    continue
                if _.sprite.collide_rect(b, e):
                    is_hit = True
                    break

            if is_hit:
                self.bullets.remove(b)
                if self.powerup_count < self.powerup_max:
                    self.powerup_count += 1
                continue

            b.update(dt)

    def handleEnemyCollisions(self, enemies):
        for e in enemies:
            if not self.is_invulnerable and _.sprite.collide_rect(self, e):
                self.is_invulnerable = True
                self.invulnerable_cooldown = self.invulnerable_cooldown_max
                self.life_count -= 1


class Bullet(_.sprite.Sprite):
    filename = "bullet"

    def __init__(self, screen, x, y, speed=.5, scale_multiplier=1):
        super().__init__()

        self.is_super = scale_multiplier > 1
        self.image = scaleImage(loadImageExt(self.filename),
                                (scale_multiplier * 3.5))
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
    cooldown_max = 100

    def __init__(self, screen, x, y):
        super().__init__()

        self.original_image = scaleImage(loadImageExt(self.filename), 2)
        self.rect = self.original_image.get_rect()
        self.rect.topleft = x, y
        self.screen = screen
        self.animation_cooldown = 0
        self.angle = 0

    def update(self, dt):
        if self.animation_cooldown <= 0:
            self.animation_cooldown = self.cooldown_max
            self.angle += 45
            self.image = _.transform.rotate(self.original_image, self.angle)
            x, y = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = (x, y)

        self.animation_cooldown -= dt
        self.screen.blit(self.image, self.rect)


class UI():
    powerups = []
    score = 200
    score_len_max = 9
    score_text = ""
    powerup_x, powerup_y = 20, 20
    lives = []

    def __init__(self, screen):
        self.screen = screen
        self.font = _.font.Font(None, 40)

    def update(self, dt, charge_count, life_count):
        if len(self.powerups) < charge_count:
            self.powerups.append(PowerUp(self.screen,
                                 self.powerup_x * charge_count,
                                 self.powerup_y))
        elif(charge_count == 0):
            self.powerups.clear()

        self.renderPowerups(dt)
        self.renderScore()
        self.renderLives(life_count)

    def renderPowerups(self, dt):
        for pu in self.powerups:
            pu.update(dt)

    def renderLives(self, life_count):
        if life_count < 0:
            return

        while len(self.lives) < life_count:
            self.lives.append(Life(self.screen,
                                   self.powerup_y,
                                   len(self.lives) + 1))
        while len(self.lives) > life_count:
            self.lives.remove(self.lives[len(self.lives) - 1])
        for l in self.lives:
            l.update()

    def renderScore(self):
        # TODO: optimize displaying score
        self.score_text = ""
        score_str = str(self.score)
        for x in range(self.score_len_max - len(score_str)):
            self.score_text += "0"
        self.score_text = f"{self.score_text}{score_str}"
        score = self.font.render(self.score_text, False, COLORS["white"])
        score_rect = score.get_rect()
        score_rect.topleft = (self.screen.get_width() - score_rect.width - 10,
                              self.powerup_y)
        self.screen.blit(score, score_rect)


class Life(_.sprite.Sprite):
    filename = "butterfly_01"

    def __init__(self, screen, y, count):
        super().__init__()

        self.screen = screen
        self.image = scaleImage(loadImageExt(self.filename), 2)
        self.rect = self.image.get_rect()
        center = screen.get_width()//2
        if count == 3:
            self.rect.topleft = center + 50, y
        elif count == 2:
            self.rect.topleft = center, y
        elif count == 1:
            self.rect.topleft = center - 50, y

    def update(self):
        self.screen.blit(self.image, self.rect)


class Enemy(_.sprite.Sprite):
    def __init__(self, screen, speed, filename):
        super().__init__()

        self.screen = screen
        self.speed = speed
        self.image = scaleImage(loadImageExt(self.filename), 2)
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(0, screen.get_width()),
                            random.randint(-200, -10))

    def update(self, dt):
        self.rect.center = (self.rect.centerx,
                            (self.rect.centery + int(self.speed * dt)))
        self.screen.blit(self.image, self.rect)


class Sun(Enemy):
    filename = "sun"

    def __init__(self, screen):
        super().__init__(screen, .5, self.filename)


class Toilet(Enemy):
    filename = "toilet"

    def __init__(self, screen):
        super().__init__(screen, .5, self.filename)


class EnemyEngine():
    enemy_max = 10
    enemies = []
    spawn_cooldown = 0
    cooldown_max = 1000

    def __init__(self, screen):
        self.screen = screen
        self.update_timer = 0

    def update(self, dt, bullets, ui):
        self.update_timer += dt
        if self.update_timer > 30000:
            self.update_timer = 0
            self.enemy_max += 10
        while(len(self.enemies) < self.enemy_max and self.spawn_cooldown < 0):
            if self.enemy_max == len(self.enemies) + 1:
                self.spawn_cooldown = self.cooldown_max

            enemy = Sun(self.screen) if random.randint(0, 1) == 0 else Toilet(self.screen)
            self.enemies.append(enemy)

        self.spawn_cooldown -= dt
        for e in self.enemies:
            if e.rect.y > self.screen.get_height() + 100:
                self.enemies.remove(e)
                continue

            is_shot = False
            for b in bullets:
                if _.sprite.collide_rect(b, e):
                    is_shot = True

            if is_shot:
                self.enemies.remove(e)
                ui.score += 10
                continue

            e.update(dt)


class GameOver():
    def __init__(self, screen):
        self.screen = screen
        self.font = _.font.Font(None, 40)
        self.game_over = self.font.render("GAME OVER!!!", False, COLORS["white"])
        self.rect = self.game_over.get_rect()
        self.rect.x, self.rect.y = screen.get_width()//2 - 100, -100

    def update(self, speed, dt):
        # TODO: Reset functionality
        if self.screen.get_height()//2 > self.rect.y:
            self.rect.y += int(dt * speed)
        self.screen.blit(self.game_over, self.rect)


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
    ee = EnemyEngine(SCREEN)
    go = GameOver(SCREEN)
    _.mixer.music.load("./audio/song.mp3")
    _.mixer.music.play()
    fpsClock = _.time.Clock()
    while(STATE['AppIsRunning']):
        delta_time = fpsClock.tick(FPS)
        processEvents(STATE, INPUTS)

        if STATE["IsGameOver"] and INPUTS["reset"]:
            STATE["IsGameOver"] = False

        STATE["IsGameOver"] = player.life_count == 0
        if STATE["IsGameOver"]:
            SCREEN.fill((0, 0, 0))
            renderBackground(backgroundArray)
            go.update(.25, delta_time)
            ui.update(delta_time, player.powerup_count, player.life_count)

        if not STATE["IsPaused"] and not STATE["IsGameOver"]:
            SCREEN.fill((0, 0, 0))
            moveBackground(delta_time, backgroundArray)
            player.update(delta_time, INPUTS, ee.enemies)
            ee.update(delta_time, player.bullets, ui)
            ui.update(delta_time, player.powerup_count, player.life_count)

        _.display.update()


if __name__ == "__main__":
    main()
