import pygame
import random
import ctypes
import math


drops = []
freq = 10  # 雨粒の密度
wind = 0  # 風の強さ
time = 0
last_drop = 0
global_yspd = 20
pre_global_ysd = global_yspd
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
DROP_LENGTH = 2  # 2以上
X_DIPERSION = 0.5  # X方向の分散
Y_DIPERSION = 5  # Y方向の分散
RADIUS = 800
ACC = 0.1
COLOR = (255, 255, 255)

pygame.init()
ctypes.windll.user32.SetProcessDPIAware()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True


class Drop:
    """雨粒

    Args:
        x (float): 出現するX座標
        y (float): 出現するY座標
        xspd (float): X初速
        yspd (float): Y初速
        depth (float): 奥行き
    """

    def __init__(self, x, y, xspd, yspd, depth):
        self.x = x
        self.y = y
        self.log = [(self.x, self.y) for i in range(DROP_LENGTH)]  # 座標の履歴
        self.xspd = xspd
        self.yspd = yspd
        self.depth = depth

    def update(self):
        if (
            (self.log[0][1] > SCREEN_WIDTH + 100)
            or self.log[0][0] < SCREEN_WIDTH / 2 - RADIUS
            or self.log[0][0] > SCREEN_WIDTH / 2 + RADIUS
        ):  # 消滅検知
            del self
        else:
            self.y += self.yspd
            self.x += wind
            self.x += self.xspd
            self.yspd += ACC
            self.log.pop(0)
            self.log.append((self.x, self.y))

            width = 5 / self.depth

            pygame.draw.lines(
                screen,
                COLOR,
                True,
                self.log,
                int(width),
            )


def drop_drop():
    direction = math.atan2(wind / 4, global_yspd) + random.uniform(
        -math.pi * 0.5, math.pi * 0.5
    )  # 雨の出現位置用の向き(ラジアン)
    drops.append(
        Drop(
            SCREEN_WIDTH / 2 - math.sin(direction) * RADIUS,
            SCREEN_HEIGHT / 2 - math.cos(direction) * RADIUS,
            random.uniform(-X_DIPERSION, X_DIPERSION),
            random.uniform(global_yspd - Y_DIPERSION, global_yspd + Y_DIPERSION),
            1,
        )
    )


while running:
    time += 1
    screen.fill((0, 0, 0))

    wind = (pygame.mouse.get_pos()[0] - SCREEN_WIDTH / 2) / 5
    global_yspd = pygame.mouse.get_pos()[1] / 10

    if 0 < freq < 1:
        if time - last_drop >= 1 / freq:
            drop_drop()
            last_drop = time
    else:
        for i in range(int(freq)):
            drop_drop()
        last_drop = time

    for x in drops:
        x.yspd += global_yspd - pre_global_ysd
    pre_global_ysd = global_yspd

    [x.update() for x in drops]
    pygame.display.flip()
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
