'''
    NOTE: All code placed here is either out of use, for reference,
    or to be used/worked on later on.
'''


'''
def get_rect_angle(entity_2):
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
    return angle

def set_relative_position(object_rect, relative_rect, x, y):
    object.x = (relative_rect.x - d_rect.x) + x
    object.y = (relative_rect.y - d_rect.y) + y

def combine_hitboxes(self):
    for accessory in self.accessories:
        self.set_offset([0, 0])
        self.offset[0] += accessory.offset[0]
        self.offset[1] += accessory.offset[1]
        x_diff = abs(self.offset[0]) + (accessory.obj.hitbox.topright[0] - self.obj.hitbox.topright[0])
        y_diff = abs(self.offset[0]) + (accessory.obj.hitbox.bottomright[1] - self.obj.hitbox.bottomright[1])
        self.obj.set_hitbox(self.x, self.y, self.width + x_diff, self.height + y_diff)

def set_hitbox(self, x, y, width, height):
    self.hitbox = pygame.Rect(x, y, width, height)

malcolm = entities.entity(start_loc['malcolm'][0], start_loc['malcolm'][1], 11, 11, 'malcolm')
wings = entities.entity(0, 0, 36, 19, 'wings', 'flapping')
malcolm.add_accessory(0, 0, 16, 6, curDir + anim_path + 'accessories/horns.png', [-3, -5], True)
malcolm_speed = [2, 2]
malcolm_movement = [0, 0]

wings_movement = [0, 0]
wings.follow(malcolm.x, malcolm.y, -12, -6)

if event.key == K_f:
    wings_toggled = not wings_toggled
    if wings_toggled:
        present_entities.append(wings)
        active_movements.append(wings_movement)
    else:
        if wings in present_entities:
            present_entities.remove(wings)
        if wings_movement in active_movements:
            active_movements.remove(wings_movement)

    def set_animation(self, sequence):
        self.animation = sequence
        self.animation_frame = 0
'''
