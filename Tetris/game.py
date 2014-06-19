import pygame
from pygame.locals import *
import math
import random

class Brick():
    brick = Brick()
    def __init__(self, p_position, p_color):
        self.position = p_position
        self.color = p_color
        self.image = pygame.Surface([self.width, self.height])
        self.image.fill(self.color)

    def getBrick(self):
        return brick
    
    def draw(self):
        screen.blit(self.image, (self.position[0] * brick_width, self.position[1] * brick_height))

class Block():
    def __init__(self, p_bricks_layout, p_direction, p_color):
        self.bricks_layout = p_bricks_layout
        self.direction = p_direction
        self.cur_layout = self.bricks_layout[self.direction]
        self.position = init_position
        self.bricks = []
        for (x, y) in self.cur_layout:
            self.bricks.append(Brick(
                (self.position[0] + x, self.position[1] + y),
                p_color))

    def draw(self):
        for brick in self.bricks:
            brick.draw()

    def rotate_clockwise(self):
        self.direction += 1
        if self.direction >= len(self.bricks_layout):
            self.direction = 0
        self.cur_layout = self.bricks_layout[p_direction]
        for (brick, (x, y)) in zip(self,bricks, self.cur_layout):
            brick.position = (self.position[0] + x, self.position[1] + y)

def drawField():
    for row in field:
        for (b_type, color) in row:
            if b_type == 1:
            image = pygame.Surface([brick_width, brick_height])
            image.fill(color)
            screen.blit(self.image, (x * brick_width, y * brick_height))

def getBlock(block_type):
    # block_type = random.randint(0, 6)
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
        ((1, 0), (1, 1), (1, 2), (1, 3)),
        ((0, 1), (1, 1), (2, 1), (2, 1)))
bricks_layout_1 = (
        ((0, 0), (1, 0), (1, 1), (1, 0))
        )
bricks_layout_2 = (
        ((1, 0), (0, 1), (1, 1), (2, 1)),
        ((0, 1), (1, 0), (1, 1), (1, 2)),
        ((1, 2), (0, 1), (1, 1), (2, 1)),
        ((2, 1), (0, 1), (1, 1), (1, 2)),
        )
bricks_layout_3 = (
        ((0, 1), (1, 1), (1, 0), (2, 0)),
        ((1, 0), (1, 1), (2, 1), (2, 2)),
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
        ((2, 2), (2, 1), (1, 1), (2, 1)),
        )

colors_for_bricks = (
        pygame.Color(255, 0, 0), pygame.Color(0, 255, 0), pygame.Color(0, 0, 255),
        pygame.Color(100, 100, 100), pygame.Color(120, 200, 0), pygame.Color(100, 0, 200))

field_width = 15
field_height = 20
brick_width = 30
brick_height = 30
field = [[[0, pygame.Color(0, 0, 0)] for i in xrange(field_width)] for i in xrange(field_height)]
init_position = [5, 0]

pygame.init()
screen = pygame.display.set_mode((field_width * brick_width, field_height * brick_height), 0, 32)

running = True
game_over = False

while running:
    drawField()
    block = getBlock(5)
    block.draw()

    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                block.rotate_clockwise()
            elif event.key == K_a or event.key == K_LEFT:
                pass
            elif event.key == K_s or event.key == K_DOWN:
                pass
            elif event.key == K_d or event.key == K_RIGHT:
                pass

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
