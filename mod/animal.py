import os
import random
import threading

import pygame
import sys
import time

from mod.map import create_map, screen
from threading import Timer
cat_x = 120
cat_y = 400
dog_x = 120
dog_y = 850
defenceTime = 2
y_max = 900
y_min = 0
x_max = 1000
x_min = 50
times = 60
def play_sound_effect(file_path, start_time, duration):
    sound = pygame.mixer.Sound(file_path)
    sound.play(loops=0, maxtime=duration, fade_ms=0)

def Cat_sound():
    play_sound_effect(file_path=os.path.join("music", "cat.mp3"), start_time=0, duration=1000)

def Dog_sound():
    play_sound_effect(file_path=os.path.join("music", "dog.mp3"), start_time=0, duration=2000)

class Cat(object):
    def __init__(self):
        self.hurtStatus = False
        self.catStatus = [pygame.transform.scale(pygame.image.load(os.path.join("images", "cat1.png")), (100, 100)),  # 正常向右移动
                          pygame.transform.scale(pygame.image.load(os.path.join("images", "cat2.png")), (115, 90)),  # 跳跃向右移动
                          pygame.transform.scale(pygame.image.load(os.path.join("images", "cat3.png")), (115, 90)),  # 下滑向右移动
                          pygame.transform.scale(pygame.image.load(os.path.join("images", "cat4.png")), (100, 100)),  # 正常向左移动
                          pygame.transform.scale(pygame.image.load(os.path.join("images", "cat5.png")), (115, 90)),  # 跳跃向左移动
                          pygame.transform.scale(pygame.image.load(os.path.join("images", "cat6.png")), (115, 90)),  # 下滑向左移动
                          ]
        self.statues = 0
        self.catX = cat_x
        self.catY = cat_y
        self.jumpStatues = False
        self.defendStatus = False  # 默认为非防御状态
        self.health = 5  # 血条
        self.healthStatus = [
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart1.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart2.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart3.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart4.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart5.png")), (300, 50)),
        ]
        self.beatS = False
        self.now_x = 0
        self.now_y = 0
        self.angle = 0
        self.size = 50
        self.energy = 5  # 能量
        # 动作互斥锁：保护 up/down/defend/beat/hurt 的"检查-置位"原子性
        self._action_lock = threading.RLock()
        self.energyStatus = [
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy0.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy1.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy2.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy3.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy4.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy5.png")), (300, 50)),
        ]

    def get_position(self):
        with self._action_lock:
            return self.catX, self.catY

    def _try_start_jump(self, current_status, jump_status):
        with self._action_lock:
            if self.jumpStatues or self.statues != current_status:
                return False
            self.jumpStatues = True
            self.statues = jump_status
            return True

    def _finish_jump(self, final_status):
        with self._action_lock:
            self.statues = final_status
            self.jumpStatues = False

    def _move_y(self, distance):
        with self._action_lock:
            self.catY += distance

    def _try_set_status(self, current_status, new_status):
        with self._action_lock:
            if self.statues != current_status:
                return False
            self.statues = new_status
            return True

    def _set_status(self, status):
        with self._action_lock:
            self.statues = status

    def _start_beat(self):
        with self._action_lock:
            if self.energy != 5:
                return False
            self.beatS = True
            self.energy -= 5
            self.angle = 0
            return True

    def _set_beat_start(self, x, y):
        with self._action_lock:
            self.now_x = x
            self.now_y = y

    def _beat_y_less_than(self, target_y):
        with self._action_lock:
            return self.now_y < target_y

    def _move_beat(self, move_x_speed, move_y_speed, rotation_speed, size_rate):
        with self._action_lock:
            self.now_x += move_x_speed
            self.now_y += move_y_speed
            self.angle += rotation_speed
            self.size *= size_rate

    def stop_beat(self):
        with self._action_lock:
            self.beatS = False

    def _start_defend(self):
        with self._action_lock:
            if self.defendStatus or self.energy != 5:
                return False
            self.defendStatus = True
            self.energy -= 5
            return True

    def _finish_defend(self):
        with self._action_lock:
            self.defendStatus = False

    def _start_hurt(self):
        with self._action_lock:
            if self.hurtStatus:
                return False
            self.hurtStatus = True
            return True

    def _finish_hurt(self):
        with self._action_lock:
            self.hurtStatus = False

    def up(self):
        if self._try_start_jump(0, 1):
            for i in range(10):  # 上升
                time.sleep(0.02)
                self._move_y(-10)
            # 停留
            time.sleep(0.5)
            for i in range(10):  # 下降
                time.sleep(0.02)
                self._move_y(10)
            self._finish_jump(0)
        elif self._try_start_jump(3, 4):
            for i in range(10):  # 上升
                time.sleep(0.02)
                self._move_y(-10)
            # 停留
            time.sleep(0.5)
            for i in range(10):  # 下降
                time.sleep(0.02)
                self._move_y(10)
            self._finish_jump(3)

    def down(self):
        if self._try_set_status(0, 2):
            time.sleep(0.9)
            self._set_status(0)
        elif self._try_set_status(3, 5):
            time.sleep(0.9)
            self._set_status(3)

    def left(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 4
            else:
                self.statues = 3
            if self.catX > x_min:
                self.catX = self.catX - 5

    def right(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 1
            else:
                self.statues = 0
            if self.catX < x_max:
                self.catX = self.catX + 5

    def beat(self, dog):
        if self._start_beat():
            rotation_speed = 360 / times

            target_x, target_y = dog.get_position()
            start_x, start_y = self.get_position()

            move_x_speed = (target_x - start_x) // times
            move_y_speed = (target_y - start_y) // times
            self._set_beat_start(start_x, start_y)
            while self._beat_y_less_than(target_y):
                self._move_beat(move_x_speed, move_y_speed, rotation_speed, 1.02)
                time.sleep(0.02)
            self.stop_beat()



    def defend(self):
        if self._start_defend():
            time.sleep(defenceTime)
            self._finish_defend()

    def getenergy(self):  # 获得能量
        with self._action_lock:
            if not self.defendStatus and self.energy < 5:
                self.energy += 1

    def useenergy(self):
        with self._action_lock:
            if self.energy >= 5:
                self.energy -= 5

    def cutlive(self):  # 扣除生命
        should_play_sound = False
        with self._action_lock:
            if not self.defendStatus:
                self.health -= 1
                should_play_sound = True
        if should_play_sound:
            Cat_sound()

    def hurt(self):
        if self._start_hurt():
            self.cutlive()
            time.sleep(defenceTime)
            self._finish_hurt()


class Dog(object):
    def __init__(self):
        self.hurtStatus = False
        self.size = 50
        self.dogStatus = [
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog1.png")), (100, 100)),  # 正常向右移动
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog2.png")), (115, 90)),  # 跳跃向右移动
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog3.png")), (115, 90)),  # 下滑向右移动
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog4.png")), (100, 100)),  # 正常向左移动
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog5.png")), (115, 90)),  # 跳跃向左移动
            pygame.transform.scale(pygame.image.load(os.path.join("images", "dog6.png")), (115, 90)),  # 下滑向左移动
        ]
        self.statues = 0
        self.dogX = dog_x
        self.dogY = dog_y
        self.jumpStatues = False
        self.defendStatus = False  # 默认为非防御状态
        self.health = 5  # 血条
        self.healthStatues = [
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart1.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart2.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart3.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart4.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "heart5.png")), (300, 50)),
        ]
        self.beatS = False
        self.now_x = 0
        self.now_y = 0
        self.angle = 0
        self.energy = 5  # 能量
        # 动作互斥锁：保护 up/down/defend/beat/hurt 的"检查-置位"原子性
        self._action_lock = threading.RLock()
        self._action_lock = threading.RLock()
        self.energyStatus = [
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy0.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy1.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy2.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy3.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy4.png")), (300, 50)),
            pygame.transform.scale(pygame.image.load(os.path.join("images", "energy5.png")), (300, 50)),
        ]

    def get_position(self):
        with self._action_lock:
            return self.dogX, self.dogY

    def _try_start_jump(self, current_status, jump_status):
        with self._action_lock:
            if self.jumpStatues or self.statues != current_status:
                return False
            self.jumpStatues = True
            self.statues = jump_status
            return True

    def _finish_jump(self, final_status):
        with self._action_lock:
            self.statues = final_status
            self.jumpStatues = False

    def _move_y(self, distance):
        with self._action_lock:
            self.dogY += distance

    def _try_set_status(self, current_status, new_status):
        with self._action_lock:
            if self.statues != current_status:
                return False
            self.statues = new_status
            return True

    def _set_status(self, status):
        with self._action_lock:
            self.statues = status

    def _start_beat(self):
        with self._action_lock:
            if self.energy != 5:
                return False
            self.beatS = True
            self.energy -= 5
            self.angle = 0
            return True

    def _set_beat_start(self, x, y):
        with self._action_lock:
            self.now_x = x
            self.now_y = y

    def _beat_y_greater_than(self, target_y):
        with self._action_lock:
            return self.now_y > target_y

    def _move_beat(self, move_x_speed, move_y_speed, rotation_speed, size_rate):
        with self._action_lock:
            self.now_x += move_x_speed
            self.now_y += move_y_speed
            self.angle += rotation_speed
            self.size *= size_rate

    def stop_beat(self):
        with self._action_lock:
            self.beatS = False

    def _start_defend(self):
        with self._action_lock:
            if self.defendStatus or self.energy != 5:
                return False
            self.defendStatus = True
            self.energy -= 5
            return True

    def _finish_defend(self):
        with self._action_lock:
            self.defendStatus = False

    def _start_hurt(self):
        with self._action_lock:
            if self.hurtStatus:
                return False
            self.hurtStatus = True
            return True

    def _finish_hurt(self):
        with self._action_lock:
            self.hurtStatus = False

    def up(self):
        if self._try_start_jump(0, 1):
            for i in range(10):  # 上升
                time.sleep(0.02)
                self._move_y(-10)
            # 停留
            time.sleep(0.5)
            for i in range(10):  # 下降
                time.sleep(0.02)
                self._move_y(10)
            self._finish_jump(0)
        elif self._try_start_jump(3, 4):
            for i in range(10):  # 上升
                time.sleep(0.02)
                self._move_y(-10)
            # 停留
            time.sleep(0.5)
            for i in range(10):  # 下降
                time.sleep(0.02)
                self._move_y(10)
            self._finish_jump(3)

    def down(self):
        if self._try_set_status(0, 2):
            time.sleep(0.9)
            self._set_status(0)
        elif self._try_set_status(3, 5):
            time.sleep(0.9)
            self._set_status(3)

    def left(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 4
            else:
                self.statues = 3
            if self.dogX > x_min:
                self.dogX = self.dogX - 5

    def right(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 1
            else:
                self.statues = 0
            if self.dogX < x_max:
                self.dogX = self.dogX + 5

    def beat(self, cat):
        if self._start_beat():
            rotation_speed = 360 / times

            target_x, target_y = cat.get_position()
            start_x, start_y = self.get_position()


            move_x_speed = (target_x - start_x) // times
            move_y_speed = (target_y - start_y) // times
            self._set_beat_start(start_x, start_y)
            while self._beat_y_greater_than(target_y):
                self._move_beat(move_x_speed, move_y_speed, rotation_speed, 1.01)
                time.sleep(0.02)
            self.stop_beat()


    def getDefend(self):
        while self.defendStatus:
            finalImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "obstacle1.png")), (50, 50))
            finalRect = finalImage.get_rect()
            finalRect.bottomleft = (self.dogX, self.dogY)
            screen.blit(finalImage, finalRect)

    def defend(self):
        if self._start_defend():
            time.sleep(defenceTime)
            self._finish_defend()

    def getenergy(self):  # 获得能量
        with self._action_lock:
            if not self.defendStatus and self.energy < 5:
                self.energy += 1

    def useenergy(self):
        with self._action_lock:
            if self.energy >= 5:
                self.energy -= 5

    def cutlive(self):  # 扣除生命
        should_play_sound = False
        with self._action_lock:
            if not self.defendStatus:
                self.health -= 1
                should_play_sound = True
        if should_play_sound:
            Dog_sound()

    def hurt(self):
        if self._start_hurt():
            self.cutlive()
            time.sleep(defenceTime)
            self._finish_hurt()
