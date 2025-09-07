from pygame import Rect

class Character:
    def __init__(self, x, y, idle_images, walk_images):
        self.x = x
        self.y = y
        self.idle_images = idle_images
        self.walk_images = walk_images
        self.current_images = idle_images
        self.image_index = 0
        self.direction = 1  # 1 for right, -1 for left
        self.moving = False
        self.alive = True
        self.width = 32
        self.height = 32

    def update_animation(self, animation_timer, animation_speed):
        if animation_timer % animation_speed == 0:
            self.image_index = (self.image_index + 1) % len(self.current_images)

    def get_current_image(self):
        return self.current_images[self.image_index]

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def is_colliding(self, other):
        return self.get_rect().colliderect(other.get_rect())

    def draw(self, screen):
        screen.blit(self.get_current_image(), (self.x, self.y))