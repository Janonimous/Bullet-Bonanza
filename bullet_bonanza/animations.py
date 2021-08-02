import pygame, json

global a_colorkey
a_colorkey = (0, 255, 0)

global animation_database
animation_database = {}

global o_frames_database
o_frames_database = {}

# Spritesheets --------------------------------------------------------------- #

class spritesheet:

    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace('png', 'json')
        self.entity_name = self.get_entity_name()
        try:
            with open(self.meta_data) as f:
                self.data = json.load(f) # parse file to json format
            f.close()
        except:
            print('Something went wrong while loading the json spritesheet file')

    def get_entity_name(self):
        start = self.filename.rfind('/') +1
        end = self.filename.index('.')
        entity_name = self.filename[start:end]
        return entity_name

    def get_sprite(self, x, y, w, h):
        sprite = pygame.Surface((w, h))
        sprite.set_colorkey(a_colorkey)
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite

    def get_sprite_sequence(self, action):
        frames = self.data['animations'][action]
        sequence = []
        timings = []
        tags = {}
        o_frames = []
        for i, frame in enumerate(frames):
            if frame[-4:] == '.png':
                name = '{action}_{i}.png'.format(action = action, i = i)
                coordinates, size = frames[name]['coordinates'], frames[name]['size']
                sequence.append(self.get_sprite(coordinates['x'], coordinates['y'], size['w'], size['h']))
            # ¯\_(ツ)_/¯ Apologies for the weird naming below
            if frame == 'timings':
                timings = frames[frame]
            if frame == 'tags':
                tags = frames[frame]
            if frame == 'occurance_frames':
                o_frames = frames[frame]
        return [sequence, timings, tags], o_frames

    def add_animation_sequence(self, e_type, action, anim_database, o_frames_db=None):
        try:
            anim_database[e_type][action], o_frames = self.get_sprite_sequence(action)
        except:
            anim_database[e_type] = {}
            anim_database[e_type][action], o_frames = self.get_sprite_sequence(action)
        if o_frames_db != None and o_frames != []:
            try:
                o_frames_db[e_type][action] = o_frames
            except:
                o_frames_db[e_type] = {}
                o_frames_db[e_type][action] = o_frames

def flip(img, boolean=True):
    return pygame.transform.flip(img, boolean, False)

class animation:

    def __init__(self, action: str=None):
        self.image = None
        self.animation = None
        self.timings = []
        self.timing = 0
        self.animation_frame = 0
        self.animation_tags = []
        self.flip = False
        self.default_action = 'idle'
        if action == None:
            self.action = self.default_action
        else:
            self.action = ''
        self.alpha = None
        self.markers = []

    def set_flip(self, bool):
        self.flip = bool

    def set_frame(self, amount):
        self.animation_frame = amount

    def set_animation_tags(self, tags):
        self.animation_tags = tags

    def set_action(self, action_id, force=False, flow=False):
        action = action_id
        if action_id == None:
            action = 'idle'
        if (self.action == action_id) and (force == False):
            pass
        else:
            self.action = action
            anim = animation_database[self.type][action]
            self.animation = anim[0]
            self.timings = anim[1]
            self.timing = 0
            self.set_animation_tags(anim[2])
            if not flow:
                self.animation_frame = 0

    def change_frame(self, amount):
        if self.timing == self.timings[self.animation_frame]:
            self.animation_frame += amount
            self.timing = 0
        else:
            self.timing += 1
        if self.animation != None:
            while self.animation_frame < 0:
                if 'loop' in self.animation_tags:
                    self.animation_frame += len(self.animation)
                else:
                    self.animation_frame = 0
            while self.animation_frame >= len(self.animation):
                if 'loop' in self.animation_tags:
                    self.animation_frame -= len(self.animation)
                elif 'once' in self.animation_tags:
                    self.animation_frame = 0
                    self.action = self.default_action
                    self.markers.append('complete')
                else:
                    self.animation_frame = len(self.animation)-1

    def get_image(self):
        image = None
        if self.animation == None:
            if self.image != None:
                image = flip(self.image, self.flip).copy()
        else:
            # NOTICE: Line below based off entity display animation_database;
            # if used with different objects change database to be more simpler/generic
            image = flip(animation_database[self.type][self.action][0][self.animation_frame], self.flip).copy()
        return image

    def display(self, surface, x, y):
        image_to_render = self.get_image()
        if image_to_render != None:
            self.image = image_to_render
            image_to_render = pygame.transform.rotate(image_to_render, self.rotation)
            if self.alpha != None:
                image_to_render.set_alpha(self.alpha)
            surface.blit(image_to_render, (x, y))

    def can_occur(self, type, action): #dunno, this is terribly written isn't it
        can = False
        if type in o_frames_database:
            if action in o_frames_database[type]:
                for f in o_frames_database[type][action]:
                    if self.animation_frame == f and self.timing == 0:
                        can = True
        return can

    def is_complete(self, bool=True):
        if 'complete' in self.markers:
            bool = False
            self.markers = []
        return bool

# Other Useful Functions ----------------------------------------------------- #

'''
        NOTE: I use a .txt file for the .png image and it's associated actions.
        Then a list of actions is created and is iterated through pulling
        frames from the .png with specifications from the entity's .json file
        ¯\_(ツ)_/¯ *Apollo-cheese if a little convoluted.
'''

def load_animations(base_path, anim_file, database=animation_database, o_frames_db=o_frames_database):
    f = open(base_path + anim_file, 'r')
    data = f.read()
    f.close()
    for action_set in data.split('\n'):
        if action_set[:4] == 'skip':
            continue
        sections = action_set.split(' ')
        img_file = sections[0]
        actions = sections[1].split(';')
        img_name = img_file[:-4] # Just the name without the .png suffix
        actions_path = (img_name + '/' + img_file)
        sheet = spritesheet(base_path + actions_path)
        for action in actions:
            sheet.add_animation_sequence(img_name, action, database, o_frames_db)

# NOTE: I was going to try to implement animation database and o_frames as class
# variables for the animation class but I haven't figured out how class variables
# can be accessed by class methods (specifically ones with a self parameter).
