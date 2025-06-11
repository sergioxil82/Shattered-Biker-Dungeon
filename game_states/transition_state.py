# game_states/transition_state.py
import pygame
import random
from .base_state import GameState
from utils.constants import *

class TransitionState(GameState):
    def __init__(self, game, next_level_number):
        super().__init__(game)
        self.next_level_number = next_level_number
        print(f"Entrando en el estado: Transición al Nivel {self.next_level_number}")

        self.messages = ["¡Gaaas!", "¡Curveando!", "¡Dándole al puño!", "¡A por el siguiente tramo!", "¡Quemando rueda!"]
        self.display_message = random.choice(self.messages)

        self.font_large = pygame.font.Font(None, FONT_DEFAULT_SIZE_LARGE) # O la fuente que prefieras
        self.font_small = pygame.font.Font(None, FONT_DEFAULT_SIZE_SMALL)

        # Cargar imagen de transición (asegúrate de tenerla en assets)
        try:
            self.transition_image = self.game.transition_screen_image # Cargada en Game.load_assets()
        except AttributeError:
            print("Advertencia: Imagen de transición no cargada. Usando fondo de color.")
            self.transition_image = None

        self.timer = 3000 # Milisegundos (3 segundos)

    def update(self, dt):
        self.timer -= (dt * 1000)
        if self.timer <= 0:
            # Importante: PlayingState se encargará de usar self.game.persistent_player.current_level_number
            # o pasaremos el next_level_number de alguna forma si es necesario.
            # Por ahora, PlayingState ya incrementa su propio current_level_number.
            self.game.request_state_change("playing")

    def draw(self, screen):
        if self.transition_image:
            screen.blit(self.transition_image, (0,0))
        else:
            screen.fill(DARK_GRAY)

        message_surf = self.font_large.render(self.display_message, True, YELLOW)
        message_rect = message_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(message_surf, message_rect)

        # Podrías añadir un "Cargando Nivel X..." si quieres
        level_text_surf = self.font_small.render(f"Preparando Nivel {self.next_level_number}...", True, WHITE)
        level_text_rect = level_text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        screen.blit(level_text_surf, level_text_rect)