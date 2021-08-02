import pygame, math, random
from pygame.locals import *

global b_colorkey
b_colorkey = (0, 0, 0)

def set_global_colorkey(colorkey):
    global b_colorkey
    b_colorkey = colorkey

class bullet:

    def __init__(self, x, y, width, height, x_vel, y_vel, lifetime, speed, image, offset=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = x_vel
        self.y_vel = y_vel
        self.lifetime = lifetime # seconds
        self.speed = speed
        self.image = None
        self.set_image(image)
        if offset == None:
            self.offset = [0, 0]
        else:
            self.offset = offset
        self.angle = 0 # relative to another object
        #print(self.angle)
        self.rotation = 0 # relative to its axis

    def set_offset(self, offset):
        self.offset = offset
        self.x -= offset[0]
        self.y -= offset[1]

    def reset_offset(self):
        self.x += offset[0]
        self.y += offset[1]
        self.offset = [0, 0]

    def set_image(self, img):
        if isinstance(img, str):
            self.image = pygame.image.load(img)
        else:
            self.image = img
        if self.image != None:
            self.image.set_colorkey(b_colorkey)
            if self.rect == None:
                width, height = self.image.get_size()
                self.rect = pygame.Rect(self.x, self.y, width, height)

    def set_angle(self, angle):
        self.angle = angle

    def set_rotation(self, rotation):
        self.rotation = rotation

    def detect_rect_collisions(self, rect_collidables):
        collision_list = []
        for rect in rect_collidables:
            if self.rect.colliderect(rect):
                collision_list.append(rect)
        return collision_list

    def vel_angle(self):
        base_angle = math.degrees(math.atan2(self.y_vel, self.x_vel))
        print(self.x_vel)
        print(base_angle)
        angle = base_angle
        if self.x_vel < 0:
            if self.y_vel < 0:
                angle = -(180 - base_angle)
            else:
                angle = 180 - base_angle
        return angle

    def get_angle(self, target, radians=True):
        x1 = self.x + int(self.width/2)
        y1 = self.y + int(self.height/2)
        x2 = target.x + int(target.width/2)
        y2 = target.y + int(target.height/2)
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

    def process(self, delta):
        vel_vector = pygame.math.Vector2(self.x_vel, self.y_vel)
        self.x_vel = round(vel_vector.rotate_rad(delta*self.angle).x, 4)
        self.y_vel = round(vel_vector.rotate_rad(delta*self.angle).y, 4)
        self.x += self.x_vel * self.speed
        self.y += self.y_vel * self.speed
        self.rect.x, self.rect.y = self.x, self.y
        self.lifetime -= delta

    def display(self, surf):
        surf.blit(self.image, (self.x, self.y))

class aura:
    # make one for basic circle/shape aura
    # make one more representative of the object's outline; an aura produced by the object's mask(outline)
    pass

class bullet_pattern:

    def __init__(self, image, obj_list, rect_list):
        self.image = image
        self.wave = 1
        self.pattern_type = None

    def update_pattern(self, type):
        if self.pattern_type != type:
            self.pattern_type = type
            self.wave = 1
        else:
            self.wave += 1

    def circular(self, x, y, x_vel, y_vel, amount, offset, lifetime, speed, clockwise=True):
        self.update_pattern('circular')
        image = self.image
        width, height = image.get_width(), image.get_height()
        rotation_addup = 360/amount
        true_offset = offset*self.wave
        if not clockwise:
            true_offset = -true_offset
        bullet_list = []

        for b in range(amount):
            vel_vector = pygame.math.Vector2(x, y)
            vel_vector = vel_vector.normalize()
            x_vel = vel_vector.rotate(b*rotation_addup+true_offset).x
            y_vel = vel_vector.rotate(b*rotation_addup+true_offset).y
            b_obj = bullet(x, y, width, height, x_vel, y_vel, lifetime, speed, image)
            bullet_list.append(b_obj)

        return bullet_list

    def alternating_spiral(self, x, y, x_vel, y_vel, amount, offset, lifetime, speed, switch=2):
        cwise = True
        rmdr = self.wave % switch
        coerced_rmdr = self.wave - rmdr
        if (rmdr == 0 and self.wave % (switch*2) != 0) or coerced_rmdr % (switch*2) != 0:
            cwise = False
        return self.circular(x, y, x_vel, y_vel, amount, offset, lifetime, speed, cwise)
