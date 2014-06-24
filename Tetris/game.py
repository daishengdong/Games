import pygame
from pygame.locals import *
import math
import random

class Brick():
    def __init__(self, p_position, p_color):
        self.position = p_position
        self.color = p_color
        self.image = pygame.Surface([brick_width, brick_height])
        self.image.fill(self.color)
    
    def draw(self):
        screen.blit(self.image, (self.position[0] * brick_width, self.position[1] * brick_height))

class Block():
    def __init__(self, p_bricks_layout, p_direction, p_color):
        self.bricks_layout = p_bricks_layout
        self.direction = p_direction
        self.cur_layout = self.bricks_layout[self.direction]
        self.position = cur_block_init_position
        self.stopped = False
        self.move_interval = 800
        self.bricks = []
        for (x, y) in self.cur_layout:
            self.bricks.append(Brick(
                (self.position[0] + x, self.position[1] + y),
                p_color))

    def setPosition(self, position):
        self.position = position
        self.refresh_bircks()

    def draw(self):
        for brick in self.bricks:
            brick.draw()

    def isLegal(self, layout, position):
        (x0, y0) = position
        for (x, y) in layout:
            if x + x0 < 0 or y + y0 < 0 or x + x0 >= field_width or y + y0 >= field_height:
                return False
            if field_map[y + y0][x + x0] != 0:
                return False
        return True

    def left(self):
        new_position = (self.position[0] - 1, self.position[1])
        if self.isLegal(self.cur_layout, new_position):
            self.position = new_position
            self.refresh_bircks()

    def right(self):
        new_position = (self.position[0] + 1, self.position[1])
        if self.isLegal(self.cur_layout, new_position):
            self.position = new_position
            self.refresh_bircks()

    def down(self):
        (x, y) = (self.position[0], self.position[1] + 1)
        while self.isLegal(self.cur_layout, (x, y)):
            self.position = (x, y)
            self.refresh_bircks()
            y += 1

    def refresh_bircks(self):
        for (brick, (x, y)) in zip(self.bricks, self.cur_layout):
            brick.position = (self.position[0] + x, self.position[1] + y)

    def stop(self):
        global field_bricks
        global score
        self.stopped = True
        ys = []
        for brick in self.bricks:
            field_bricks.append(brick)
            (x, y) = brick.position
            if y not in ys:
                ys.append(y)
            field_map[y][x] = 1

        eliminate_count = 0
        ys.sort()
        for y in ys:
            if 0 in field_map[y]:
                continue
            eliminate_count += 1
            for fy in xrange(y, 0, -1):
                field_map[fy] = field_map[fy - 1][:]
            field_map[0] = [0 for i in xrange(field_width)]

            tmp_field_bricks = []
            for fb in field_bricks:
                (fx, fy) = fb.position
                if fy < y:
                    fb.position = (fx, fy + 1)
                    tmp_field_bricks.append(fb)
                elif fy > y:
                    tmp_field_bricks.append(fb)
            field_bricks = tmp_field_bricks
        if eliminate_count == 1:
            score += 1
        elif eliminate_count == 2:
            score += 2
        elif eliminate_count == 3:
            score += 4
        elif eliminate_count == 4:
            score += 6
        '''
        attention: the code below does not work
        index = 0
        for fb in field_bricks:
            if fb.y < y:
                fb.y += 1
            elif fb.y == y:
                field_bricks.pop(index)
            index += 1
            '''

    def update(self, time):
        global last_move
        self.draw()
        if last_move == -1 or time - last_move >= self.move_interval:
            new_position = (self.position[0], self.position[1] + 1)
            if self.isLegal(self.cur_layout, new_position):
                self.position = new_position
                self.refresh_bircks()
                last_move = time
            else:
                self.stop()

    def rotate(self):
        new_direction = (self.direction + 1) % len(self.bricks_layout)
        new_layout = self.bricks_layout[new_direction]
        if not self.isLegal(new_layout, self.position):
            return
        self.direction = new_direction
        self.cur_layout = new_layout
        for (brick, (x, y)) in zip(self.bricks, self.cur_layout):
            brick.position = (self.position[0] + x, self.position[1] + y)
        self.refresh_bircks()
        self.draw()

def drawField():
    for brick in field_bricks:
        brick.draw()

def drawInfoPanel():
    font = pygame.font.Font("resources/fonts/MONACO.TTF", 18)
    survivedtext = font.render('score: ' + str(score), True, (255, 255, 255))
    textRect = survivedtext.get_rect()
    textRect.topleft = ((field_width + 2) * brick_width, 10)
    screen.blit(survivedtext, textRect)

    next_block.draw()

def drawFrame():
    frame_color = pygame.Color(200, 200, 200)
    pygame.draw.line(screen, frame_color, (field_width * brick_width, field_height * brick_height), (field_width * brick_width, 0), 3)

def getBlock():
    block_type = random.randint(0, 6)
    if block_type == 0:
        return Block(bricks_layout_0, random.randint(0, len(bricks_layout_0) - 1), colors_for_bricks[0])
    elif block_type == 1:
        return Block(bricks_layout_1, random.randint(0, len(bricks_layout_1) - 1), colors_for_bricks[1])
    elif block_type == 2:
        return Block(bricks_layout_2, random.randint(0, len(bricks_layout_2) - 1), colors_for_bricks[2])
    elif block_type == 3:
        return Block(bricks_layout_3, random.randint(0, len(bricks_layout_3) - 1), colors_for_bricks[3])
    elif block_type == 4:
        return Block(bricks_layout_4, random.randint(0, len(bricks_layout_4) - 1), colors_for_bricks[4])
    elif block_type == 5:
        return Block(bricks_layout_5, random.randint(0, len(bricks_layout_5) - 1), colors_for_bricks[5])
    elif block_type == 6:
        return Block(bricks_layout_6, random.randint(0, len(bricks_layout_6) - 1), colors_for_bricks[6])

# 0: oooo
# 1: oo
#    oo
# 2: o
#   ooo
# 3: o
#    oo
#     o
# 4:  o
#    oo
#    o
# 5: ooo
#    o
# 6: ooo
#      o
bricks_layout_0 = (
        ((0, 0), (0, 1), (0, 2), (0, 3)),
        ((0, 1), (1, 1), (2, 1), (3, 1)))
bricks_layout_1 = (
        ((1, 0), (2, 0), (1, 1), (2, 1)),
        )
bricks_layout_2 = (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((0, 1), (1, 0), (1, 1), (1, 2)),
        ((1, 2), (0, 1), (1, 1), (2, 1)),
        ((2, 1), (1, 0), (1, 1), (1, 2)),
        )
bricks_layout_3 = (
        ((0, 1), (1, 1), (1, 0), (2, 0)),
        ((0, 0), (0, 1), (1, 1), (1, 2)),
        )
bricks_layout_4 = (
        ((0, 0), (1, 0), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (0, 1), (0, 2)),
        )
bricks_layout_5 = (
        ((0, 0), (1, 0), (1, 1), (1, 2)),
        ((0, 2), (0, 1), (1, 1), (2, 1)),
        ((1, 0), (1, 1), (1, 2), (2, 2)),
        ((2, 0), (2, 1), (1, 1), (0, 1)),
        )
bricks_layout_6 = (
        ((2, 0), (1, 0), (1, 1), (1, 2)),
        ((0, 0), (0, 1), (1, 1), (2, 1)),
        ((0, 2), (1, 2), (1, 1), (1, 0)),
        ((2, 2), (2, 1), (1, 1), (0, 1)),
        )

colors_for_bricks = (
        pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255),
        pygame.Color(100, 100, 100), pygame.Color(120, 200, 0), pygame.Color(100, 0, 200),
        pygame.Color(10, 100, 30))

field_width, field_height = 12, 17
cur_block_init_position = (4, 0)
info_panel_width = 8
next_block_init_position = (field_width + 3, 5)
field_map = [[0 for i in xrange(field_width)] for i in xrange(field_height)]

game_over_img = pygame.image.load("resources/images/game_over.gif")

running = True
score = 0
brick_width, brick_height = 30, 30
field_bricks = []

next_block = None
last_move = -1

pygame.init()
screen = pygame.display.set_mode(((field_width + info_panel_width) * brick_width, field_height * brick_height), 0, 32)
pygame.display.set_caption('Tetris')

while running:
    if next_block == None:
        cur_block = getBlock()
    else:
        cur_block = next_block
        cur_block.setPosition(cur_block_init_position)
    next_block = getBlock()
    next_block.setPosition(next_block_init_position)

    if not cur_block.isLegal(cur_block.cur_layout, cur_block.position):
        cur_block.draw()
        running = False
        continue
    while not cur_block.stopped:
        screen.fill(0)
        drawFrame()
        time = pygame.time.get_ticks()
        cur_block.update(time)
        drawField()
        drawInfoPanel()

        pygame.display.flip()
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit(0)
            if event.type == pygame.KEYDOWN:
                if event.key == K_w or event.key == K_UP:
                    cur_block.rotate()
                    last_move = time
                elif event.key == K_a or event.key == K_LEFT:
                    cur_block.left()
                elif event.key == K_d or event.key == K_RIGHT:
                    cur_block.right()
                elif event.key == K_s or event.key == K_DOWN:
                    cur_block.down()
                    last_move = time - 500

screen.blit(game_over_img, (field_width / 2 * brick_width, (field_height / 2 - 2) * brick_height))

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
