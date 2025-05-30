import pygame
from utils.constants import *

class Camera:
    def __init__(self, target, map_width_tiles, map_height_tiles):
        self.target = target # El objeto que la cámara debe seguir (ej. el jugador)
        self.map_width_tiles = map_width_tiles
        self.map_height_tiles = map_height_tiles

        # Dimensiones de la cámara en píxeles (igual que la pantalla)
        self.camera_width = SCREEN_WIDTH
        self.camera_height = SCREEN_HEIGHT

        # offset_x, offset_y: Representa el desplazamiento que se aplica a las coordenadas del mundo
        # para obtener las coordenadas de la pantalla. Son negativos.
        self.offset_x = 0
        self.offset_y = 0

    def apply(self, entity_rect):
        """
        Aplica el desplazamiento de la cámara a un rectángulo de entidad.
        Esto convierte las coordenadas del mundo a coordenadas de pantalla.
        """
        # Movemos el rectángulo de la entidad por el offset de la cámara.
        # Un offset negativo de la cámara mueve el mapa "hacia la izquierda/arriba" en la pantalla.
        return entity_rect.move(self.offset_x, self.offset_y)

    def update(self):
        # Calcular la posición central del objetivo en píxeles del mundo
        target_center_x_world = self.target.x * TILE_SIZE + TILE_SIZE // 2
        target_center_y_world = self.target.y * TILE_SIZE + TILE_SIZE // 2

        # Calcular el offset deseado para que el objetivo esté en el centro de la pantalla
        # (Esto es lo que el offset_x/y DEBERÍA ser, antes de aplicar límites)
        desired_offset_x = -target_center_x_world + SCREEN_WIDTH // 2
        desired_offset_y = -target_center_y_world + SCREEN_HEIGHT // 2

        # --- Limitar el offset de la cámara para que no se salga de los bordes del mapa ---
        map_width_pixels = self.map_width_tiles * TILE_SIZE
        map_height_pixels = self.map_height_tiles * TILE_SIZE

        # Límite horizontal (X):
        if map_width_pixels < self.camera_width: # Si el mapa es más pequeño que la pantalla en ancho
            # Centrar el mapa en X: el offset se calcula para que el mapa quede centrado.
            self.offset_x = (SCREEN_WIDTH - map_width_pixels) // 2
        else: # El mapa es más grande que la pantalla en ancho
            # El offset_x máximo (más a la derecha) es 0 (cuando el borde izquierdo del mapa coincide con el borde izquierdo de la pantalla).
            # El offset_x mínimo (más a la izquierda) es -(map_width_pixels - camera_width)
            self.offset_x = max(-(map_width_pixels - self.camera_width), desired_offset_x)
            self.offset_x = min(0, self.offset_x)


        # Límite vertical (Y):
        if map_height_pixels < self.camera_height: # Si el mapa es más pequeño que la pantalla en alto
            # Centrar el mapa en Y
            self.offset_y = (SCREEN_HEIGHT - map_height_pixels) // 2
        else: # El mapa es más grande que la pantalla en alto
            # El offset_y máximo (más abajo) es 0.
            # El offset_y mínimo (más arriba) es -(map_height_pixels - camera_height)
            self.offset_y = max(-(map_height_pixels - self.camera_height), desired_offset_y)
            self.offset_y = min(0, self.offset_y)

        # DEBUG: Puedes añadir prints aquí para ver los valores
        # print(f"Camera offset: ({self.offset_x}, {self.offset_y})")