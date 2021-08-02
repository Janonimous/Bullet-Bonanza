#!/usr/bin/python3.0

# Setup Python --------------------------------------------------------------- #
import pygame, sys, math, random, os
import animations, bullets, entities, players

# Setup Pygame/window -------------------------------------------------------- #
main_clock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('Bullet Bonanza')

# window_size should only be changed for different resolutions (later on)
# display is where everything is blitted on and display is then scaled to window_size (screen)
# field is the area where the player is confined to
window_size = (1152, 864)
screen_rect = pygame.Rect(0, 0, window_size[0], window_size[1])
display_rect = pygame.Rect(0, 0, window_size[0]/2, window_size[1]/2)
screen = pygame.display.set_mode((window_size), 0, 32)
display = pygame.Surface((display_rect[2], display_rect[3])) # surface for rendering, scaled to window_size
field = pygame.Rect(window_size[0]/8, window_size[1]/64, window_size[0]/4, (window_size[1]/2 - window_size[1]/32))

# Setup Animations/Display ----------------------------------------------------------- #

curDir = os.path.dirname(os.path.realpath(__file__)) + '/'
anim_path = 'data/images/entities/'
img_path = 'data/images/'
animations.load_animations(curDir + anim_path, 'entity_animations.txt')

bullet_img = pygame.image.load(curDir + img_path + 'projectiles/light_bullet/light_bullet.png')
heart_image = pygame.image.load(curDir + img_path + 'HUD/heart.png').convert()
heart_image.set_colorkey((0, 255, 0))

# Setup Entities and Objects ------------------------------------------------- #

start_loc = {'player': [int(field.x + field.width/2), int(field.y + field.height*3/4)], 'pyramyth': [int(field.x + field.width/2), int(field.y + field.height*3/16)]}

player = players.player(start_loc['player'][0], start_loc['player'][1], 11, 11, 'player', 3)
pyramyth = entities.entity(start_loc['pyramyth'][0], start_loc['pyramyth'][1], 31, 32, 'pyramyth')
pyramyth.set_scale(2)

global player_speed
player_speed = [2.5, 2.5]
player_movement = [0, 0]
player_moving = {'up':False, 'down':False, 'right':False, 'left':False}
player_collisions = {'top':False, 'bottom':False, 'right':False, 'left':False}

pyramyth_movement = [0, 0]
enemy_patterns = {'blink': False, 'stompshot': False, 'rapidfire': False, 'seekers': False}

present_entities = [player, pyramyth]
active_movements = [player_movement, pyramyth_movement]

projectiles = []
projectile_rects = []
seeking_projectiles = []
bullet_generator = bullets.bullet_pattern(bullet_img, projectiles, projectile_rects)
movement_generator = entities.movement_pattern(pyramyth.x, pyramyth.y)

# Functions --------------------------------------------- #

def scale_rect(rect1, rect2=None, ratio=None):
    # rect1 is scaleable; can be scaled to rect2 or a specified ratio
    if rect2 != None:
        ratio_x = rect2.width/rect1.width
        ratio_y = rect2.height/rect1.height
    else:
        ratio_x = ratio_y = ratio
    rect1.width = int(rect1.width * ratio_x)
    rect1.height = int(rect1.height * ratio_y)
    rect1.x = int(rect1.x * ratio_x)
    rect1.y = int(rect1.y * ratio_y)
    return rect1

def set_center_rect(rect):
    rect.center = (rect.x, rect.y)
    return rect.center

def get_border_rects(inner_rect, outer_rect):
    inner, outer = inner_rect, outer_rect # for shortening
    l_rect = pygame.Rect(outer.x, outer.y, (inner.x - outer.x), outer.height)
    r_rect = pygame.Rect(inner.right, outer.y, (outer.right - inner.right), outer.height)
    t_rect = pygame.Rect(outer.x, outer.y, outer.width, (inner.y - outer.y))
    b_rect = pygame.Rect(outer.x, inner.bottom, outer.width, (outer.bottom - inner.bottom))
    return [l_rect, r_rect, t_rect, b_rect]


# Main Menu ------------------------------------------------------------------ #
def menu():

    click = False

    while True:

        # Event Handler #
        click = False
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == K_RETURN:
                    game()

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        # Background #
        display.fill((0, 0, 0))

        mx, my = pygame.mouse.get_pos()

        start_button = pygame.Rect(576, 432, 200, 50)
        set_center_rect(start_button)
        if start_button.collidepoint((mx, my)):
            if click:
                game()
        pygame.draw.rect(display, (0, 255, 0), scale_rect(start_button, ratio=0.5))

        # Update #
        surf = pygame.transform.scale(display, window_size)
        screen.blit(surf, (0, 0))
        pygame.display.update()
        main_clock.tick(60)

# Main Game Loop ------------------------------------------------------------- #
def game():

    running = True
    delta_clock = pygame.time.Clock()
    FPS = 60

    HP = 3
    godmode = False
    recovery_state = False

    shoot_circular = False
    hover_idle = False

    # temporary #
    smoothboi = False
    blink = False
    stomp = False
    stomped = False
    seek = False
    counter = 0
    r_counter = 0
    f_counter = 0
    true_thyme = 0

    global player_speed # add functions and player variables to player class

    while running:

        # Event Handler ------------------------------------------------------ #
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                if event.key == K_7:
                    godmode = not godmode
                    if godmode:
                        print('oh god.')

                # WASD player movement
                if event.key == K_w:
                    player_moving['up'] = True
                if event.key == K_s:
                    player_moving['down'] = True
                if event.key == K_d:
                    player_moving['right'] = True
                if event.key == K_a:
                    player_moving['left'] = True
                if event.key == K_LSHIFT:
                    player_speed = [1.25, 1.25]

                # Temp #
                if event.key == K_SPACE:
                    shoot_circular = True
                if event.key == K_b:
                    enemy_patterns['blink'] = True
                if event.key == K_v:
                    enemy_patterns['stompshot'] = True
                if event.key == K_r:
                    enemy_patterns['rapidfire'] = not enemy_patterns['rapidfire']
                if event.key == K_x:
                    enemy_patterns['seekers'] = not enemy_patterns['seekers']

                if event.key == K_1:
                    hover_idle = not hover_idle
                    if hover_idle:
                        movement_generator.directions['down'] = True
                    else:
                        smoothboi = True
                if event.key == K_2:
                    pyramyth.x, pyramyth.y = random.randint(field.x, field.right), random.randint(field.y, field.bottom)

            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    shoot_circular = True

            if event.type == KEYUP:
                if event.key == K_w:
                    player_moving['up'] = False
                if event.key == K_s:
                    player_moving['down'] = False
                if event.key == K_d:
                    player_moving['right'] = False
                if event.key == K_a:
                    player_moving['left'] = False
                if event.key == K_LSHIFT:
                    player_speed = [2.5, 2.5]

        # Beforehand Calculations -------------------------------------------- #
        delta_time = delta_clock.tick(FPS)*0.001
        true_thyme += delta_time
        thyme = math.floor(true_thyme)
        relative_thyme = round(true_thyme - thyme, 3)

        # Background --------------------------------------------------------- #
        display.fill((0, 0, 0))

        # Player ------------------------------------------------------------- #
        player_movement = [0, 0]

        if player_moving['up'] and not player_collisions['top']:
            player_movement[1] -= player_speed[1]
        if player_moving['down'] and not player_collisions['bottom']:
            player_movement[1] += player_speed[1]
        if player_moving['left'] and not player_collisions['left']:
            player_movement[0] -= player_speed[0]
        if player_moving['right'] and not player_collisions['right']:
            player_movement[0] += player_speed[0]

        if player_movement != [0, 0]:
            action = ''
            if player_moving['up']:
                action += 'up'
            elif player_moving['down']:
                action += 'down'
            if player_moving['right']:
                action += 'right'
            elif player_moving['left']:
                action += 'left'
            if action != '':
                player.set_action(action)
        else:
            player.set_action('idle')

        if recovery_state:
            if r_counter % 10 == 0:
                first_digit = int(str(r_counter)[0])
                if first_digit % 2 == 0:
                    opacity = 100
                else:
                    opacity = 255
            player.alpha = opacity
            r_counter += 1
            if r_counter >= 60:
                r_counter = 0
                recovery_state = False
                player.alpha = 255

        player_collisions = player.move(player_movement, field, 'within', False)

        # Enemy -------------------------------------------------------------- #

        seeker_angle = pyramyth.get_rect_angle(player)
        action = entities.cardinal_direction(seeker_angle)

        if thyme % 8 == 0:
            for pattern in enemy_patterns:
                if not pattern and relative_thyme < 0.1:
                    enemy_patterns['blink'] = True

        if enemy_patterns['blink']: # might want to change to a sort of switch case-like statement later on
            enemy_patterns['blink'] = pyramyth.is_complete(enemy_patterns['blink'])
            action = action + '_blink'
            if '_blink' not in pyramyth.action:
                pyramyth.set_frame(0)
        else:
            if enemy_patterns['stompshot']:
                pyramyth.set_size(31, 40)
                enemy_patterns['stompshot'] = pyramyth.is_complete(enemy_patterns['stompshot'])
                if not enemy_patterns['stompshot']:
                    pyramyth.set_size(31, 32)
                action = 'stomp_shot'
                if pyramyth.action != action:
                    pyramyth.set_frame(0)
                stomped = pyramyth.can_occur(action)
            elif enemy_patterns['rapidfire']:
                if thyme % 5 == 0 and relative_thyme < 0.025:
                    stomped = True
                action = 'rapidfire'
                if pyramyth.action != action:
                    pyramyth.set_frame(0)
                shoot_circular = pyramyth.can_occur(action)
            elif enemy_patterns['seekers']:
                #pyramyth.set_pos(display_rect.width/2, display_rect.height/2)
                action = 'seekers'
                seek = pyramyth.can_occur(action)

        pyramyth.set_action(action, flow=True)

        if hover_idle:
            movement_generator.hover(pyramyth, pyramyth_movement, 0.1, 1)
        if smoothboi:
            if (pyramyth.x != movement_generator.origin[0]) or (pyramyth.y != movement_generator.origin[1]):
                movement_generator.reset_pos(pyramyth, True)
            else:
                smoothboi = False

        # Projectiles -------------------------------------------------------- #
        if shoot_circular:
            bullet_list = bullet_generator.circular(pyramyth.x, pyramyth.y, 1, 0, 10, 18, 3, 3)
            #bullet_list = bullet_generator.alternating_spiral(pyramyth.x, pyramyth.y, 1, 0, 9, 10, 3, 3, 4)
            for b in bullet_list:
                b.set_offset([4, 4])
                projectiles.append(b)
                projectile_rects.append(b.rect)
            shoot_circular = False

        if stomped:
            bullet_list = bullet_generator.circular(pyramyth.x, pyramyth.y, 1, 0, 30, 5, 3, 3)
            for b in bullet_list:
                b.set_offset([4, 4])
                projectiles.append(b)
                projectile_rects.append(b.rect)
            stomped = False

        if seek:
            s_offsets = [[-20, -10, 10, 20], [0, 15, 15, 0]]
            s_vels = [[-0.7, -0.7, 0.7, 0.7], [0.7, 0.7, 0.7, 0.7]]
            '''for i in range(4):
                b_obj = bullets.bullet(pyramyth.x + s_offsets[0][i], pyramyth.y + s_offsets[1][i], 9, 9, s_vels[0][i], s_vels[1][i], 3, 3, bullet_img)
                b_obj.set_offset([4, 4])
                projectiles.append(b_obj)
                projectile_rects.append(b_obj.rect)
                seeking_projectiles.append(b_obj)'''
            b_obj = bullets.bullet(pyramyth.x, pyramyth.y, 9, 9, -0.7, 0.7, 3, 3, bullet_img)
            b_obj.set_offset([4, 4])
            projectiles.append(b_obj)
            projectile_rects.append(b_obj.rect)
            seeking_projectiles.append(b_obj)
            seek = False

        for s in seeking_projectiles:
            if round(s.lifetime, 2) == 2.5 and s.angle == 0:
                print(s.vel_angle())
                s_angle = s.get_angle(player, radians=False) #- s.vel_angle()
                #print(s_angle)
                s.set_angle(s_angle)
            else:
                s.set_angle(0)


        if not (godmode or recovery_state):
            bullet_rect_collisions = entities.detect_rect_collisions(player.obj.rect, projectile_rects, enumerated=True)
            if len(bullet_rect_collisions) != 0:
                for bullet_rect in bullet_rect_collisions:
                    bullet_index = bullet_rect[0]
                    hit = entities.detect_mask_collision(player.image, projectiles[bullet_index].image, player.obj.rect, bullet_rect[1])
                    if hit:
                        HP -= 1
                        recovery_state = True
                        projectiles.pop(bullet_index)
                        projectile_rects.pop(bullet_index)

        # Display ------------------------------------------------------------ #
        for p in projectiles:
            if p.lifetime <= 0:# or not projectile_rects[projectiles.index(p)].colliderect(display_rect):
                projectiles.pop(projectiles.index(p))
                projectile_rects.pop(projectile_rects.index(p))
                if p in seeking_projectiles:
                    seeking_projectiles.pop(seeking_projectiles.index(p))
            p.process(delta_time)
            p.display(display)

        entities.change_frames(present_entities, 1)
        player.display(display, player_movement)
        pyramyth.display(display, pyramyth_movement, True)

        border_rects = get_border_rects(field, screen_rect)
        for border_rect in border_rects:
            pygame.draw.rect(display, (8, 24, 144), border_rect)

        # HUD #
        if HP != 0:
            for h in range(HP):
                display.blit(heart_image, (10 + (h)*18, 10))

        # Update #
        surf = pygame.transform.scale(display, window_size)
        screen.blit(surf, (0, 0))
        pygame.display.update()
        main_clock.tick(60)


menu()
