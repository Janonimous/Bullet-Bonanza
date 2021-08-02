#!/usr/bin/python3.9
# Setup Python --------------------------------------------------------------- #
import pygame, sys, math, random, os
import data.engine as e

# Setup Pygame/window -------------------------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('Bullet Bonanza')

# WINDOW_SIZE should only be changed for different resolutions
# display is where everything is blitted on and display is then scaled to WINDOW_SIZE
# field is the main area where the player is confined to
WINDOW_SIZE = (1152, 864)
screen = pygame.display.set_mode((WINDOW_SIZE), 0, 32)
display = pygame.Surface((WINDOW_SIZE[0]/2, WINDOW_SIZE[1]/2)) # surface for rendering, scaled to WINDOW_SIZE
field = pygame.Rect(WINDOW_SIZE[0]/16, WINDOW_SIZE[1]/64, WINDOW_SIZE[0]/4, (WINDOW_SIZE[1]/2 - WINDOW_SIZE[1]/32))

field_rects = [field]

curDir = os.path.dirname(os.path.realpath(__file__))
e.load_animations(curDir + '/data/images/entities/')

initial_location = {'player': [(WINDOW_SIZE[0]/16 * 3), (WINDOW_SIZE[1]/8 * 3)], 'enemy': [(WINDOW_SIZE[0]/16 * 3), (WINDOW_SIZE[1]/16)]}

player = e.entity(initial_location['player'][0], initial_location['player'][1], 11, 11, 'player')
player_speed = [3, 3]
player_movement = [0, 0]

moving = {'up':False, 'down':False, 'right':False, 'left':False}
collision_types = {'top':False, 'bottom':False, 'right':False, 'left':False}

enemy = e.entity(initial_location['enemy'][0], initial_location['enemy'][1], 11, 11, 'enemy')
bobble_toggled = False
flight_toggled = False
reset_smooth = False
enemy_movement = [0, 0]

horns = pygame.image.load(curDir + '/data/images/entities/accessories/horns.png').convert()
horns.set_colorkey((0, 0, 0))
wings = e.entity((enemy.x - 12), (enemy.y - 6), 35, 19, 'wings', 'flapping')

intensity = 1

def reset_toggles():
    bobble_toggled = False
    flight_toggled = False

def look_towards(seeker_location, target_location):
    dist_x = target_location[0] - seeker_location[0]
    dist_y = target_location[1] - seeker_location[1]

    segments = [-70, -20, 20, 70, 110, 160, 200, 250]
    angle = 0

    # Calculate angle and adjust accordingly
    if dist_x != 0:
        angle = math.atan(dist_y / dist_x)
        if dist_x < 0:
            angle += math.pi
        angle = math.degrees(angle)
    else:
        if dist_y > 0:
            angle = 90
        elif dist_y < 0:
            angle = 270

    # Set animation of enemy based on its angle to its target
    if angle > segments[7] or angle < segments[0]:
        enemy.set_action('lookUp')
    if (angle > segments[0] and angle < segments[1]) or (angle > segments[6] and angle < segments[7]):
        enemy.set_action('lookUpperSide')
    if (angle > segments[5] and angle < segments[6]) or (angle > segments[1] and angle < segments[2]):
        enemy.set_action('lookSide')
    if (angle > segments[2] and angle < segments[3]) or (angle > segments[4] and angle < segments[5]):
        enemy.set_action('lookLowerSide')
    if angle > segments[3] and angle < segments[4]:
        enemy.set_action('lookDown')

    if angle > 90:
        enemy.set_flip(True)
    elif angle <= 90:
        enemy.set_flip(False)

def bobble(entity, movement):
    # Create center coordinate pairs to compare
    initial_center = [initial_location[entity.type][0] + (entity.size_x / 2), initial_location[entity.type][1] + (entity.size_y / 2)]
    current_center = [entity.x + (entity.size_x / 2), entity.y + (entity.size_y / 2)]

    # Check if there is movement and adjust it accordingly (increment/decrement)
    if movement[0] != 0:
        if (current_center[0] + 0.1) > initial_center[0]:
            movement[0] -= 0.05
        if current_center[0] < initial_center[0]:
            movement[0] += 0.05

    if movement[1] != 0:
        if (current_center[1] + 0.1) > initial_center[1]:
            movement[1] -= 0.05
        if current_center[1] < initial_center[1]:
            movement[1] += 0.05

    entity.x += movement[0]
    entity.y += movement[1]

def reset_pos(entity, position):
    entity.set_pos(position[0], position[1])
    initial_location[entity.type] = [position[0], [position[1]]]

# Loop ----------------------------------------------------------------------- #
while True:

    # Background ------------------------------------------------------------- #
    display.fill((5, 15, 89))
    pygame.draw.rect(display, (0, 0, 0), field)


    # Player ----------------------------------------------------------------- #
    # Move player accordingly based on previous input
    player_movement = [0, 0]
    if moving['up'] and not collision_types['top']:
        player_movement[1] -= player_speed[1]
    if moving['down'] and not collision_types['bottom']:
        player_movement[1] += player_speed[1]
    if moving['left'] and not collision_types['left']:
        player_movement[0] -= player_speed[0]
    if moving['right'] and not collision_types['right']:
        player_movement[0] += player_speed[0]

    # Set animations
    if player_movement != [0, 0]:
        if moving['right'] or moving['left']:
            if moving['up']:
                player.set_action('moveUpperSide')
            elif moving['down']:
                player.set_action('moveLowerSide')
            else:
                player.set_action('moveSide')
        else:
            if moving['up']:
                player.set_action('moveUp')
            elif moving['down']:
                player.set_action('moveDown')
    else:
        player.set_action('idle')
    if player_movement[0] > 0:
        player.set_flip(False)
    if player_movement[0] < 0:
        player.set_flip(True)

    collision_types = player.move_within(player_movement, field_rects)


    # Enemy ------------------------------------------------------------------ #
    look_towards([enemy.x, enemy.y], [player.x, player.y])

    #if reset_smooth:
        #reset_pos_smooth(enemy, initial_location['enemy'], (enemy.x, enemy.y))

    if bobble_toggled or flight_toggled:
        bobble(enemy, enemy_movement)

    wings_movement = [(enemy.x - wings.x) - 12, (enemy.y - wings.y) - 6]


    # Projectiles ------------------------------------------------------------ #



    # Draw Scene ------------------------------------------------------------- #
    player.change_frame(1)
    player.display(display, player_movement)

    enemy.change_frame(1)
    enemy.display(display, enemy_movement)
    display.blit(horns, (enemy.x - 3, enemy.y - 5))

    if flight_toggled or bobble_toggled:
        wings.change_frame(1)
        wings.display(display, wings_movement)

    # Buttons ---------------------------------------------------------------- #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()

            # WASD player movement
            if event.key == K_UP or event.key == K_w:
                moving['up'] = True
            if event.key == K_DOWN or event.key == K_s:
                moving['down'] = True
            if event.key == K_RIGHT or event.key == K_d:
                moving['right'] = True
                facing_right = True
            if event.key == K_LEFT or event.key == K_a:
                moving['left'] = True
                facing_right = False

            # Enemy movement modes, and reset
            if event.key == K_1: # Idle Flying
                flight_toggled = not flight_toggled
                if flight_toggled:
                    reset_toggles()
                    enemy_movement = [0, 0.5]
                else:
                    enemy_movement = [0, 0]
                    reset_pos(wings, ((enemy.x - wings.x) - 12, (enemy.y - wings.y) - 6))
                    initial_location['enemy'] = [enemy.x, enemy.y]#[(enemy.x - wings.x) - 12, (enemy.y - wings.y) - 6]
            if event.key == K_2: # Bobbling around
                bobble_toggled = not bobble_toggled
                if bobble_toggled:
                    reset_toggles()
                    enemy_movement = [(random.randint(12, 15) * intensity) / 10, (random.randint(4, 6) * intensity) / 10]
                else:
                    enemy_movement = [0, 0]
                    reset_pos(enemy, (enemy.x, enemy.y))
                    initial_location['enemy'] = [enemy.x, enemy.y]

            if event.key == K_r: # (Smooth) Reset
                enemy.set_pos(WINDOW_SIZE[0]/16 * 3, WINDOW_SIZE[1]/16)
                initial_location['enemy'] = [WINDOW_SIZE[0]/16 * 3, WINDOW_SIZE[1]/16]

            if event.key == K_t: # Test button
                enemy.x, enemy.y = player.x, player.y
        if event.type == KEYUP:
            if event.key == K_UP or event.key == K_w:
                moving['up'] = False
            if event.key == K_DOWN or event.key == K_s:
                moving['down'] = False
            if event.key == K_RIGHT or event.key == K_d:
                moving['right'] = False
            if event.key == K_LEFT or event.key == K_a:
                moving['left'] = False

    # Update ----------------------------------------------------------------- #
    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    mainClock.tick(60)
