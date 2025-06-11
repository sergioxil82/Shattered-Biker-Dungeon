# game_states/menu_state.py
import pygame
from .base_state import GameState
from utils.constants import * # Ajusta según tu estructura

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Menú Principal")

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Al pulsar cualquier tecla, cambiamos al estado de juego
            # La solicitud de cambio de estado se hace a través del objeto game
            self.game.request_state_change("playing") 

    def update(self, dt):
        pass

    def draw(self, screen):
        screen.fill(DARK_GRAY)

        screen_rect = screen.get_rect()
        image_rect = self.game.welcome_image.get_rect(center=screen_rect.center)
        screen.blit(self.game.welcome_image, image_rect)       

        font_small = pygame.font.Font(None, FONT_DEFAULT_SIZE_SMALL)
        start_text_surface = font_small.render("Pulsa cualquier tecla para empezar", True, GREEN)
        start_text_rect = start_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(start_text_surface, start_text_rect)