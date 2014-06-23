import os
import pygame
from pygame.locals import *
import random

def drawFrame():
    frame_color = pygame.Color(200, 200, 200)
    pygame.draw.line(screen, frame_color, (0, 0), (164, 0), 3)
    pygame.draw.line(screen, frame_color, (164, 0), (164, 217), 3)
    pygame.draw.line(screen, frame_color, (164, 217), (0, 217), 3)
    pygame.draw.line(screen, frame_color, (0, 217), (0, 0), 3)
    pygame.draw.line(screen, frame_color, (10, 10), (154, 10), 3)
    pygame.draw.line(screen, frame_color, (154, 10), (154, 53), 3)
    pygame.draw.line(screen, frame_color, (154, 53), (10, 53), 3)
    pygame.draw.line(screen, frame_color, (10, 53), (10, 10), 3)
    pygame.draw.line(screen, frame_color, (10, 63), (154, 63), 3)
    pygame.draw.line(screen, frame_color, (154, 63), (154, 207), 3)
    pygame.draw.line(screen, frame_color, (154, 207), (10, 207), 3)
    pygame.draw.line(screen, frame_color, (10, 207), (10, 63), 3)

def initBlockBitset():
    global block_bitset
    # [False, False, 0, 9]: 
    # 1. False: not clicked yet
    # 2. False: not a mine
    # 3.
        # 0: none
        # 1: marked as mine
        # 2: marked as wonder
    # 4. 9: counts of mines surround
    block_bitset = [[[False, False, False, 9] for _ in xrange(9)] for _ in xrange(9)]

    random_pos = []
    for remain in xrange(10, 0, -1):
        pos = random.randint(1, 81 - remain)
        if pos not in random_pos:
            random_pos.append(pos)
        else:
            random_pos.append(81 - remain)

    for pos in random_pos:
        x = pos / 9
        y = pos % 9
        block_bitset[x][y][1] = True
        block_bitset[x][y][3] = 10

    for i in xrange(9):
        for j in xrange(9):
            counts_of_mine_surround = 0
            if block_bitset[i][j][1] == True:
                continue
            for deltax in xrange(-1, 2, 1):
                for deltay in xrange(-1, 2, 1):
                    x = i + deltax
                    y = j + deltay
                    if x < 0 or x > 8 or y <0 or y > 8:
                        continue
                    if block_bitset[x][y][1] == True:
                        counts_of_mine_surround += 1

            block_bitset[i][j][3] = counts_of_mine_surround

def drawContinueBlocks():
    for i in xrange(9):
        for j in xrange(9):
            if block_bitset[i][j][2] == 0 and block_bitset[i][j][0] == False:
                screen.blit(blocks[9], (10 + 16 * i, 63 + 16 * j))
            elif block_bitset[i][j][2] == 1:
                screen.blit(blocks[13], (10 + 16 * i, 63 + 16 * j))
            elif block_bitset[i][j][2] == 2:
                screen.blit(blocks[14], (10 + 16 * i, 63 + 16 * j))
            elif block_bitset[i][j][0] == False:
                screen.blit(blocks[9], (10 + 16 * i, 63 + 16 * j))
            else:
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))

def drawSuccess():
    for i in xrange(9):
        for j in xrange(9):
            if block_bitset[i][j][1] == True:
                screen.blit(blocks[10], (10 + 16 * i, 63 + 16 * j))
            else: 
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))

def drawFail((x, y)):
    for i in xrange(9):
        for j in xrange(9):
            flag_mine = block_bitset[i][j][1]
            flag_marked = block_bitset[i][j][2]
            if i == x and j == y:
                screen.blit(blocks[12], (10 + 16 * i, 63 + 16 * j))
                continue
            if flag_mine == False and flag_marked == True:
                screen.blit(blocks[11], (10 + 16 * i, 63 + 16 * j))
            elif flag_mine == True:
                screen.blit(blocks[10], (10 + 16 * i, 63 + 16 * j))
            else:
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))

def expandBlank((x, y)):
    global remain_blocks_count
    position_queue = [(x, y)]
    for position in position_queue:
        for deltax in xrange(-1, 2, 1):
            for deltay in xrange(-1, 2, 1):
                new_x = position[0] + deltax
                new_y = position[1] + deltay
                if new_x == x and new_y == y:
                    continue
                if new_x < 0 or new_x > 8 or new_y < 0 or new_y > 8:
                    continue
                if block_bitset[new_x][new_y][0] == True:
                    continue

                block_bitset[new_x][new_y][0] = True
                block_bitset[new_x][new_y][2] = 0
                remain_blocks_count -= 1
                if block_bitset[new_x][new_y][3] == 0:
                    position_queue.append((new_x, new_y))

def handleClick(position, right):
    global running
    global mines_count
    global remain_blocks_count

    x = (position[0] - 10) / 16
    y = (position[1] - 63) / 16
    if x < 0 or x > 8 or y <0 or y > 8:
        return

    if block_bitset[x][y][0] == True:
        return

    if right == False:
        if block_bitset[x][y][2] == 0:
            block_bitset[x][y][2] = 1
        elif block_bitset[x][y][2] == 1:
            block_bitset[x][y][2] = 2
        else:
            block_bitset[x][y][2] = 0
        return

    if block_bitset[x][y][1] == True:
        drawFail((x, y))
        running = False
        return
    remain_blocks_count -= 1
    block_bitset[x][y][0] = True
    block_bitset[x][y][2] = 0
    if block_bitset[x][y][3] == 0:
        expandBlank((x, y))
    if remain_blocks_count == mines_count:
        drawSuccess()
        running = False

def drawNumber(number, time):
    number0 = number / 100 % 10
    number1 = number / 10 % 10
    number2 = number % 10

    time0 = time / 100 % 10
    time1 = time / 10 % 10
    time2 = time % 10

    screen.blit(number_blocks[number0], (20, 20))
    screen.blit(number_blocks[number1], (33, 20))
    screen.blit(number_blocks[number2], (46, 20))

    screen.blit(number_blocks[time0], (105, 20))
    screen.blit(number_blocks[time1], (118, 20))
    screen.blit(number_blocks[time2], (131, 20))

pygame.init()
width, height = 164, 217 
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Minesweeper')
white_color = pygame.Color(255, 255, 255)

# blocks[i = 0 : 8]: i mines arround
# blocks[9]: blank block
# blocks[10]: mine, marked correctly
# blocks[11]: mine, marked falsely
# blocks[12]: mine, blow up
# blocks[13]: flag
# blocks[14]: wonder
block_names = [os.path.join("resources", "images", str(x) + ".bmp") for x in xrange(15)]
blocks = [pygame.image.load(block_name) for block_name in block_names]

number_block_names = [os.path.join("resources", "images", "d" + str(x) + ".bmp") for x in xrange(10)]
number_blocks = [pygame.image.load(number_block_name) for number_block_name in number_block_names]

currend_second = 0
last_second = currend_second
block_bitset = []
mines_count = 10
remain_blocks_count = 9 * 9
running = True
initBlockBitset()

while running:
    screen.fill(white_color)
    drawFrame()
    drawNumber(mines_count, currend_second)
    drawContinueBlocks()
    pygame.display.flip()
    currend_second = pygame.time.get_ticks() / 1000
    if currend_second != last_second:
        last_second = currend_second
    else:
        currend_second = last_second
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            right = pygame.mouse.get_pressed()[0]
            left = pygame.mouse.get_pressed()[2]
            position = pygame.mouse.get_pos()
            if right:
                handleClick(position, True)
            elif left:
                handleClick(position, False)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
