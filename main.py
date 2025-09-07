import pgzrun
import math
import random
import pygame
from pygame import Rect, K_RETURN, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT, K_SPACE

# Import game modules
from settings import *
from player import Player, CollisionHandler
from enemies import Enemy
from wall import Wall
from treasure import Treasure
from menu import Button

# Initialize Pygame Mixer for sound
pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)

# --- Asset Loading ---
class ImageLoader:
    def __init__(self):
        # Load hero images
        self.hero_idle1 = 'hero/hero_idle1'
        self.hero_idle2 = 'hero/hero_idle2'
        self.hero_walk1 = 'hero/hero_walk1'
        self.hero_walk2 = 'hero/hero_walk2'
        # Load enemy images
        self.enemy_idle1 = 'enemy/enemy_idle1'
        self.enemy_idle2 = 'enemy/enemy_idle2'
        self.enemy_walk1 = 'enemy/enemy_walk1'
        self.enemy_walk2 = 'enemy/enemy_walk2'
        # Load environment images
        self.treasure = 'treasure'
        # Load wall images dynamically
        self.walls = [f'background/parede_{i}' for i in range(1, 3)] # Use 1-2 for internal
        self.parede_4 = 'background/parede_4'
        self.bg_forest = 'background/bg_forest'

images = ImageLoader()

# Load rotated wall image
parede_4_surface = pygame.image.load('images/background/parede_4.png').convert_alpha()
parede_4_rotated = pygame.transform.rotate(parede_4_surface, 90)

class SoundLoader:
    def __init__(self):
        try:
            self.background = pygame.mixer.Sound('music/music/background.ogg')
            self.hit = pygame.mixer.Sound('sounds/hit.ogg')
            self.pickup = pygame.mixer.Sound('sounds/pickup.ogg')
            print("Sounds loaded successfully!")
        except Exception as e:
            print(f"Error loading sounds: {e}")
            self.background = None
            self.hit = None
            self.pickup = None

sounds = SoundLoader()


# --- Game State Variables ---
game_state = "menu"
score = 0
high_score = 0
audio_enabled = True
level = 1
music_playing = False
animation_timer = 0
audio_feedback_timer = 0

# --- Game Objects ---
player = Player(GRID_SIZE * 1, GRID_SIZE * 1, images)
enemies = []
walls = []
treasures = []

# --- Menu Buttons ---
start_button = Button(WIDTH//2 - 100, HEIGHT//2 - 50, 200, 50, "Start Game")
audio_button = Button(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50, "Sound: ON")
exit_button = Button(WIDTH//2 - 100, HEIGHT//2 + 90, 200, 50, "Exit")
in_game_audio_button = Button(WIDTH - 120, 10, 110, 30, "Sound: ON", True)


# --- Sound Functions ---
def safe_play_sound(sound_name):
    if not audio_enabled:
        return
    sound = getattr(sounds, sound_name, None)
    if sound:
        try:
            sound.play()
        except Exception as e:
            print(f"Error playing sound {sound_name}: {e}")

def safe_play_music(force_stop=False):
    global music_playing
    if force_stop:
        if music_playing and sounds.background:
            sounds.background.stop()
            music_playing = False
        return

    if audio_enabled and sounds.background and not music_playing and game_state == "menu":
        try:
            sounds.background.play(-1)
            music_playing = True
        except Exception as e:
            print(f"Error playing background music: {e}")
    elif (not audio_enabled or game_state != "menu") and music_playing:
        try:
            sounds.background.stop()
            music_playing = False
        except Exception as e:
            print(f"Error stopping background music: {e}")


# --- Level Generation ---
def generate_level(level_num):
    global player, enemies, walls, treasures
    enemies.clear()
    walls.clear()
    treasures.clear()

    player.x = GRID_SIZE * 1.5
    player.y = GRID_SIZE * 1.5
    player.alive = True
    player.invulnerable_timer = 60

    # Create border walls
    for x in range(0, WIDTH, GRID_SIZE):
        walls.append(Wall(x, 0, wall_type='top_bottom'))
        walls.append(Wall(x, HEIGHT - GRID_SIZE, wall_type='top_bottom'))
    for y in range(GRID_SIZE, HEIGHT - GRID_SIZE, GRID_SIZE):
        walls.append(Wall(0, y, wall_type='side'))
        walls.append(Wall(WIDTH - GRID_SIZE, y, wall_type='side'))

    # Generate random internal walls
    num_internal_walls = 10 + level_num * 2 # Reduced number of walls
    occupied_coords = set((wall.x, wall.y) for wall in walls)

    for _ in range(num_internal_walls):
        while True:
            # Place walls on a coarser grid to increase spacing
            x = random.randint(2, (WIDTH // GRID_SIZE) - 3) * GRID_SIZE
            y = random.randint(2, (HEIGHT // GRID_SIZE) - 3) * GRID_SIZE
            
            # Check for neighbors
            has_neighbor = False
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if (x + i * GRID_SIZE, y + j * GRID_SIZE) in occupied_coords:
                        has_neighbor = True
                        break
                if has_neighbor:
                    break
            
            if not has_neighbor and not (x < GRID_SIZE * 4 and y < GRID_SIZE * 4):
                walls.append(Wall(x, y))
                occupied_coords.add((x, y))
                break

    # Add enemies
    num_enemies = 3 + level_num
    for _ in range(num_enemies):
        while True:
            x = random.randint(2, (WIDTH // GRID_SIZE) - 3) * GRID_SIZE
            y = random.randint(2, (HEIGHT // GRID_SIZE) - 3) * GRID_SIZE
            new_enemy = Enemy(x, y, images)
            if math.sqrt((player.x - x)**2 + (player.y - y)**2) < GRID_SIZE * 5:
                continue
            if any(new_enemy.get_rect().colliderect(wall.get_rect()) for wall in walls):
                continue
            if any(new_enemy.get_rect().colliderect(e.get_rect()) for e in enemies):
                continue
            enemies.append(new_enemy)
            break

    # Add treasures
    num_treasures = 5 + level_num
    for _ in range(num_treasures):
        while True:
            x = random.randint(2, (WIDTH // GRID_SIZE) - 3) * GRID_SIZE
            y = random.randint(2, (HEIGHT // GRID_SIZE) - 3) * GRID_SIZE
            new_treasure = Treasure(x, y)
            if any(new_treasure.get_rect().colliderect(wall.get_rect()) for wall in walls):
                continue
            if any(new_treasure.get_rect().colliderect(t.get_rect()) for t in treasures):
                continue
            if any(new_treasure.get_rect().colliderect(e.get_rect()) for e in enemies):
                continue
            treasures.append(new_treasure)
            break

# --- Game Loop Functions ---

def update():
    global animation_timer, game_state, high_score, score, level, audio_enabled, audio_feedback_timer

    animation_timer += 1
    safe_play_music()

    if audio_feedback_timer > 0:
        audio_feedback_timer -= 1

    if game_state == "menu":
        mouse_pos = pygame.mouse.get_pos()
        start_button.check_hover(mouse_pos)
        audio_button.check_hover(mouse_pos)
        exit_button.check_hover(mouse_pos)

    elif game_state == "playing":
        mouse_pos = pygame.mouse.get_pos()
        in_game_audio_button.check_hover(mouse_pos)

        # Update player
        new_game_state, new_score, new_high_score = player.update(keyboard, walls, treasures, enemies, audio_enabled, safe_play_sound, game_state, score, high_score, PLAYER_SPEED)
        game_state = new_game_state
        score = new_score
        high_score = new_high_score
        player.update_animation(animation_timer, animation_speed)


        # Update enemies
        for enemy in enemies:
            enemy.update(walls, WIDTH, HEIGHT, ENEMY_SPEED)
            enemy.update_animation(animation_timer, animation_speed)
            if enemy.is_colliding(player) and player.invulnerable_timer <= 0:
                safe_play_sound('hit')
                game_state = "game_over"
                if score > high_score:
                    high_score = score

        # Check for level clear
        if not treasures:
            level += 1
            generate_level(level)

def draw():
    screen.clear()

    if game_state == "menu":
        screen.fill((20, 20, 40))
        screen.draw.text("DUNGEON EXPLORER", centerx=WIDTH//2, centery=HEIGHT//4, fontsize=50, color="white")
        screen.draw.text("Arrow Keys to move, Collect treasures, Avoid enemies", centerx=WIDTH//2, centery=HEIGHT//3, fontsize=20, color=(200, 200, 200))
        start_button.draw(screen)
        audio_button.draw(screen)
        exit_button.draw(screen)
        if high_score > 0:
            screen.draw.text(f"High Score: {high_score}", centerx=WIDTH//2, centery=HEIGHT*4//5, fontsize=20, color=(255, 255, 100))

    elif game_state in ["playing", "game_over"]:
        # Draw floor
        screen.blit(images.bg_forest, (0, 0))

        # Draw walls
        for wall in walls:
            wall.draw(screen, images, parede_4_rotated)

        for treasure in treasures:
            treasure.draw(screen, images)

        for enemy in enemies:
            enemy.draw(screen)

        if player.invulnerable_timer <= 0 or animation_timer % 4 < 2:
            player.draw(screen)

        screen.draw.text(f"Score: {score}", (10, 10), fontsize=20, color="white")
        screen.draw.text(f"Level: {level}", (10, 40), fontsize=20, color="white")

        in_game_audio_button.text = "Sound: ON" if audio_enabled else "Sound: OFF"
        in_game_audio_button.draw(screen)
        if audio_feedback_timer > 0:
            screen.draw.text("✓", (in_game_audio_button.rect.right + 5, in_game_audio_button.rect.y + 5), fontsize=20, color=(0, 255, 0))

        if game_state == "game_over":
            screen.draw.filled_rect(Rect(WIDTH//4, HEIGHT//3, WIDTH//2, HEIGHT//3), (0, 0, 0, 180))
            screen.draw.text("GAME OVER", centerx=WIDTH//2, centery=HEIGHT//2 - 40, fontsize=40, color=(255, 50, 50))
            screen.draw.text(f"Final Score: {score}", centerx=WIDTH//2, centery=HEIGHT//2, fontsize=30, color="white")
            screen.draw.text("Press ENTER to play again", centerx=WIDTH//2, centery=HEIGHT//2 + 40, fontsize=20, color=(200, 200, 200))

# --- Input Handlers ---

def on_mouse_down(pos, button):
    global game_state, audio_enabled, audio_feedback_timer

    if game_state == "menu":
        if start_button.check_click(pos):
            start_game()
        elif audio_button.check_click(pos):
            audio_enabled = not audio_enabled
            audio_button.text = "Sound: ON" if audio_enabled else "Sound: OFF"
        elif exit_button.check_click(pos):
            exit()

    elif game_state == "playing":
        if in_game_audio_button.check_click(pos):
            audio_enabled = not audio_enabled
            audio_feedback_timer = 30

def on_key_down(key):
    global game_state, score, level

    if game_state == "menu" and key == K_RETURN:
        start_game()
    elif game_state == "game_over" and key == K_RETURN:
        score = 0
        level = 1
        game_state = "playing"
        generate_level(level)

def start_game():
    global game_state, score, level
    game_state = "playing"
    score = 0
    level = 1
    generate_level(level)
    safe_play_music(force_stop=True) # Stop menu music

# --- Initialization ---
generate_level(level)
safe_play_music()
pgzrun.go()