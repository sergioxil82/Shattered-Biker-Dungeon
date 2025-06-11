# game_states/game_over_state.py
import pygame
from .base_state import GameState
from utils.constants import * # Cambio a importación absoluta

class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Game Over")
        self.font = pygame.font.Font(None, 48) # Debería ser FONT_DEFAULT_SIZE_MEDIUM o similar
        self.small_font = pygame.font.Font(None, 24) # FONT_DEFAULT_SIZE_SMALL

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                if hasattr(self.game, 'persistent_player'):
                    del self.game.persistent_player
                if hasattr(self.game, 'persistent_motorcycle'):
                    del self.game.persistent_motorcycle
                self.game.target_level_number = 1 # Resetear al nivel 1 al reiniciar
                self.game.request_state_change("playing")
            elif event.key == pygame.K_ESCAPE:
                self.game.running = False

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(DARK_RED) # Un color más temático para game over

        screen_rect = screen.get_rect()
        image_rect = self.game.game_over_image.get_rect(center=screen_rect.center)
        screen.blit(self.game.game_over_image, image_rect)
        
        restart_text = self.small_font.render("Pulsa 'R' para Reiniciar o 'ESC' para Salir", True, WHITE)
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50)) # Ajustar posición
        screen.blit(restart_text, restart_rect)
        # pygame.display.flip() # No es necesario aquí, se hace en Game.draw()