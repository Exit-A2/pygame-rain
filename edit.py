import pygame
import ctypes
import json


def rgb2tuple(rgb):
    return (int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16))


colors = {k: rgb2tuple(v) for k, v in json.load(open("colors.json")).items()}
print(colors)
pygame.init()
screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
ctypes.windll.user32.SetProcessDPIAware()  # ウィンドウサイズの誤挙動を防ぐ

border_position = 0.6
current_w = 1280
current_h = 720

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.VIDEORESIZE:
            current_w = event.w
            current_h = event.h

        if event.type == pygame.QUIT:
            running = False

    screen.fill(colors["background"])

    pygame.draw.line(
        screen,
        colors["border"],
        (0, current_h * border_position),
        (current_w, current_h * border_position),
        5,
    )
    pygame.display.flip()
