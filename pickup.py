# pickup.py
import pygame
from utils.constants import *

class Pickup:
    def __init__(self, game, x, y, type):
        self.game = game
        self.x = x
        self.y = y
        self.type = type # Ej. "health_potion", "attack_boost"
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.is_collected = False

        # Cargar imagen según el tipo (tendrás que cargar estas en main.py)
        if self.type == "health_potion":
            self.image = self.game.pickup_health_image # Asegúrate de cargar esta imagen en Game.load_assets
        # elif self.type == "attack_boost":
        #     self.image = self.game.pickup_attack_image
        else:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE)) # Placeholder
            self.image.fill(BLUE) # Un color si no hay imagen

    def get_rect(self):
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)

    def draw(self, screen, camera):
        if not self.is_collected:
            pickup_rect_world = self.get_rect()
            screen.blit(self.image, camera.apply(pickup_rect_world))

    def collect(self, player):
        """Aplica el efecto del pickup al jugador."""
        if self.is_collected:
            return

        if self.type == "health_potion":
            heal_amount = 25 # Cantidad de vida a restaurar
            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
            self.game.current_state.show_message(f"¡Curado +{heal_amount} HP!")
            print(f"Jugador curado. HP: {player.current_hp}/{player.max_hp}")
            self.game.sound_pickup.play() # Sonido de recogida (necesitas cargarlo)

        # Otros tipos de pickup aquí
        # elif self.type == "attack_boost":
        #     player.attack += 5
        #     self.game.current_state.show_message("¡Ataque Aumentado!")

        self.is_collected = True