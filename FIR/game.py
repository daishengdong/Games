# -*- coding: utf-8 -*-

import thread
import pygame
from pygame.locals import *
import random

from AI import searchThread, get_data

def drawFrame():
    frame_color = pygame.Color(200, 200, 200)
    pygame.draw.line(screen, frame_color, (w1, w1), (w1 + 2 * w2 + count * width, w1), 3)
    pygame.draw.line(screen, frame_color, (w1 + 2 * w2 + count * width, w1), (w1 + 2 * w2 + count * width, w1 + 2 * w2 + count * width), 3)
    pygame.draw.line(screen, frame_color, (w1 + 2 * w2 + count * width, w1 + 2 * w2 + count * width), (w1, w1 + 2 * w2 + count * width), 3)
    pygame.draw.line(screen, frame_color, (w1, w1 + 2 * w2 + count * width), (w1, w1), 3)

    for i in xrange(count + 1):
        row_x1, row_y1 = w1 + w2, w1 + w2 + i * width
        row_x2, row_y2 = w1 + w2 + count * width, w1 + w2 + i * width
        pygame.draw.line(screen, frame_color, (row_x1, row_y1), (row_x2, row_y2), 3)

        column_x1, column_y1 = w1 + w2 + i * width, w1 + w2
        column_x2, column_y2 = w1 + w2 + i * width, w1 + w2 + count * width
        pygame.draw.line(screen, frame_color, (column_x1, column_y1), (column_x2, column_y2), 3)

def drawChessBoard():
    global bitset
    for x in xrange(count + 1):
        for y in xrange(count + 1):
            # * for white chess; + for black chess
            # white: computer; black: player
            if bitset[x][y] == '*':
                pygame.draw.circle(screen, white_color, (w1 + w2 + x * width, w1 + w2 + y * width), w2 / 2)
            elif bitset[x][y] == '+':
                pygame.draw.circle(screen, black_color, (w1 + w2 + x * width, w1 + w2 + y * width), w2 / 2)
                
def handleClick(position):
    global bitset, running
    x = (position[0] - w1) / width
    y = (position[1] - w1) / width
    if x >= 0 or x <= count or y >= 0 or y <= count:
        if bitset[x][y] == 'o':
            bitset[x][y] = '+'
            running = not is_game_over((x, y), False)

def is_game_over((x, y), is_computer=True):
    # 横
    layout_points = [(x + i, y) for i in xrange(-4, 5)]
    # 在这里边界用 % 代替，因为只要判断是否有 5 个连起来的就行了
    layout = ''.join(map(lambda (x, y): '%' if x < 0 or x > count or y < 0 or y > count else bitset[x][y], layout_points))
    if is_computer:
        if '*****' in layout:
            return True
    else:
        if '+++++' in layout:
            return True
    # 纵
    layout_points = [(x, y + i) for i in xrange(-4, 5)]
    layout = ''.join(map(lambda (x, y): '%' if x < 0 or x > count or y < 0 or y > count else bitset[x][y], layout_points))
    if is_computer:
        if '*****' in layout:
            return True
    else:
        if '+++++' in layout:
            return True
    # 正斜 \
    layout_points = [(x + i, y + i) for i in xrange(-4, 5)]
    layout = ''.join(map(lambda (x, y): '%' if x < 0 or x > count or y < 0 or y > count else bitset[x][y], layout_points))
    if is_computer:
        if '*****' in layout:
            return True
    else:
        if '+++++' in layout:
            return True
    # 反斜 /
    layout_points = [(x + i, y - i) for i in xrange(-4, 5)]
    layout = ''.join(map(lambda (x, y): '%' if x < 0 or x > count or y < 0 or y > count else bitset[x][y], layout_points))
    if is_computer:
        if '*****' in layout:
            return True
    else:
        if '+++++' in layout:
            return True
    return False

pygame.init()
fpsClock = pygame.time.Clock()

width, count = 60, 10
w1, w2 = 5, width / 2
bitset = [['o' for _ in xrange(count + 1)] for _ in xrange(count + 1)]
screen = pygame.display.set_mode((2 * w1 + 2 * w2 + count * width, 2 * w1 + 2 * w2 + count * width))
pygame.display.set_caption('FIR')

back_color = pygame.Color(100, 100, 255)
white_color = pygame.Color(255, 255, 255)
black_color = pygame.Color(0, 0, 0)

running = True
first_step = True

turn = 'player'

while running:
    screen.fill(back_color)
    drawFrame()
    drawChessBoard()

    if turn == 'computer':
        if first_step:
            first_step = False
            for x, y in ((count / 2, count / 2), (count / 2, count / 2 - 1), (count / 2 - 1, count / 2), (count / 2 - 1, count / 2 - 1)):
                if bitset[x][y] == 'o':
                    turn = 'player'
                    bitset[x][y] = '*'
                    break
        else:
            computer_played, ret_x, ret_y = get_data()
            if computer_played:
                bitset[ret_x][ret_y] = '*'
                running = not is_game_over((ret_x, ret_y))
                turn = 'player'
                pygame.mouse.set_visible(True)

    pygame.display.flip()
    pygame.display.update()
    fpsClock.tick(30)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            left = pygame.mouse.get_pressed()[0]
            right = pygame.mouse.get_pressed()[2]
            position = pygame.mouse.get_pos()
            if left and turn == 'player':
                turn = 'computer'
                handleClick(position)
                if not first_step:
                    searchThread(bitset, count).start()
                    pygame.mouse.set_visible(False)

while True:
    screen.fill(back_color)
    drawFrame()
    drawChessBoard()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
