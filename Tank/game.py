import pygame
from pygame.locals import *
import math
import random

def expand_battle_field():
    for row in small_battle_field:
        new_row = []
        for column in row:
            new_row.extend([column] * 2)
        battle_field.append(new_row)
        battle_field.append(new_row[:])

def area_conflict(area1, area2):
    for point1 in area1:
        if point1 in area2:
            return True
    return False

def draw_battle_field():
    global symbol_position
    global symbol_area
    for row_index in range(y_max):
        for column_index in range(x_max):
            if battle_field[row_index][column_index] == 1:
                # is a brick_wall
                screen.blit(brick_wall_img, (column_index * 30, row_index * 30))
            if battle_field[row_index][column_index] == 2:
                # is a cement_wall
                screen.blit(cement_wall_img, (column_index * 30, row_index * 30))
            if symbol_position != None:
                continue
            if battle_field[row_index][column_index] == 3:
                # is a symbol
                symbol_position = (column_index, row_index)
                symbol_area = (
                        (column_index, row_index),
                        (column_index + 1, row_index),
                        (column_index, row_index + 1),
                        (column_index + 1, row_index + 1))
    if game_over:
        screen.blit(symbol_destoryed_img, (symbol_position[0] * 30, symbol_position[1] * 30))
    else:
        screen.blit(symbol_img, (symbol_position[0] * 30, symbol_position[1] * 30))

def produce_enemy(time):
    global last_product
    global enemys_cur_number
    if last_product != -1 and time - last_product < enemys_product_interval:
        return
    index_e = random.randint(0, 1)
    conflict = False
    for point in tank.area:
        if point in enemy_init_area[index_e]:
            conflict = True
            break

    if not conflict:
        for enemy in enemys:
            for point_e in enemy.area:
                if point_e in enemy_init_area[index_e]:
                    conflict = True
                    break
            if conflict:
                break;

    if not conflict:
        enemys.append(Enemy(enemy_init_position[index_e]))
        last_product = time
        enemys_cur_number += 1
        return

    for point in tank.area:
        if point in enemy_init_area[1 - index_e]:
            return

    for enemy in enemys:
        for point_e in enemy.area:
            if point_e in enemy_init_area[1 - index_e]:
                return

    enemys.append(Enemy(enemy_init_position[1 - index_e]))
    last_product = time
    enemys_cur_number += 1

class ArmoredCar():
    def __init__(self, p_position, p_direction, p_image, p_fire_interval):
        self.position = p_position
        self.area = (
            (self.position[0], self.position[1]),
            (self.position[0] + 1, self.position[1]),
            (self.position[0], self.position[1] + 1),
            (self.position[0] + 1, self.position[1] + 1))
        self.direction = p_direction
        self.image = p_image 
        self.missiles = []

        self.destroyed = False

        self.last_fire = -1
        self.fire_interval = p_fire_interval 

    def draw(self):
        screen.blit(self.image, (self.position[0] * 30, self.position[1] * 30))

    def is_legal(self, new_area):
        for (x, y) in new_area:
            if x < 0 or y < 0 or x >= x_max or y >= y_max:
                return False
            if battle_field[y][x] != 0:
                return False

        for enemy in enemys:
            if enemy == self:
                continue
            if area_conflict(enemy.area, new_area):
                return False
        if isinstance(self, Enemy) and area_conflict(self.area, tank.area):
            return False

        return True

    def update(self):
        self.draw()
        index = 0
        for missile in self.missiles:
            if missile.update() == False:
                self.missiles.pop(index)
            index += 1

    def up(self):
        self.direction = 'U'
        if isinstance(self, Tank):
            self.image = tank_img_U
        else:
            self.image = enemy_img_U 
        new_position = (self.position[0], self.position[1] - 1)
        new_area = (
            (new_position[0], new_position[1]),
            (new_position[0] + 1, new_position[1]),
            (new_position[0], new_position[1] + 1),
            (new_position[0] + 1, new_position[1] + 1))
        if self.is_legal(new_area):
            self.position = new_position
            self.area = new_area
    
    def down(self):
        self.direction = 'D'
        if isinstance(self, Tank):
            self.image = tank_img_D
        else:
            self.image = enemy_img_D
        new_position = (self.position[0], self.position[1] + 1)
        new_area = (
            (new_position[0], new_position[1]),
            (new_position[0] + 1, new_position[1]),
            (new_position[0], new_position[1] + 1),
            (new_position[0] + 1, new_position[1] + 1))
        if self.is_legal(new_area):
            self.position = new_position
            self.area = new_area

    def right(self):
        self.direction = 'R'
        if isinstance(self, Tank):
            self.image = tank_img_R
        else:
            self.image = enemy_img_R
        new_position = (self.position[0] + 1, self.position[1])
        new_area = (
            (new_position[0], new_position[1]),
            (new_position[0] + 1, new_position[1]),
            (new_position[0], new_position[1] + 1),
            (new_position[0] + 1, new_position[1] + 1))
        if self.is_legal(new_area):
            self.position = new_position
            self.area = new_area

    def left(self):
        self.direction = 'L'
        if isinstance(self, Tank):
            self.image = tank_img_L
        else:
            self.image = enemy_img_L
        new_position = (self.position[0] - 1, self.position[1])
        new_area = (
            (new_position[0], new_position[1]),
            (new_position[0] + 1, new_position[1]),
            (new_position[0], new_position[1] + 1),
            (new_position[0] + 1, new_position[1] + 1))
        if self.is_legal(new_area):
            self.position = new_position
            self.area = new_area

    def fire(self, time):
        if self.last_fire == -1 or time - self.last_fire >= self.fire_interval:
            self.last_fire = time
            if isinstance(self, Tank):
                self.missiles.append(TankMissile(self.direction, self.position))
            else:
                self.missiles.append(EnemyMissile(self.direction, self.position))

class Tank(ArmoredCar):
    def __init__(self):
        ArmoredCar.__init__(self, tank_init_position, 'U', tank_img_U, 300)
        self.life = 3
        # for future use
        self.buf = []

    def attacked(self):
        self.direction = 'U'
        self.image = tank_img_U
        self.position = tank_init_position
        self.life -= 1
        if self.life == 0:
            self.destroyed = True

    def update(self):
        self.draw()
        index = 0
        for missile in self.missiles:
            if missile.update() == False:
                self.missiles.pop(index)
            index += 1

class Enemy(ArmoredCar):
    def __init__(self, p_init_position):
        ArmoredCar.__init__(self, p_init_position, 'D', enemy_img_D, 800)
        # for future use

        self.damaged = 0
        self.limitation = 1
        self.move_interval = 1000
        self.last_move = -1

    def attacked(self, damage):
        self.damaged += damage
        if self.damaged >= self.limitation:
            self.destroyed = True

    def update(self, time):
        self.fire(time)
        index = 0
        for missile in self.missiles:
            if missile.update() == False:
                self.missiles.pop(index)
            index += 1
        self.draw()

        if self.last_move != -1 and time - self.last_move < self.move_interval:
            return
        self.last_move = time
        self.direction = ('D', 'D', 'D', 'D', 'D', 'R', 'R', 'L', 'L', 'U')[random.randint(0, 9)]
        if self.direction == 'U':
            self.up()
        elif self.direction == 'D':
            self.down()
        elif self.direction == 'R':
            self.right()
        elif self.direction == 'L':
            self.left()

class Missile():
    def __init__(self, direction, p_position, image):
        self.image = image

        self.direction = direction
        self.speed = 0.3
        self.damage = 10

        missile_img_width = self.image.get_width()
        missile_img_height = self.image.get_height()
        if self.direction == 'U':
            self.position = [
                    p_position[0] * 30 + 30 - missile_img_width / 2,
                    p_position[1] * 30 - missile_img_height]
        elif self.direction == 'D':
            self.position = [
                    p_position[0] * 30 + 30 - missile_img_width / 2,
                    p_position[1] * 30 + 60]
        elif self.direction == 'R':
            self.position = [
                    p_position[0] * 30 + 60,
                    p_position[1] * 30 + 30 - missile_img_height / 2]
        elif self.direction == 'L':
            self.position = [
                    p_position[0] * 30 - missile_img_width,
                    p_position[1] * 30 + 30 - missile_img_height / 2]

        # for future use
        self.damage = 1

    def draw(self):
        screen.blit(self.image, (self.position[0], self.position[1]))

class TankMissile(Missile):
    def __init__(self, direction, p_position):
        Missile.__init__(self, direction, p_position, tank_missile_img)

    def update(self):
        global symbol_attacked
        if self.direction == 'U':
            self.position[1] -= self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x + 1, y))
        elif self.direction == 'D':
            self.position[1] += self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x + 1, y))
        elif self.direction == 'R':
            self.position[0] += self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x, y + 1))
        elif self.direction == 'L':
            self.position[0] -= self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x, y + 1))

        x = int(self.position[0] / 30)
        y = int(self.position[1] / 30)

        if self.area[0][0] < 0 or self.area[0][1] < 0 or self.area[0][0] >= x_max or self.area[0][1] >= y_max:
            return False

        if self.area[1][0] < 0 or self.area[1][1] < 0 or self.area[1][0] >= x_max or self.area[1][1] >= y_max:
            return False

        if battle_field[self.area[0][1]][self.area[0][0]] == 1:
            battle_field[self.area[0][1]][self.area[0][0]] = 0
            return False

        if battle_field[self.area[1][1]][self.area[1][0]] == 1:
            battle_field[self.area[1][1]][self.area[1][0]] = 0
            return False

        if battle_field[self.area[0][1]][self.area[0][0]] == 2:
            return False
        if battle_field[self.area[1][1]][self.area[1][0]] == 2:
            return False

        for enemy in enemys:
            if area_conflict(enemy.area, self.area):
                enemy.attacked(self.damage)
                hit_msc.play()
                return False

        if area_conflict(symbol_area, self.area):
            symbol_attacked += 1
            return False

        self.draw()

class EnemyMissile(Missile):
    def __init__(self, direction, p_position):
        Missile.__init__(self, direction, p_position, enemy_missile_img)

    def update(self):
        global symbol_attacked
        if self.direction == 'U':
            self.position[1] -= self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x + 1, y))
        elif self.direction == 'D':
            self.position[1] += self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x + 1, y))
        elif self.direction == 'R':
            self.position[0] += self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x, y + 1))
        elif self.direction == 'L':
            self.position[0] -= self.speed

            x = int(self.position[0] / 30)
            y = int(self.position[1] / 30)

            self.area = ((x, y), (x, y + 1))

        x = int(self.position[0] / 30)
        y = int(self.position[1] / 30)
        if x < 0 or y < 0 or x >= x_max or y >= y_max:
            return False

        if self.area[0][0] < 0 or self.area[0][1] < 0 or self.area[0][0] >= x_max or self.area[0][1] >= y_max:
            return False

        if self.area[1][0] < 0 or self.area[1][1] < 0 or self.area[1][0] >= x_max or self.area[1][1] >= y_max:
            return False

        if battle_field[self.area[0][1]][self.area[0][0]] == 1:
            battle_field[self.area[0][1]][self.area[0][0]] = 0
            return False

        if battle_field[self.area[1][1]][self.area[1][0]] == 1:
            battle_field[self.area[1][1]][self.area[1][0]] = 0
            return False

        if battle_field[self.area[0][1]][self.area[0][0]] == 2:
            return False
        if battle_field[self.area[1][1]][self.area[1][0]] == 2:
            return False

        if area_conflict(tank.area, self.area):
            tank.attacked()
            return False

        if area_conflict(symbol_area, self.area):
            symbol_attacked += 1
            return False

        self.draw()

# blank         0
# brick_wall    1
# cement_wall   2
# symbol        3
small_battle_field = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
    [0, 1, 2, 1, 0, 0, 0, 1, 2, 1, 0],
    [0, 2, 2, 2, 0, 0, 0, 2, 2, 2, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
    [0, 1, 1, 1, 0, 0, 0, 1, 1, 1, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 1, 1, 3, 1, 1, 0, 0, 0]]
battle_field = []
pygame.init()
expand_battle_field()
x_max, y_max = len(battle_field[0]), len(battle_field)
screen = pygame.display.set_mode((x_max* 30, y_max * 30), 0, 32)
pygame.display.set_caption('Battle City')

symbol_area = None
symbol_position = None
symbol_attacked = 0
symbol_limitation = 4

brick_wall_img = pygame.image.load("resources/images/brick_wall.gif")
cement_wall_img = pygame.image.load("resources/images/cement_wall.gif")
symbol_img = pygame.image.load("resources/images/symbol.gif")
symbol_destoryed_img = pygame.image.load("resources/images/symbol_destoryed.gif")
game_over_img = pygame.image.load("resources/images/game_over.gif")

tank_img_D = pygame.image.load("resources/images/p1tankD.gif")
tank_img_L = pygame.image.load("resources/images/p1tankL.gif")
tank_img_R = pygame.image.load("resources/images/p1tankR.gif")
tank_img_U = pygame.image.load("resources/images/p1tankU.gif")

enemy_img_D = pygame.image.load("resources/images/enemy1D.gif")
enemy_img_L = pygame.image.load("resources/images/enemy1L.gif")
enemy_img_R = pygame.image.load("resources/images/enemy1R.gif")
enemy_img_U = pygame.image.load("resources/images/enemy1U.gif")

tank_missile_img = pygame.image.load("resources/images/tankmissile.gif")
enemy_missile_img = pygame.image.load("resources/images/enemymissile.gif")

fire_msc = pygame.mixer.Sound("resources/audios/fire.wav")
fire_msc.set_volume(1)

hit_msc = pygame.mixer.Sound("resources/audios/hit.wav")
hit_msc.set_volume(50)

start_msc = pygame.mixer.Sound("resources/audios/start.wav")
start_msc.set_volume(5)

tank_init_position = (4, 16)
enemy_init_position = ((0, 0), (20, 0))
enemy_init_area = (
        ((0, 0), (0, 1), (1, 0), (1, 1)), 
        ((20, 0), (20, 1), (21, 0), (21, 1)))
enemys_cur_number = 0
enemys_max_number = 10

tank = Tank()
enemys = []

# up, left, down, right, fire
keys = [False, False, False, False, False]
last_move = -1
move_interval = 200
last_product = -1
enemys_product_interval = 5000

running = True
game_over = False

start_msc.play()
while running:
    screen.fill(0);
    if symbol_attacked >= symbol_limitation:
        game_over = True

    if tank.destroyed:
        game_over = True
    tank.update()

    draw_battle_field()
    time = pygame.time.get_ticks()
    if enemys_cur_number < enemys_max_number:
        produce_enemy(time)
    index = 0
    for enemy in enemys:
        if enemy.destroyed:
            enemys.pop(index)
        else:
            enemy.update(time)
        index += 1
    if game_over:
        screen.blit(game_over_img, (x_max * 15 - game_over_img.get_width() / 2, y_max * 15 - game_over_img.get_height() / 2))
    pygame.display.flip()
    pygame.display.update()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_w or event.key == K_UP:
                keys[0] = True 
            elif event.key == K_a or event.key == K_LEFT:
                keys[1] = True 
            elif event.key == K_s or event.key == K_DOWN:
                keys[2] = True 
            elif event.key == K_d or event.key == K_RIGHT:
                keys[3] = True 
            if event.key == K_SPACE:
                keys[4] = True 

        if event.type == pygame.KEYUP:
            if event.key == K_w or event.key == K_UP:
                keys[0] = False
            elif event.key == K_a or event.key == K_LEFT:
                keys[1] = False
            elif event.key == K_s or event.key == K_DOWN:
                keys[2] = False
            elif event.key == K_d or event.key == K_RIGHT:
                keys[3] = False
            if event.key == K_SPACE:
                keys[4] = False
    
    if game_over:
        continue

    if keys[0]:
        if last_move == -1 or time - last_move >= move_interval:
            last_move = time
            tank.up()
    elif keys[2]:
        if last_move == -1 or time - last_move >= move_interval:
            last_move = time
            tank.down()
    if keys[1]:
        if last_move == -1 or time - last_move >= move_interval:
            last_move = time
            tank.left()
    elif keys[3]:
        if last_move == -1 or time - last_move >= move_interval:
            last_move = time
            tank.right()
    if keys[4]:
        tank.fire(time)
        fire_msc.play()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
