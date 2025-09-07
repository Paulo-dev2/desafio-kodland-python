import pygame

class Camera:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.camera = pygame.Rect(0, 0, width, height)

    def apply(self, entity):
        return entity.move(self.camera.topleft)

    def update(self, target, screen_width, screen_height):
        x = -target.centerx + int(screen_width / 2)
        y = -target.centery + int(screen_height / 2)

        # limit scrolling to map size
        x = min(0, x)  # left
        y = min(0, y)  # top
        x = max(-(self.width - screen_width), x)  # right
        y = max(-(self.height - screen_height), y)  # bottom
        
        self.camera = pygame.Rect(x, y, self.width, self.height)