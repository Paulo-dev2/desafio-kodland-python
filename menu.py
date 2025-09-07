from pygame import Rect

class Button:
    def __init__(self, x, y, width, height, text, in_game=False):
        self.rect = Rect(x, y, width, height)
        self.text = text
        self.hovered = False
        self.in_game = in_game  # Se é um botão in-game

    def draw(self, screen):
        if self.in_game:
            # Estilo minimalista para botões in-game
            color = (0, 0, 0, 150) if self.hovered else (0, 0, 0, 100)
            screen.draw.filled_rect(self.rect, color)
            screen.draw.text(self.text, center=self.rect.center, fontsize=16, color=(255, 255, 255))
        else:
            # Estilo normal para menu
            color = (100, 100, 200) if self.hovered else (70, 70, 170)
            screen.draw.filled_rect(self.rect, color)
            screen.draw.rect(self.rect, (200, 200, 255))
            screen.draw.text(self.text, center=self.rect.center, fontsize=20, color=(255, 255, 255))

    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)

    def check_click(self, pos):
        return self.rect.collidepoint(pos)