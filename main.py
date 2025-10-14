import pygame
import random
import ctypes
import math
import pygame_record as rec
import tkinter as tk
from tkinter import filedialog
import os
import pathlib
import yaml

state = "PLAY"
"""State一覧
RENDER: レンダリング中
FINISH: レンダリング終了
FREE: フリープレイ(マウスで雨を操れる)
PLAY: 再生中"""
drops = []

# 動画の途中で変えられる
freq = 1  # 雨粒の密度
wind = 0  # 風の強さ
global_yspd = 20

# 動画の途中で変えられない
SCREEN_WIDTH = 1280  # 横解像度/ピクセル
SCREEN_HEIGHT = 720  # 縦解像度/ピクセル
FRAME_RATE = 60  # フレームレート
DROP_LENGTH = 2  # 雨粒の長さ/フレーム
DROP_WIDTH = 4  # 雨粒の太さ/ピクセル
DROP_COLOR = (128, 128, 128)  # 雨粒の色
X_DIPERSION = 0.5  # X方向の分散
Y_DIPERSION = 5  # Y方向の分散
DIR_RANGE = math.pi  # 雨の範囲/ラジアン
RADIUS = 800  # 雨の出現半径
ACC = 0.1  # 加速度


def open_project() -> str | None:
    path = filedialog.askopenfilename(
        title="Open Project File",
        defaultextension="rain",
        filetypes=[("Rain Project File", "*.rain")],
        initialdir=os.getcwd(),
    )
    if pathlib.Path(path).exists():
        return path


def select_window():
    select = ["CONTINUE"]

    root = tk.Tk("SBANRain")
    root.geometry("280x120")
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_rowconfigure(0, weight=1)

    frame1 = tk.Frame(root)
    frame1.grid_rowconfigure(0, weight=1)
    frame1.grid_rowconfigure(1, weight=1)
    frame1.grid_rowconfigure(2, weight=1)
    frame1.grid_rowconfigure(3, weight=1)

    def cmd_continue():
        nonlocal select
        select = ["CONTINUE"]
        root.destroy()

    def cmd_render():
        nonlocal select
        select = ["RENDER"]
        root.destroy()

    def cmd_open():
        nonlocal select
        select = ["OPEN"]
        root.destroy()

    def cmd_free():
        nonlocal select
        select = ["FREE"]
        root.destroy()

    def cmd_play():
        select = ["PLAY", int(60 * int(entry1.get()) + int(entry2.get()))]
        root.destroy()

    button1 = tk.Button(frame1, text="Continue", width=12, command=cmd_continue)
    button2 = tk.Button(frame1, text="Render", width=12, command=cmd_render)
    button3 = tk.Button(frame1, text="Open", width=12, command=cmd_open)
    button4 = tk.Button(frame1, text="FreePlay", width=12, command=cmd_free)
    button1.grid(row=0)
    button2.grid(row=1)
    button3.grid(row=2)
    button4.grid(row=3)

    frame2 = tk.Frame(root)
    frame2.grid_columnconfigure(0, weight=1)
    frame2.grid_columnconfigure(2, weight=1)
    frame2.grid_rowconfigure(0, weight=1)
    frame2.grid_rowconfigure(1, weight=1)
    entry1 = tk.Entry(frame2, width=6, justify=tk.RIGHT)  # 再生位置分
    label = tk.Label(frame2, text=":")
    entry2 = tk.Entry(frame2, width=6)  # 再生位置秒
    button5 = tk.Button(frame2, text="Play", width=12, command=cmd_play)
    entry1.grid(row=0, column=0, sticky=tk.E)
    label.grid(row=0, column=1)
    entry2.grid(row=0, column=2, sticky=tk.W)
    button5.grid(row=1, column=0, columnspan=3)

    frame1.grid(row=0, column=0)
    frame2.grid(row=0, column=1)

    root.mainloop()

    return select


def load_project(path):
    pass


pygame.init()
ctypes.windll.user32.SetProcessDPIAware()  # ウィンドウサイズの誤挙動を防ぐ
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
running = True
last_drop = 0
pre_global_ysd = global_yspd
path = ""
frame = 0


class Drop:
    """雨粒

    Args:
        x (float): 出現するX座標
        y (float): 出現するY座標
        xspd (float): X初速
        yspd (float): Y初速
    """

    def __init__(self, x, y, xspd, yspd):
        self.x = x
        self.y = y
        self.log = [(self.x, self.y) for i in range(DROP_LENGTH)]  # 座標の履歴
        self.xspd = xspd
        self.yspd = yspd

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

            pygame.draw.lines(
                surface,
                DROP_COLOR,
                True,
                self.log,
                DROP_WIDTH,
            )


def drop_drop():
    direction = math.atan2(wind / 4, global_yspd) + random.uniform(
        -DIR_RANGE * 0.5, DIR_RANGE * 0.5
    )  # 雨の出現位置用の向き(ラジアン)
    drops.append(
        Drop(
            SCREEN_WIDTH / 2 - math.sin(direction) * RADIUS,
            SCREEN_HEIGHT / 2 - math.cos(direction) * RADIUS,
            random.uniform(-X_DIPERSION, X_DIPERSION),
            random.uniform(global_yspd - Y_DIPERSION, global_yspd + Y_DIPERSION),
        )
    )


def get_pressed():
    pressed = []
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            pressed.append(pygame.key.name(event.key))
    return pressed


while running:
    if (
        (path == "" and not state == "FREE")
        or "r" in get_pressed()
        or state == "FINISH"
    ):
        if path == "":
            open_project()
        select = select_window()
        if select[0] == "CONTINUE":
            pass
        elif select[0] == "RENDER":
            state = "RENDER"
            rec.key(SCREEN_WIDTH, SCREEN_HEIGHT, 60)
            frame = 0
        elif select[0] == "OPEN":
            if state == "RENDER":
                rec.stop()
            continue
        elif select[0] == "FREE":
            if state == "RENDER":
                rec.stop()
            state = "FREE"
        elif select[0] == "PLAY":
            frame = select[1]
            state = "PLAY"

    frame += 1
    screen.fill((0, 0, 0))
    surface.fill((0, 0, 0))

    if state == "FREE":
        # マウス座標で動かす
        wind = (pygame.mouse.get_pos()[0] - SCREEN_WIDTH / 2) / 5
        global_yspd = pygame.mouse.get_pos()[1] / 10

    if 0 < freq < 1:
        if frame - last_drop >= 1 / freq:
            drop_drop()
            last_drop = frame
    else:
        for i in range(int(freq)):
            drop_drop()
        last_drop = frame

    for x in drops:
        x.yspd += global_yspd - pre_global_ysd
    pre_global_ysd = global_yspd

    [x.update() for x in drops]
    if state == "RENDER":
        rec.draw(surface)
    screen.blit(surface, (0, 0))
    pygame.display.flip()
    clock.tick(FRAME_RATE)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            if state == "RENDER":
                rec.stop()
            running = False
