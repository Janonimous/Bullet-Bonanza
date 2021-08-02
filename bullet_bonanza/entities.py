import pygame, math, os, json, sys
import animations
from pygame.locals import *

global e_colorkey # entity colorkey
e_colorkey = (0, 255, 0)

global animation_database # stores entity's frames sequentially
animation_database = {}

def set_global_colorkey(colorkey):
    global e_colorkey
    e_colorkey = colorkey

def detect_rect_collisions(object_collider, object_list, enumerated=False):
    collision_list = []
    if enumerated:
        list_enumerated = enumerate(object_list)
        for obj in list_enumerated:
            if obj[1].colliderect(object_collider):
                collision_list.append(obj)
        return collision_list
    for obj in object_list:
        if obj.colliderect(object_collider):
            collision_list.append(obj)
    return collision_list

def detect_mask_collision(img1, img2, rect1, rect2):
    mask1 = pygame.mask.from_surface(img1) # reason for all the conversion is if img is not initially a surf;
    mask2 = pygame.mask.from_surface(img2) # would make change if img is already Surface type

    surf1 = mask1.to_surface(setcolor=(0, 255, 0)) # the surf (collision area) won't be visible unless blitted
    surf1.set_colorkey(e_colorkey)
    surf2 = mask2.to_surface(setcolor=(0, 255, 0))
    surf2.set_colorkey(e_colorkey)

    mask1 = pygame.mask.from_surface(surf1)
    mask2 = pygame.mask.from_surface(surf2)

    x_offset = round(rect1.x - rect2.x)
    y_offset = round(rect1.y - rect2.y)

    if mask1.overlap(mask2, (x_offset, y_offset)) != None:
        return True
    return False

# 2d physics objects --------------------------------------------------------- #

class physics_object(object):

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    # Basic rect collision
    # Mainly for rect-like obstacle collision
    def move_against(self, movement, blocks, rounded):
        self.x += movement[0]
        self.rect.x = int(self.x)
        if not isinstance(blocks, list):
            blocks = [blocks]
        blocks_collided_list = detect_rect_collisions(self.rect, blocks)
        collision_types = {'top':False, 'bottom':False, 'right':False, 'left':False}
        for block in blocks_collided_list:
            if movement[0] > 0:
                self.rect.right = block.left
                collision_types['right'] = True
            elif movement[0] < 0:
                self.rect.left = block.right
                collision_types['left'] = True
            if rounded:
                self.x = self.rect.x
        self.y += movement[1]
        self.rect.y = int(self.y)
        blocks_collided_list = detect_rect_collisions(self.rect, blocks)
        for block in blocks_collided_list:
            if movement[1] > 0:
                self.rect.bottom = block.top
                collision_types['bottom'] = True
            elif movement[1] < 0:
                self.rect.top = block.bottom
                collision_types['top'] = True
            if rounded:
                self.y = self.rect.y
        return collision_types

    ''' NOTE: the use of the rounded variable allows for decimal movement '''
    # Mainly for keeping rect-like objects within a certain area
    def move_within(self, movement, bounding_boxes, rounded):
        if not isinstance(bounding_boxes, list):
            bounding_boxes = [bounding_boxes]
        collision_types = {'top':False, 'bottom':False, 'right':False, 'left':False}
        for box in bounding_boxes:
            if self.rect.colliderect(box):
                self.x += movement[0]
                self.rect.x = math.floor(self.x)
                if self.rect.right >= box.right:
                    self.rect.right = box.right
                    collision_types['right'] = True
                elif self.rect.left <= box.left:
                    self.rect.left = box.left
                    collision_types['left'] = True
                if rounded or collision_types['right']:
                    self.x = self.rect.x

                self.y += movement[1]
                self.rect.y = math.floor(self.y)
                if self.rect.top <= box.top:
                    self.rect.top = box.top
                    collision_types['top'] = True
                elif self.rect.bottom >= box.bottom:
                    self.rect.bottom = box.bottom
                    collision_types['bottom'] = True
                if rounded or collision_types['bottom']:
                    self.y = self.rect.y
        return collision_types

# Entities ------------------------------------------------------------------- #

'''
    NOTE: Entities created from the Entity class should have a corresponding animation
    sequence already loaded into the animation database from the Spritesheet class
'''

def simple_entity(x, y, e_type):
    return entity(x, y, 1, 1, e_type)

def flip(img, boolean=True):
    return pygame.transform.flip(img, boolean, False)

class entity(animations.animation):

    def __init__(self, x, y, width, height, e_type, action: str=None):
        super().__init__(action)
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obj = physics_object(x, y, width, height)
        self.type = e_type
        self.offset = [0, 0]
        self.scale = 1
        if action == None:
            self.action = 'idle'
        else:
            self.action = ''
        self.set_action(action)
        self.alpha = None
        self.accessories = []
        self.mask = None

    def rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def set_size(self, width, height):
        self.width = width
        self.height = height
        self.obj = physics_object(self.x, self.y, width, height)

    def set_offset(self, offset):
        self.offset = offset

    def set_scale(self, scale):
        self.scale = scale

    def set_mask(self, image=None):
        if self.image != None and image != None:
            image = self.image
        if image != None:
            self.mask = pygame.mask.from_surface(image)

    def add_accessory(self, x, y, width, height, path, offset=[0, 0], visible=False):
        accessory = accessories(x, y, width, height)
        accessory.get_image(path)
        accessory.set_offset(offset, self.x, self.y)
        accessory.set_visible(visible)
        self.accessories.append(accessory)

    def move(self, movement, collidables, type='against', rounded=True):
        collisions = {}
        if type == 'against':
            collisions = self.obj.move_against(movement, collidables, rounded)
        if type == 'within':
            collisions = self.obj.move_within(movement, collidables, rounded)
        self.x = self.obj.x - self.offset[0]
        self.y = self.obj.y - self.offset[1]
        return collisions

    def get_rect_angle(self, entity_2, radians=True):
        x1 = self.x + int(self.width/2)
        y1 = self.y + int(self.height/2)
        x2 = entity_2.x + int(entity_2.width/2)
        y2 = entity_2.y + int(entity_2.height/2)
        dist_x = x2 - x1
        dist_y = y2 - y1
        if dist_x != 0:
            angle = math.atan2(dist_y, dist_x)
        else:
            angle = 0
            if dist_y > 0:
                angle = math.pi/2
            if dist_y < 0:
                angle = -math.pi/2
        if angle < 0:
            diff = angle + math.pi
            angle = abs(angle) + (diff*2)
        if not radians:
            angle = math.degrees(angle)
            if angle < 0:
                angle = 360 + angle
        return angle

    def get_image(self):
        image = None
        if self.animation == None:
            if self.image != None:
                image = flip(self.image, self.flip).copy()
        else:
            image = flip(animations.animation_database[self.type][self.action][0][self.animation_frame], self.flip).copy()
        return image

    def display(self, surface, movement, centered=False):
        image_to_render = self.get_image()
        if image_to_render != None:
            self.image = image_to_render
            x, y = self.x + movement[0], self.y + movement[1]
            width, height = self.width, self.height
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            if self.scale != None:
                width, height = self.width*self.scale, self.height*self.scale
                image_to_render = pygame.transform.scale(image_to_render, (width, height))
            if centered:
                x, y = x - (width/2), y - (height/2)
            surface.blit(image_to_render, (x, y))
            for accessory in self.accessories:
                accessory.display(surface, self.x, self.y)

    def follow(self, target_x, target_y, offset_x=0, offset_y=0):
        new_x = target_x + offset_x
        new_y = target_y + offset_y
        self.set_offset([offset_x, offset_y])
        self.set_pos(new_x, new_y)

    def can_occur(self, action): #spaghet code
        o_frames_db = animations.o_frames_database
        can = False
        if self.type in o_frames_db:
            if action in o_frames_db[self.type]:
                for f in o_frames_db[self.type][action]:
                    if self.animation_frame == f and self.timing == 0:
                        can = True
        return can


# Accessories ---------------------------------------------------------------- #

# Images attached to a main entity
class accessories():

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obj = physics_object(x, y, width, height)
        self.image = None
        self.flip = False
        self.offset = [0, 0]
        self.alpha = None
        self.visible = False

    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.obj.x = x
        self.obj.y = y
        self.obj.rect.x = x
        self.obj.rect.y = y

    def set_offset(self, offset, entity_x=0, entity_y=0):
        self.offset = offset
        self.obj.rect.x = entity_x + self.offset[0]
        self.obj.rect.y = entity_y + self.offset[1]
        self.x = self.obj.rect.x
        self.y = self.obj.rect.y

    def set_visible(self, visible):
        self.visible = visible

    def get_image(self, path):
        self.image = pygame.image.load(path).convert()
        self.image.set_colorkey(e_colorkey)

    def display(self, surface, entity_x=0, entity_y=0):
        self.set_offset(self.offset, entity_x, entity_y)
        surface.blit(self.image, (self.x, self.y))

# Movement Patterns ---------------------------------------------------------- #

class movement_pattern():

    def __init__(self, x_origin, y_origin, directions: dict=None):
        self.origin = [x_origin, y_origin]
        if directions == None:
            self.directions = {'up':False, 'down':False, 'right':False, 'left':False}
        else:
            self.directions = directions

    def set_origin(self, origin):
        self.origin = origin

    def reset_pos(self, entity, smooth=False, speed=15):
        self.directions = {'up':False, 'down':False, 'right':False, 'left':False}
        if smooth:
            dist_x, dist_y = entity.x - self.origin[0], entity.y - self.origin[1]
            entity.x = entity.x - (dist_x/speed) if round(dist_x, 1) != 0 else self.origin[0]
            entity.y = entity.y - (dist_y/speed) if round(dist_y, 1) != 0 else self.origin[1]
        else:
            entity.x, entity.y = self.origin[0], self.origin[1]

    def hover(self, entity, movement, vel_increase, y_limit):
        if vel_increase > y_limit:
            vel_increase = y_limit
        if movement[1] + vel_increase > y_limit:
            self.directions['down'] = False
            self.directions['up'] = True
        if movement[1] - vel_increase < -y_limit:
            self.directions['up'] = False
            self.directions['down'] = True

        if self.directions['down']:
            movement[1] += vel_increase
        if self.directions['up']:
            movement[1] -= vel_increase

        entity.y += movement[1]


# Other Useful Functions  ---------------------------------------------------- #

def change_frames(entities, amount):
    for entity in entities:
        entity.change_frame(amount)

def display_entities(surface, entities, movements):
    for i, entity in enumerate(entities):
        entity.display(surface, movements[i], True)

def cardinal_direction(angle, spacing=(math.pi/8)):
    # List below starts at right because that's where angle 0 is using atan2
    # Goes clockwise (E to NE) instead of counterclockwise (through the quadrants) due to pygame's reversed y-axis
    directions = ['right', 'downright', 'down', 'downleft', 'left', 'upleft', 'up', 'upright']

    relevant_direction = None
    direction_angle = 0
    for d in range(len(directions)):
        lower_limit = direction_angle - spacing
        upper_limit = direction_angle + spacing

        if lower_limit < 0:
            lower_limit = (math.pi*2) - spacing
            if (angle >= lower_limit) or (angle < upper_limit):
                relevant_direction = directions[d]

        if lower_limit <= angle < upper_limit:
            relevant_direction = directions[d]

        direction_angle += (math.pi/4)
    return relevant_direction
