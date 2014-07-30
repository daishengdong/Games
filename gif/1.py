# -*- coding: utf-8 -*-
import pygame
from math import cos, sin, pi

def drawBigCircle():
    red_color = pygame.Color(255, 0, 0)
    pygame.draw.circle(screen, red_color, (radius, radius),  radius)

'''
def getvector_impl(n):
    angle = math.pi / 8.
    x = math.sqrt(radius * radius / (1. + math.tan(angle * n) * math.tan(angle * n)))
    y = math.tan(angle * n) * x
    # 返回直线向量
    # 起始点相减
    # (x, y) - (-x, -y)
    return ((x + radius, y + radius), (2 * x, 2 * y))

def getvector():
    global vector
    vector.append(((-radius + radius, 0 + radius), (2 * radius, 0)))
    vector.extend(map(getvector_impl, range(1, 4)))
    vector.append(((0 + radius, -radius + radius), (0, 2 * radius)))
    vector.extend(map(getvector_impl, range(5, 8)))

def divTuple(((x_original, y_original), (x, y)), n):
    return (int(x_original + math.ceil(x * n / 10.)), int(y_original + math.ceil(y * n / 10.)))

def drawSmallCircle():
    global cur, turn
    white_color = pygame.Color(255, 255, 255)
    # 向量的 1 / cur 处
    points = map(lambda point: divTuple(point, cur), vector)
    print points
    for point in points:
        pygame.draw.circle(screen, white_color, point, 15)

    if turn == 0:
        cur += 1
        if cur == 10:
            turn = 1
    else:
        cur -= 1
        if cur == 0:
            turn = 0
'''

def drawSmallCircle():
    global turn, time

    points = map(lambda i: (int(radius + radius * cos(i * pi / 8) * sin(time + i * pi /8)), int(radius + radius * sin(i * pi / 8) * sin(time + i * pi /8))), range(0, 8))
    white_color = pygame.Color(255, 255, 255)

    for point in points:
        pygame.draw.circle(screen, white_color, point, 15)

    if turn == 0:
        time += 0.5
        if time == 2 * pi:
            turn = 1
    else:
        time -= 0.5
        if time == 0:
            turn = 0
                
pygame.init()
fpsClock = pygame.time.Clock()

radius = 250
vector = []
screen = pygame.display.set_mode((radius * 2, radius * 2))
pygame.display.set_caption('GIF')

back_color = pygame.Color(100, 100, 255)
black_color = pygame.Color(0, 0, 0)

cur, time, turn = 0, 0, 1

running = True

# getvector()
while running:
    screen.fill(back_color)
    drawBigCircle()
    drawSmallCircle()

    pygame.display.flip()
    pygame.display.update()
    fpsClock.tick(10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
