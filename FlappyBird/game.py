import pygame
from pygame.locals import *
import math
import random

pygame.init()

# =========== game ===========
running = True
game_over = False
score = 0
last_second = 0 
time_interval = 2
clock = pygame.time.Clock()
width, height = 640, 480

screen = pygame.display.set_mode((width, height), 0, 32)
pygame.display.set_caption('FlappyBird')
background_img = pygame.image.load("resources/images/background.png")
gameover_img = pygame.image.load("resources/images/gameover.png")

jump_msc = pygame.mixer.Sound("resources/audios/jump.wav")
jump_msc.set_volume(5)

pygame.mixer.music.load('resources/audios/moonlight.wav')
pygame.mixer.music.play(-1, 0.0)
pygame.mixer.music.set_volume(10)
# =========== game ===========

# =========== pipe ===========
pipe_body_img = pygame.image.load("resources/images/pipe_body.png")
pipe_head_img = pygame.image.load("resources/images/pipe_head.png")
body_hight = pipe_body_img.get_height()
head_hight = pipe_head_img.get_height()
body_width = pipe_body_img.get_width()
head_width = pipe_head_img.get_width()
max_n = (height - 2 * head_hight) / body_hight
gap_n = 8
# =========== pipe ===========

# =========== bird ===========
bird_img = pygame.image.load("resources/images/bird.png")
bird_img.get_rect().centerx = 0
bird_img.get_rect().centery = bird_img.get_height() / 2 
down_speed = 300
angle_speed = 300
angle_max = 15 
jump_speed = 150
jump_height = 8
# =========== bird ===========

class Bird():
    def __init__(self):
        self.angle = 0
        self.x = 150
        self.y = (height - bird_img.get_height()) / 2.0

        self.cur_jump_height = 0
        self.is_jumping = False

    def draw(self):
        rotate_image = pygame.transform.rotate(bird_img, self.angle)
        delta_width = (rotate_image.get_rect().width - bird_img.get_rect().width) / 2
        delta_height = (rotate_image.get_rect().height - bird_img.get_rect().height) / 2
        (draw_x, draw_y) = (self.x - delta_width, self.y - delta_height)
        screen.blit(rotate_image, (draw_x, draw_y)) 

    def die(self, time_passed):
        global running

        if self.angle > -angle_max:
            self.angle -= angle_speed * time_passed
            if self.angle <= -angle_max:
                self.angle = -angle_max
            self.draw()
            return

        self.y += down_speed * time_passed
        self.draw()
        if self.y >= height:
            screen.blit(gameover_img, (0,0))
            running = False

    def update(self, time_passed):
        global game_over
        if self.is_jumping:
            if self.angle < angle_max:
                self.angle += time_passed * angle_speed
                if self.angle >= angle_max:
                    self.angle = angle_max
                self.draw()
                return

            if self.cur_jump_height < jump_height:
                self.cur_jump_height += time_passed * jump_speed
                self.y -= self.cur_jump_height
                if self.y <= 0:
                    game_over = True
                self.draw()
                return
            self.cur_jump_height = 0
            self.is_jumping = False

        if self.angle > -angle_max:
            self.angle -= angle_speed * time_passed
            if self.angle <= -angle_max:
                self.angle = -angle_max
            self.draw()
            return

        self.y += down_speed * time_passed
        if self.y >= height:
            game_over = True
            return
        self.draw()

class Pipe():
    def __init__(self):
        self.x = 600
        self.speed = 100
        self.random_n = random.randint(0, max_n - gap_n)
        self.up_n = self.random_n
        self.down_n = max_n - self.up_n - gap_n
        self.appearance = []

        self.added = False

        self.construct()

    def construct(self):
        for i in xrange(self.up_n):
            self.appearance.append((0, i * body_hight, pipe_body_img))
        self.appearance.append((-(head_width - body_width) / 2, self.up_n * body_hight, pipe_head_img))

        for i in xrange(self.down_n):
            self.appearance.append((0, height - (i + 1) * body_hight, pipe_body_img))
        self.appearance.append((-(head_width - body_width) / 2, height - self.down_n * body_hight - head_hight, pipe_head_img))

    def update(self, time_passed):
        global score
        self.x -= time_passed * self.speed
        if not self.added:
            if self.x + (head_width - body_width) / 2 + body_width <= bird.x:
                score += 1
                self.added = True 
        self.draw()

    def draw(self):
        for a in self.appearance:
            screen.blit(a[2], (self.x + a[0], a[1])) 

    def collide_with_bird(self):
        bird_rect = pygame.Rect(bird_img.get_rect())
        bird_rect.topleft = (bird.x, bird.y)
        for a in self.appearance:
            pipe_rect = pygame.Rect(a[2].get_rect())
            pipe_rect.left = self.x + a[0]
            pipe_rect.top = a[1]
            if pipe_rect.colliderect(bird_rect):
                return True
        return False

def draw_background_img():
    for x in xrange(width / background_img.get_width() + 1):
        for y in xrange(height / background_img.get_height() + 1):
            screen.blit(background_img, (x * 100, y * 100))

def draw_text(text):
    font = pygame.font.Font("resources/fonts/MONACO.TTF", 24)
    survivedtext = font.render(str(text), True, (0, 0, 0))
    textRect = survivedtext.get_rect()
    textRect.topleft = [10, 10]
    screen.blit(survivedtext, textRect)

pipes = []
bird = Bird()
while running:
    screen.fill(0)
    draw_background_img()
    draw_text(score)

    time_passed = clock.tick() / 1000.0

    if game_over:
        for p in pipes:
            p.update(0)
        bird.die(time_passed)
        pygame.display.flip()
        pygame.display.update()
        continue

    currend_second = pygame.time.get_ticks() / 1000
    if currend_second - last_second >= time_interval:
        last_second = currend_second 
        pipes.append(Pipe())

    bird.update(time_passed)
    for p in pipes:
        p.update(time_passed)

    pygame.display.flip()
    pygame.display.update()

    index = 0
    for p in pipes:
        if p.x + (head_width - body_width) / 2 + body_width <= 0:
            pipes.pop(index)
        elif p.collide_with_bird():
            # game over
            game_over = True
        index += 1

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
        if event.type == pygame.KEYDOWN:
            if event.key == K_SPACE:
                jump_msc.play()
                bird.cur_jump_height = 0
                bird.is_jumping = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip()
    pygame.display.update()
