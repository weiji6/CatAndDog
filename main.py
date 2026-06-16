import threading

import pygame
import sys
import os
import random
import time
from mod.obstacle import (
    CAT_ENERGY,
    DAMAGE_OBSTACLE_TYPES,
    DOG_ENERGY,
    obstaclelist,
    createdogObstacle,
    creatcatObstacle,
)
import mod.animal
from mod.map import screen
from mod.map import start


class DogJumpThread(threading.Thread):
    def __init__(self, dog):
        super().__init__()
        self.dog = dog

    def run(self):
        self.dog.up()


class CatJumpThread(threading.Thread):
    def __init__(self, cat):
        super().__init__()
        self.cat = cat

    def run(self):
        self.cat.up()


class DogDownThread(threading.Thread):
    def __init__(self, dog):
        super().__init__()
        self.dog = dog

    def run(self):
        self.dog.down()


class CatDownThread(threading.Thread):
    def __init__(self, cat):
        super().__init__()
        self.cat = cat

    def run(self):
        self.cat.down()


class DogDefendThread(threading.Thread):
    def __init__(self, dog):
        super().__init__()
        self.dog = dog

    def run(self):
        self.dog.defend()


class CatDefendThread(threading.Thread):
    def __init__(self, cat):
        super().__init__()
        self.cat = cat

    def run(self):
        self.cat.defend()


class CatBeatThread(threading.Thread):
    def __init__(self, cat, dog):
        super().__init__()
        self.dog = dog
        self.cat = cat

    def run(self):
        self.cat.beat(self.dog)


class DogBeatThread(threading.Thread):
    def __init__(self, cat, dog):
        super().__init__()
        self.dog = dog
        self.cat = cat

    def run(self):
        self.dog.beat(self.cat)


class DogHurtThread(threading.Thread):
    def __init__(self, dog):
        super().__init__()
        self.dog = dog

    def run(self):
        self.dog.hurt()


class CatHurtThread(threading.Thread):
    def __init__(self, cat):
        super().__init__()
        self.cat = cat

    def run(self):
        self.cat.hurt()


def music_play():
    pygame.mixer.music.load(os.path.join("music", "music.mp3"))
    pygame.mixer.music.play(-1)  # 循环播放音乐
def Play():
    cat = mod.animal.Cat()
    dog = mod.animal.Dog()
    count = 0
    q = 400

    while True:
        with cat._action_lock:
            cat_alive = cat.health > 0
        with dog._action_lock:
            dog_alive = dog.health > 0
        if not cat_alive or not dog_alive:
            break

        count += 1
        if count == 7:
            count = 0
            q = max(200, q - 1)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        key = pygame.key.get_pressed()

        # 猫的控制
        if key[pygame.K_w]:
            CatJumpThread(cat).start()
        elif key[pygame.K_s]:
            CatDownThread(cat).start()
        elif key[pygame.K_a]:
            cat.left()
        elif key[pygame.K_d]:
            cat.right()
        elif key[pygame.K_j]:
            CatBeatThread(cat, dog).start()
        elif key[pygame.K_k]:
            # CatgetDefendThread(cat).start()
            CatDefendThread(cat).start()

        # 狗的控制
        if key[pygame.K_UP]:
            DogJumpThread(dog).start()
        elif key[pygame.K_DOWN]:
            DogDownThread(dog).start()
        elif key[pygame.K_LEFT]:
            dog.left()
        elif key[pygame.K_RIGHT]:
            dog.right()
        elif key[pygame.K_KP1]:
            DogBeatThread(cat, dog).start()
        elif key[pygame.K_KP2]:
            DogDefendThread(dog).start()

        mod.map.create_map()  # 每帧重新绘制背景

        with cat._action_lock:
            cat_status = cat.statues
            cat_x = cat.catX
            cat_y = cat.catY
            cat_health = cat.health
            cat_energy_value = cat.energy
            cat_beatS = cat.beatS
            cat_beat_size = cat.size
            cat_beat_angle = cat.angle
            cat_beat_x = cat.now_x
            cat_beat_y = cat.now_y
            cat_defendStatus = cat.defendStatus
            cat_hurtStatus = cat.hurtStatus

        with dog._action_lock:
            dog_status = dog.statues
            dog_x = dog.dogX
            dog_y = dog.dogY
            dog_health = dog.health
            dog_energy_value = dog.energy
            dog_beatS = dog.beatS
            dog_beat_size = dog.size
            dog_beat_angle = dog.angle
            dog_beat_x = dog.now_x
            dog_beat_y = dog.now_y
            dog_defendStatus = dog.defendStatus
            dog_hurtStatus = dog.hurtStatus

        cat_image = cat.catStatus[cat_status]
        cat_image_rect = cat_image.get_rect()
        cat_image_rect.bottomleft = (cat_x, cat_y)

        dog_image = dog.dogStatus[dog_status]
        dog_image_rect = dog_image.get_rect()
        dog_image_rect.bottomleft = (dog_x, dog_y)

        dog_heart = dog.healthStatues[max(1, dog_health) - 1]
        dog_heart_rect = dog_heart.get_rect()
        dog_heart_rect.bottomleft = (800, 70)

        cat_heart = cat.healthStatus[max(1, cat_health) - 1]
        cat_heart_rect = cat_heart.get_rect()
        cat_heart_rect.bottomleft = (100, 70)

        cat_energy = cat.energyStatus[cat_energy_value]
        cat_energy_rect = cat_energy.get_rect()
        cat_energy_rect.bottomleft = (100, 140)

        dog_energy = dog.energyStatus[dog_energy_value]
        dog_energy_rect = dog_energy.get_rect()
        dog_energy_rect.bottomleft = (800, 140)

        if cat_beatS:
            cat_beatImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "fish.png")), (cat_beat_size, cat_beat_size))
            cat_beatImage = pygame.transform.rotate(cat_beatImage, cat_beat_angle)
            beatRect = cat_beatImage.get_rect()
            beatRect.bottomleft = (cat_beat_x, cat_beat_y)
            screen.blit(cat_beatImage, beatRect)
            if dog_image_rect.colliderect(beatRect):
                DogHurtThread(dog).start()
                cat.stop_beat()

        if dog_beatS:
            dog_beatImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "bone.png")), (dog_beat_size, dog_beat_size))
            dog_beatImage = pygame.transform.rotate(dog_beatImage, dog_beat_angle)
            beatRect = dog_beatImage.get_rect()
            beatRect.bottomleft = (dog_beat_x, dog_beat_y)
            screen.blit(dog_beatImage, beatRect)
            if cat_image_rect.colliderect(beatRect):
                CatHurtThread(cat).start()
                dog.stop_beat()

        if cat_defendStatus:
            cat_defendImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "denfendcat.png")), (200, 150))
            cat_defendRect = cat_defendImage.get_rect()
            cat_defendRect.bottomleft = (cat_x - 35, cat_y - 15)
            screen.blit(cat_defendImage, cat_defendRect)

        if dog_defendStatus:
            dog_defendImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "defendog.png")), (200, 150))
            dog_defendRect = dog_defendImage.get_rect()
            dog_defendRect.bottomleft = (dog_x - 35, dog_y - 15)
            screen.blit(dog_defendImage, dog_defendRect)

        if cat_hurtStatus:
            cat_hurtImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "hurt.png")), (100, 75))
            cat_hurtRect = cat_hurtImage.get_rect()
            cat_hurtRect.bottomleft = (cat_x + 15, cat_y - 80)
            screen.blit(cat_hurtImage, cat_hurtRect)

        if dog_hurtStatus:
            finalImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "hurt.png")), (100, 75))
            finalRect = finalImage.get_rect()
            finalRect.bottomleft = (dog_x + 15, dog_y - 80)
            screen.blit(finalImage, finalRect)

        # 创建新障碍物
        if random.randint(1, q) == 1:
            createdogObstacle()
            creatcatObstacle()

        # 移动障碍物
        # 复制当前的障碍物的副本并游历
        for obstacle in obstaclelist[:]:
            obstacle.move()
            obstacle_destroyed = False
            # 碰撞检测
            if dog_image_rect.colliderect(obstacle.obstacleRect):
                if obstacle.type == DOG_ENERGY:
                    dog.getenergy()
                    obstacle.destroy()
                    obstacle_destroyed = True
                elif obstacle.type in DAMAGE_OBSTACLE_TYPES:
                    DogHurtThread(dog).start()
                    obstacle.destroy()
                    obstacle_destroyed = True
            if not obstacle_destroyed and cat_image_rect.colliderect(obstacle.obstacleRect):
                if obstacle.type == CAT_ENERGY:
                    cat.getenergy()
                    obstacle.destroy()
                    obstacle_destroyed = True
                elif obstacle.type in DAMAGE_OBSTACLE_TYPES:
                    CatHurtThread(cat).start()
                    obstacle.destroy()
                    obstacle_destroyed = True
            if not obstacle_destroyed:
                obstacle.remove()

        screen.blit(cat_image, cat_image_rect)
        screen.blit(dog_image, dog_image_rect)
        screen.blit(cat_heart, cat_heart_rect)
        screen.blit(dog_heart, dog_heart_rect)
        screen.blit(cat_energy, cat_energy_rect)
        screen.blit(dog_energy, dog_energy_rect)

        for obstacle in obstaclelist:
            screen.blit(obstacle.obstacleStatus, obstacle.obstacleRect)

        pygame.display.flip()
        clock.tick(100)  # 控制帧率

    with dog._action_lock:
        dog_won = dog.health > 0

    if dog_won:
        finalImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "dogwin.png")), (500, 500))
        finalRect = finalImage.get_rect()
        finalRect.bottomleft = (350, 650)
        cat_heart = pygame.transform.scale(pygame.image.load(os.path.join("images", "heart0.png")), (300, 50))
        cat_heart_rect = cat_heart.get_rect()
        cat_heart_rect.bottomleft = (100, 70)
        mod.map.screen.blit(finalImage, finalRect)
        mod.map.screen.blit(cat_heart, cat_heart_rect)
    else:
        finalImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "catwin.png")), (500, 500))
        finalRect = finalImage.get_rect()
        finalRect.bottomleft = (300, 690)
        dog_heart = pygame.transform.scale(pygame.image.load(os.path.join("images", "heart0.png")), (300, 50))
        dog_heart_rect = dog_heart.get_rect()
        dog_heart_rect.bottomleft = (800, 70)
        mod.map.screen.blit(finalImage, finalRect)
        mod.map.screen.blit(dog_heart, dog_heart_rect)
    # 清空障碍物列表
    obstaclelist.clear()
    pygame.display.flip()
    time.sleep(5)



if __name__ == "__main__":
    # 初始化
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("猫狗大战")
    clock = pygame.time.Clock()
    music_play()

    while start():
        Play()

