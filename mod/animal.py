import os
import threading

import pygame

from mod.map import screen

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


def load_character_status(prefix):
    image_sizes = [(100, 100), (115, 90), (115, 90), (100, 100), (115, 90), (115, 90)]
    return [
        pygame.transform.scale(
            pygame.image.load(os.path.join("images", f"{prefix}{index}.png")),
            size,
        )
        for index, size in enumerate(image_sizes, start=1)
    ]


def load_bar_images(prefix):
    return [
        pygame.transform.scale(
            pygame.image.load(os.path.join("images", f"{prefix}{index}.png")),
            (300, 50),
        )
        for index in range(1, 6)
    ]


def load_energy_images():
    return [
        pygame.transform.scale(
            pygame.image.load(os.path.join("images", f"energy{index}.png")),
            (300, 50),
        )
        for index in range(6)
    ]


class Animal(object):
    def __init__(
        self,
        image_prefix,
        start_x,
        start_y,
        x_attr,
        y_attr,
        status_attr,
        health_attr,
        hurt_sound,
        beat_moves_down,
        beat_size_rate,
    ):
        self._x_attr = x_attr
        self._y_attr = y_attr
        self._hurt_sound = hurt_sound
        self._beat_moves_down = beat_moves_down
        self._beat_size_rate = beat_size_rate
        self._action_lock = threading.RLock()

        self.hurtStatus = False
        self.size = 50
        self.statues = 0
        setattr(self, x_attr, start_x)
        setattr(self, y_attr, start_y)
        self.jumpStatues = False
        self.defendStatus = False
        self.health = 5
        self.beatS = False
        self.now_x = 0
        self.now_y = 0
        self.angle = 0
        self.energy = 5
        self._base_y = start_y
        self._jump_elapsed = 0
        self._jump_duration = 0.9
        self._jump_height = 100
        self._jump_landing_status = 0
        self._down_elapsed = 0
        self._down_duration = 0.9
        self._down_final_status = 0
        self._defend_elapsed = 0
        self._hurt_elapsed = 0
        self._beat_elapsed = 0
        self._beat_duration = 1.2
        self._beat_start = (0, 0)
        self._beat_target = (0, 0)

        setattr(self, status_attr, load_character_status(image_prefix))
        setattr(self, health_attr, load_bar_images("heart"))
        self.energyStatus = load_energy_images()

    def _get_x(self):
        return getattr(self, self._x_attr)

    def _get_y(self):
        return getattr(self, self._y_attr)

    def _set_x(self, value):
        setattr(self, self._x_attr, value)

    def _set_y(self, value):
        setattr(self, self._y_attr, value)

    def get_position(self):
        with self._action_lock:
            return self._get_x(), self._get_y()

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
            self._set_y(self._get_y() + distance)

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
            if self.beatS or self.energy != 5:
                return False
            self.beatS = True
            self.energy -= 5
            self.angle = 0
            self.size = 50
            self._beat_elapsed = 0
            return True

    def _set_beat_start(self, x, y):
        with self._action_lock:
            self.now_x = x
            self.now_y = y

    def _should_continue_beat(self, target_y):
        with self._action_lock:
            if self._beat_moves_down:
                return self.now_y < target_y
            return self.now_y > target_y

    def _move_beat(self, move_x_speed, move_y_speed, rotation_speed):
        with self._action_lock:
            self.now_x += move_x_speed
            self.now_y += move_y_speed
            self.angle += rotation_speed
            self.size *= self._beat_size_rate

    def stop_beat(self):
        with self._action_lock:
            self.beatS = False
            self._beat_elapsed = 0

    def _start_defend(self):
        with self._action_lock:
            if self.defendStatus or self.energy != 5:
                return False
            self.defendStatus = True
            self.energy -= 5
            self._defend_elapsed = 0
            return True

    def _finish_defend(self):
        with self._action_lock:
            self.defendStatus = False
            self._defend_elapsed = 0

    def _start_hurt(self):
        with self._action_lock:
            if self.hurtStatus:
                return False
            self.hurtStatus = True
            self._hurt_elapsed = 0
            return True

    def _finish_hurt(self):
        with self._action_lock:
            self.hurtStatus = False
            self._hurt_elapsed = 0

    def up(self):
        with self._action_lock:
            if self.jumpStatues:
                return
            if self.statues == 0:
                self.statues = 1
                self._jump_landing_status = 0
            elif self.statues == 3:
                self.statues = 4
                self._jump_landing_status = 3
            else:
                return
            self.jumpStatues = True
            self._jump_elapsed = 0
            self._base_y = self._get_y()

    def down(self):
        with self._action_lock:
            if self.statues == 0:
                self.statues = 2
                self._down_final_status = 0
            elif self.statues == 3:
                self.statues = 5
                self._down_final_status = 3
            else:
                return
            self._down_elapsed = 0

    def left(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 4
            else:
                self.statues = 3
            if self._get_x() > x_min:
                self._set_x(self._get_x() - 5)

    def right(self):
        with self._action_lock:
            if self.jumpStatues:
                self.statues = 1
            else:
                self.statues = 0
            if self._get_x() < x_max:
                self._set_x(self._get_x() + 5)

    def beat(self, target):
        if not self._start_beat():
            return

        target_x, target_y = target.get_position()
        start_x, start_y = self.get_position()

        with self._action_lock:
            self._beat_start = (start_x, start_y)
            self._beat_target = (target_x, target_y)
            self._set_beat_start(start_x, start_y)

    def defend(self):
        self._start_defend()

    def getenergy(self):
        with self._action_lock:
            if not self.defendStatus and self.energy < 5:
                self.energy += 1

    def useenergy(self):
        with self._action_lock:
            if self.energy >= 5:
                self.energy -= 5

    def cutlive(self):
        should_play_sound = False
        with self._action_lock:
            if not self.defendStatus:
                self.health -= 1
                should_play_sound = True
        if should_play_sound:
            self._hurt_sound()

    def hurt(self):
        if self._start_hurt():
            self.cutlive()

    def update(self, dt):
        with self._action_lock:
            self._update_jump(dt)
            self._update_down(dt)
            self._update_defend(dt)
            self._update_hurt(dt)
            self._update_beat(dt)

    def _update_jump(self, dt):
        if not self.jumpStatues:
            return

        self._jump_elapsed += dt
        progress = min(1, self._jump_elapsed / self._jump_duration)
        jump_offset = -self._jump_height * 4 * progress * (1 - progress)
        self._set_y(self._base_y + jump_offset)

        if progress >= 1:
            self._set_y(self._base_y)
            self.statues = self._jump_landing_status
            self.jumpStatues = False
            self._jump_elapsed = 0

    def _update_down(self, dt):
        if self.statues not in (2, 5):
            return

        self._down_elapsed += dt
        if self._down_elapsed >= self._down_duration:
            self.statues = self._down_final_status
            self._down_elapsed = 0

    def _update_defend(self, dt):
        if not self.defendStatus:
            return

        self._defend_elapsed += dt
        if self._defend_elapsed >= defenceTime:
            self.defendStatus = False
            self._defend_elapsed = 0

    def _update_hurt(self, dt):
        if not self.hurtStatus:
            return

        self._hurt_elapsed += dt
        if self._hurt_elapsed >= defenceTime:
            self.hurtStatus = False
            self._hurt_elapsed = 0

    def _update_beat(self, dt):
        if not self.beatS:
            return

        self._beat_elapsed += dt
        progress = min(1, self._beat_elapsed / self._beat_duration)
        start_x, start_y = self._beat_start
        target_x, target_y = self._beat_target
        self.now_x = start_x + (target_x - start_x) * progress
        self.now_y = start_y + (target_y - start_y) * progress
        self.angle = 360 * progress
        self.size = 50 * (self._beat_size_rate ** (times * progress))

        if progress >= 1:
            self.beatS = False
            self._beat_elapsed = 0


class Cat(Animal):
    def __init__(self):
        super().__init__(
            image_prefix="cat",
            start_x=cat_x,
            start_y=cat_y,
            x_attr="catX",
            y_attr="catY",
            status_attr="catStatus",
            health_attr="healthStatus",
            hurt_sound=Cat_sound,
            beat_moves_down=True,
            beat_size_rate=1.02,
        )


class Dog(Animal):
    def __init__(self):
        super().__init__(
            image_prefix="dog",
            start_x=dog_x,
            start_y=dog_y,
            x_attr="dogX",
            y_attr="dogY",
            status_attr="dogStatus",
            health_attr="healthStatues",
            hurt_sound=Dog_sound,
            beat_moves_down=False,
            beat_size_rate=1.01,
        )

    def getDefend(self):
        while self.defendStatus:
            finalImage = pygame.transform.scale(pygame.image.load(os.path.join("images", "obstacle1.png")), (50, 50))
            finalRect = finalImage.get_rect()
            with self._action_lock:
                finalRect.bottomleft = (self.dogX, self.dogY)
            screen.blit(finalImage, finalRect)
