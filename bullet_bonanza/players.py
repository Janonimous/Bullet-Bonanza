from entities import entity

# Players -------------------------------------------------------------------- #

class player(entity):

    def __init__(self, x, y, width, height, e_type, hp, action=None):
        super().__init__(x, y, width, height, e_type, action)
        self.hitpoints = hp

    #def move(self, )
