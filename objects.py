# objects.py
import pygame
from utils.constants import *

class Obstacle:
    def __init__(self, game,  x, y, width=TILE_SIZE, height=TILE_SIZE):
        self.game = game
        self.x = x # Coordenada X en tiles
        self.y = y # Coordenada Y en tiles
        self.width = width
        self.height = height        

        # Asigna la imagen cargada del objeto Game
        # ¡IMPORTANTE! Asegúrate de que `self.game.obstacle_image` existe y se cargó correctamente en main.py
        if hasattr(self.game, 'obstacle_image') and self.game.obstacle_image:
            self.image = self.game.obstacle_image
        else:
            # Fallback a un cuadrado azul si la imagen no se carga
            print("ADVERTENCIA: Imagen de obstáculo no cargada. Usando placeholder azul.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(BLUE) # El color azul que estás viendo
            
    def get_rect(self):
        """Devuelve el rectángulo de posición del obstáculo en coordenadas del mundo."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)

    def draw(self, screen, camera):
        """Dibuja el obstáculo aplicando el desplazamiento de la cámara."""
        obstacle_rect_world = self.get_rect()        
        screen.blit(self.image, camera.apply(obstacle_rect_world))