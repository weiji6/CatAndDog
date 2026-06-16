import os
import random

import pygame

from mod.animal import cat_y, dog_y

obstaclelist = []
y_max = 900
y_min = 0
x_max = 1000
x_min = 50
speed = 500

GROUND_OBSTACLE = 'ground_obstacle'
AIR_OBSTACLE = 'air_obstacle'
CAT_ENERGY = 'cat_sky'
DOG_ENERGY = 'dog_sky'
DAMAGE_OBSTACLE_TYPES = {GROUND_OBSTACLE, AIR_OBSTACLE}
OBSTACLE_IMAGES = {}


def get_obstacle_image(file_name):
    if file_name not in OBSTACLE_IMAGES:
        OBSTACLE_IMAGES[file_name] = pygame.transform.scale(
            pygame.image.load(os.path.join("images", file_name)),
            (50, 50),
        )
    return OBSTACLE_IMAGES[file_name]


def creatcatObstacle():
    i = random.randint(1, 130)
    if i <= 50:
        obstacle = Obstacle1()
        obstacle.obstacleY = cat_y
    elif i <= 100:
        obstacle = Obstacle2()
        obstacle.obstacleY = random.randint(y_min + 100, y_min + 300)
    else:
        obstacle = Obstacle3()
        obstacle.obstacleY = 0
        obstacle.obstacleX = random.randint(x_min, x_max)

    obstaclelist.append(obstacle)


def createdogObstacle():
    i = random.randint(1, 130)
    if i <= 50:
        obstacle = Obstacle1()
        obstacle.obstacleY = dog_y
    elif i <= 100:
        obstacle = Obstacle2()
        obstacle.obstacleY = random.randint(y_max // 2 + 100, y_max // 2 + 300)
    else:
        obstacle = Obstacle4()
        obstacle.obstacleY = 0
        obstacle.obstacleX = random.randint(x_min, x_max)

    obstaclelist.append(obstacle)


class Obstacle(object):
    def __init__(self, image_name, obstacle_type, direction):
        self.obstacleStatus = get_obstacle_image(image_name)
        self.obstacleRect = self.obstacleStatus.get_rect()
        self.speed = speed
        self.obstacleX = 1200
        self.obstacleY = 0
        self.type = obstacle_type
        self.direction = direction

    def move(self, dt):
        if self.direction == 'left':
            self.obstacleX -= self.speed * dt
        else:
            self.obstacleY += self.speed * dt
        self.obstacleRect.bottomleft = (int(self.obstacleX), int(self.obstacleY))

    def remove(self):
        out_of_bounds = self.obstacleX < 0 if self.direction == 'left' else self.obstacleY >= y_max
        if out_of_bounds:
            self.destroy()

    def destroy(self):
        if self in obstaclelist:
            obstaclelist.remove(self)


class Obstacle1(Obstacle):
    def __init__(self):
        super().__init__("obstacle1.png", GROUND_OBSTACLE, 'left')


class Obstacle2(Obstacle):
    def __init__(self):
        super().__init__("obstacle2.png", AIR_OBSTACLE, 'left')


class Obstacle3(Obstacle):
    def __init__(self):
        super().__init__("fish.png", CAT_ENERGY, 'down')
        self.obstacleX = 0


class Obstacle4(Obstacle):
    def __init__(self):
        super().__init__("bone.png", DOG_ENERGY, 'down')
        self.obstacleX = 0
