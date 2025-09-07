from pygame import Rect

class Treasure:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32

    def get_rect(self): 
        return Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, images):
        screen.blit(images.treasure, (self.x, self.y))