from character import Character
from pygame import Rect

class CollisionHandler:
    @staticmethod
    def precise_collision(rect, walls):
        """Verificação de colisão com margem de segurança"""
        margin = 2  # Margem de pixels para evitar colisões fantasmas
        test_rect = rect.inflate(-margin, -margin)  # Reduz o retângulo
        
        for wall in walls:
            if test_rect.colliderect(wall.get_rect()):
                return True
        return False

    @staticmethod
    def can_move(character, walls, dx, dy):
        """Verifica movimento com tratamento de cantos"""
        test_rect = Rect(character.x + dx, character.y + dy, 
                        character.width, character.height)
        
        # Verifica colisão com margem
        if not CollisionHandler.precise_collision(test_rect, walls):
            return True
            
        # Tenta movimento parcial (deslize em paredes)
        if dx != 0 and not CollisionHandler.precise_collision(
            Rect(character.x + dx, character.y, character.width, character.height), walls):
            return True
            
        if dy != 0 and not CollisionHandler.precise_collision(
            Rect(character.x, character.y + dy, character.width, character.height), walls):
            return True
            
        return False

class Player(Character):
    def __init__(self, x, y, images):
        super().__init__(x, y,
                         [images.hero_idle1, images.hero_idle2],
                         [images.hero_walk1, images.hero_walk2])
        self.treasures = 0
        self.invulnerable_timer = 0

    def update(self, keyboard, walls, treasures, enemies, audio_enabled, safe_play_sound, game_state, score, high_score, PLAYER_SPEED):
        # Guarda posição anterior
        previous_x, previous_y = self.x, self.y
        
        # Controle de movimento
        dx, dy = 0, 0
        if keyboard.left: dx = -PLAYER_SPEED
        if keyboard.right: dx = PLAYER_SPEED
        if keyboard.up: dy = -PLAYER_SPEED
        if keyboard.down: dy = PLAYER_SPEED

        # Normalização diagonal
        if dx and dy:
            dx *= 0.7071
            dy *= 0.7071

        # Verificação de colisão com paredes
        if CollisionHandler.can_move(self, walls, dx, dy):
            self.x += dx
            self.y += dy
            self.moving = dx != 0 or dy != 0
        else:
            self.x, self.y = previous_x, previous_y
            self.moving = False

        # Verificação de tesouros
        for treasure in treasures[:]:
            if self.get_rect().colliderect(treasure.get_rect()):
                treasures.remove(treasure)
                self.treasures += 1
                score += 100
                if audio_enabled:
                    safe_play_sound('pickup')

        # Verificação de inimigos
        for enemy in enemies:
            if self.get_rect().colliderect(enemy.get_rect()) and self.invulnerable_timer <= 0:
                if audio_enabled:
                    safe_play_sound('hit')
                game_state = "game_over"
                if score > high_score:
                    high_score = score

        # Atualização de animação
        if self.moving:
            self.current_images = self.walk_images
        else:
            self.current_images = self.idle_images

        # Temporizador de invulnerabilidade
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1
        
        return game_state, score, high_score