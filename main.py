import os
import random
import sys
import time

import pygame

import mod.animal
import mod.map
from mod.map import screen
from mod.map import start
from mod.obstacle import (
    CAT_ENERGY,
    DAMAGE_OBSTACLE_TYPES,
    DOG_ENERGY,
    obstaclelist,
    createdogObstacle,
    creatcatObstacle,
)


def load_game_assets():
    return {
        "fish": pygame.image.load(os.path.join("images", "fish.png")).convert_alpha(),
        "bone": pygame.image.load(os.path.join("images", "bone.png")).convert_alpha(),
        "cat_defend": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "denfendcat.png")).convert_alpha(),
            (200, 150),
        ),
        "dog_defend": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "defendog.png")).convert_alpha(),
            (200, 150),
        ),
        "hurt": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "hurt.png")).convert_alpha(),
            (100, 75),
        ),
        "dog_win": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "dogwin.png")).convert_alpha(),
            (500, 500),
        ),
        "cat_win": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "catwin.png")).convert_alpha(),
            (500, 500),
        ),
        "empty_heart": pygame.transform.scale(
            pygame.image.load(os.path.join("images", "heart0.png")).convert_alpha(),
            (300, 50),
        ),
    }


def music_play():
    pygame.mixer.music.load(os.path.join("music", "music.mp3"))
    pygame.mixer.music.play(-1)


def handle_action_key(event, cat, dog):
    if event.key == pygame.K_w:
        cat.up()
    elif event.key == pygame.K_s:
        cat.down()
    elif event.key == pygame.K_j:
        cat.beat(dog)
    elif event.key == pygame.K_k:
        cat.defend()
    elif event.key == pygame.K_UP:
        dog.up()
    elif event.key == pygame.K_DOWN:
        dog.down()
    elif event.key == pygame.K_KP1:
        dog.beat(cat)
    elif event.key == pygame.K_KP2:
        dog.defend()


def handle_movement_keys(cat, dog):
    key = pygame.key.get_pressed()

    if key[pygame.K_a]:
        cat.left()
    elif key[pygame.K_d]:
        cat.right()

    if key[pygame.K_LEFT]:
        dog.left()
    elif key[pygame.K_RIGHT]:
        dog.right()


def read_animal_snapshots(cat, dog):
    with cat._action_lock:
        cat_snapshot = {
            "status": cat.statues,
            "x": cat.catX,
            "y": cat.catY,
            "health": cat.health,
            "energy": cat.energy,
            "beatS": cat.beatS,
            "beat_size": cat.size,
            "beat_angle": cat.angle,
            "beat_x": cat.now_x,
            "beat_y": cat.now_y,
            "defend": cat.defendStatus,
            "hurt": cat.hurtStatus,
        }

    with dog._action_lock:
        dog_snapshot = {
            "status": dog.statues,
            "x": dog.dogX,
            "y": dog.dogY,
            "health": dog.health,
            "energy": dog.energy,
            "beatS": dog.beatS,
            "beat_size": dog.size,
            "beat_angle": dog.angle,
            "beat_x": dog.now_x,
            "beat_y": dog.now_y,
            "defend": dog.defendStatus,
            "hurt": dog.hurtStatus,
        }

    return cat_snapshot, dog_snapshot


def draw_projectile(base_image, size, angle, x, y):
    projectile = pygame.transform.scale(base_image, (int(size), int(size)))
    projectile = pygame.transform.rotate(projectile, angle)
    projectile_rect = projectile.get_rect()
    projectile_rect.bottomleft = (int(x), int(y))
    screen.blit(projectile, projectile_rect)
    return projectile_rect


def handle_attack_rendering(assets, cat, dog, cat_snapshot, dog_snapshot, cat_rect, dog_rect):
    if cat_snapshot["beatS"]:
        beat_rect = draw_projectile(
            assets["fish"],
            cat_snapshot["beat_size"],
            cat_snapshot["beat_angle"],
            cat_snapshot["beat_x"],
            cat_snapshot["beat_y"],
        )
        if dog_rect.colliderect(beat_rect):
            dog.hurt()
            cat.stop_beat()

    if dog_snapshot["beatS"]:
        beat_rect = draw_projectile(
            assets["bone"],
            dog_snapshot["beat_size"],
            dog_snapshot["beat_angle"],
            dog_snapshot["beat_x"],
            dog_snapshot["beat_y"],
        )
        if cat_rect.colliderect(beat_rect):
            cat.hurt()
            dog.stop_beat()


def handle_obstacles(dt, cat, dog, cat_rect, dog_rect):
    for obstacle in obstaclelist[:]:
        obstacle.move(dt)
        obstacle_destroyed = False

        if dog_rect.colliderect(obstacle.obstacleRect):
            if obstacle.type == DOG_ENERGY:
                dog.getenergy()
                obstacle.destroy()
                obstacle_destroyed = True
            elif obstacle.type in DAMAGE_OBSTACLE_TYPES:
                dog.hurt()
                obstacle.destroy()
                obstacle_destroyed = True

        if not obstacle_destroyed and cat_rect.colliderect(obstacle.obstacleRect):
            if obstacle.type == CAT_ENERGY:
                cat.getenergy()
                obstacle.destroy()
                obstacle_destroyed = True
            elif obstacle.type in DAMAGE_OBSTACLE_TYPES:
                cat.hurt()
                obstacle.destroy()
                obstacle_destroyed = True

        if not obstacle_destroyed:
            obstacle.remove()


def Play():
    assets = load_game_assets()
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

        dt = clock.tick(100) / 1000
        count += 1
        if count == 7:
            count = 0
            q = max(200, q - 1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                handle_action_key(event, cat, dog)

        handle_movement_keys(cat, dog)
        cat.update(dt)
        dog.update(dt)

        mod.map.create_map()
        cat_snapshot, dog_snapshot = read_animal_snapshots(cat, dog)

        cat_image = cat.catStatus[cat_snapshot["status"]]
        cat_rect = cat_image.get_rect()
        cat_rect.bottomleft = (int(cat_snapshot["x"]), int(cat_snapshot["y"]))

        dog_image = dog.dogStatus[dog_snapshot["status"]]
        dog_rect = dog_image.get_rect()
        dog_rect.bottomleft = (int(dog_snapshot["x"]), int(dog_snapshot["y"]))

        dog_heart = dog.healthStatues[max(1, dog_snapshot["health"]) - 1]
        dog_heart_rect = dog_heart.get_rect()
        dog_heart_rect.bottomleft = (800, 70)

        cat_heart = cat.healthStatus[max(1, cat_snapshot["health"]) - 1]
        cat_heart_rect = cat_heart.get_rect()
        cat_heart_rect.bottomleft = (100, 70)

        cat_energy = cat.energyStatus[cat_snapshot["energy"]]
        cat_energy_rect = cat_energy.get_rect()
        cat_energy_rect.bottomleft = (100, 140)

        dog_energy = dog.energyStatus[dog_snapshot["energy"]]
        dog_energy_rect = dog_energy.get_rect()
        dog_energy_rect.bottomleft = (800, 140)

        handle_attack_rendering(assets, cat, dog, cat_snapshot, dog_snapshot, cat_rect, dog_rect)

        if cat_snapshot["defend"]:
            defend_rect = assets["cat_defend"].get_rect()
            defend_rect.bottomleft = (int(cat_snapshot["x"] - 35), int(cat_snapshot["y"] - 15))
            screen.blit(assets["cat_defend"], defend_rect)

        if dog_snapshot["defend"]:
            defend_rect = assets["dog_defend"].get_rect()
            defend_rect.bottomleft = (int(dog_snapshot["x"] - 35), int(dog_snapshot["y"] - 15))
            screen.blit(assets["dog_defend"], defend_rect)

        if cat_snapshot["hurt"]:
            hurt_rect = assets["hurt"].get_rect()
            hurt_rect.bottomleft = (int(cat_snapshot["x"] + 15), int(cat_snapshot["y"] - 80))
            screen.blit(assets["hurt"], hurt_rect)

        if dog_snapshot["hurt"]:
            hurt_rect = assets["hurt"].get_rect()
            hurt_rect.bottomleft = (int(dog_snapshot["x"] + 15), int(dog_snapshot["y"] - 80))
            screen.blit(assets["hurt"], hurt_rect)

        if random.randint(1, q) == 1:
            createdogObstacle()
            creatcatObstacle()

        handle_obstacles(dt, cat, dog, cat_rect, dog_rect)

        screen.blit(cat_image, cat_rect)
        screen.blit(dog_image, dog_rect)
        screen.blit(cat_heart, cat_heart_rect)
        screen.blit(dog_heart, dog_heart_rect)
        screen.blit(cat_energy, cat_energy_rect)
        screen.blit(dog_energy, dog_energy_rect)

        for obstacle in obstaclelist:
            screen.blit(obstacle.obstacleStatus, obstacle.obstacleRect)

        pygame.display.flip()

    with dog._action_lock:
        dog_won = dog.health > 0

    if dog_won:
        final_rect = assets["dog_win"].get_rect()
        final_rect.bottomleft = (350, 650)
        empty_heart_rect = assets["empty_heart"].get_rect()
        empty_heart_rect.bottomleft = (100, 70)
        screen.blit(assets["dog_win"], final_rect)
        screen.blit(assets["empty_heart"], empty_heart_rect)
    else:
        final_rect = assets["cat_win"].get_rect()
        final_rect.bottomleft = (300, 690)
        empty_heart_rect = assets["empty_heart"].get_rect()
        empty_heart_rect.bottomleft = (800, 70)
        screen.blit(assets["cat_win"], final_rect)
        screen.blit(assets["empty_heart"], empty_heart_rect)

    obstaclelist.clear()
    pygame.display.flip()
    time.sleep(5)


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    pygame.display.set_caption("猫狗大战")
    clock = pygame.time.Clock()
    music_play()

    while start():
        Play()
