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

screen_width = 1920
screen_height = 1080

focus = "None"
border_position = 0.6
timeline_side_x = 200

current_w = 1280
current_h = 720

running = True
while running:
    cursor = pygame.SYSTEM_CURSOR_ARROW
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.VIDEORESIZE:
            current_w = event.w
            current_h = event.h
        if event.type == pygame.QUIT:
            running = False

    screen.fill(colors["background"])

    # ボーダー
    border_y = current_h * border_position
    pygame.draw.line(
        screen,
        colors["border"],
        (0, border_y),
        (current_w, border_y),
        6,
    )
    if border_y - 5 < pygame.mouse.get_pos()[1] < border_y + 5:
        cursor = pygame.SYSTEM_CURSOR_SIZENS
        if pygame.mouse.get_pressed()[0]:
            border_y = pygame.mouse.get_pos()[1]
            border_position = border_y / current_h

    # プレビュー
    preview_height = current_h * border_position - 3
    preview_width = preview_height / screen_height * screen_width
    pygame.draw.rect(
        screen,
        colors["preview_bg"],
        pygame.Rect(
            current_w / 2 - preview_width / 2, 0, preview_width, preview_height
        ),
    )

    # タイムライン
    pygame.draw.rect(
        screen,
        colors["tl_side_bg"],
        pygame.Rect(0, border_y + 4, 200, current_h - border_y - 4),
    )

    pygame.mouse.set_cursor(cursor)
    pygame.display.flip()
