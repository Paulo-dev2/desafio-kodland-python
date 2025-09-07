from pygame import Rect

class Wall:
    def __init__(self, x, y, wall_type='internal'):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 32
        self.wall_type = wall_type

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def draw(self, screen, images, parede_4_rotated):
        if self.wall_type == 'side':
            screen.blit(images.parede_4, (self.x, self.y))
        elif self.wall_type == 'top_bottom':
            screen.blit(parede_4_rotated, (self.x, self.y))
        else:
            # Use a deterministic but varied index for the wall image
            wall_image_index = (self.x + self.y) % len(images.walls) 
            screen.blit(images.walls[wall_image_index], (self.x, self.y))