import random
from character import Character

class Enemy(Character):
    def __init__(self, x, y, images):
        super().__init__(x, y,
                         [images.enemy_idle1, images.enemy_idle2],
                         [images.enemy_walk1, images.enemy_walk2])
        self.move_timer = 0
        self.move_duration = random.randint(30, 90)
        self.move_direction = random.choice(['left', 'right', 'up', 'down'])

    def update(self, walls, WIDTH, HEIGHT, ENEMY_SPEED):
        previous_x, previous_y = self.x, self.y

        # Handle movement based on current direction
        self.move_timer += 1
        if self.move_timer >= self.move_duration:
            self.move_timer = 0
            self.move_duration = random.randint(30, 90)
            self.move_direction = random.choice(['left', 'right', 'up', 'down'])

        if self.move_direction == 'left':
            self.x -= ENEMY_SPEED
            self.direction = -1
        elif self.move_direction == 'right':
            self.x += ENEMY_SPEED
            self.direction = 1
        elif self.move_direction == 'up':
            self.y -= ENEMY_SPEED
        elif self.move_direction == 'down':
            self.y += ENEMY_SPEED

        # Keep within screen bounds
        if self.x < 0:
            self.x = 0
            self.move_direction = 'right'
        elif self.x > WIDTH - self.width:
            self.x = WIDTH - self.width
            self.move_direction = 'left'
        if self.y < 0:
            self.y = 0
            self.move_direction = 'down'
        elif self.y > HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.move_direction = 'up'

        # Check for wall collisions
        for wall in walls:
            if self.get_rect().colliderect(wall.get_rect()):
                self.x, self.y = previous_x, previous_y
                # Change direction upon hitting a wall
                possible_directions = ['left', 'right', 'up', 'down']
                if self.move_direction in possible_directions:
                    possible_directions.remove(self.move_direction)
                if possible_directions:
                    self.move_direction = random.choice(possible_directions)
                break

        # Update animation state
        self.moving = True
        if self.moving:
            self.current_images = self.walk_images
        else:
            self.current_images = self.idle_images