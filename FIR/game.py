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
    global bitset
    x = (position[0] - w1) / width
    y = (position[1] - w1) / width
    if x >= 0 or x <= count or y >= 0 or y <= count:
        bitset[x][y] = '+'

pygame.init()
fpsClock = pygame.time.Clock()

width, count = 60, 12
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
            for x, y in ((6, 6), (6, 5), (5, 6), (5, 5)):
                if bitset[x][y] == 'o':
                    turn = 'player'
                    bitset[x][y] = '*'
                    break
        else:
            computer_played, ret_x, ret_y = get_data()
            if computer_played:
                turn = 'player'
                bitset[ret_x][ret_y] = '*'

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
            if left:
                if turn == 'player':
                    turn = 'computer'
                    handleClick(position)
                    searchThread(bitset, count).start()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
