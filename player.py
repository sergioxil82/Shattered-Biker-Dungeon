# player.py
import pygame
from utils.constants import *

class Player:
    def __init__(self, game, start_x, start_y):
        self.game = game
        self.x = start_x # Posición en coordenadas de tile
        self.y = start_y # Posición en coordenadas de tile
        self.color = ORANGE # Color para el placeholder del jugador (ya no usado si tienes imagen)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = PLAYER_SPEED # Velocidad de movimiento (en tiles por ahora)

         # --- Estadísticas de combate ---
        self.max_hp = 100
        self.current_hp = self.max_hp
        self.attack = 15 # Daño base que inflige
        self.defense = 5 # Reducción de daño
    
    def take_damage(self, damage):
        """Calcula el daño recibido y actualiza HP."""
        # Daño = Ataque_enemigo - Defensa_jugador (mínimo 1 de daño)
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        self.game.sound_hit.play() # Sonido de recibir daño
        print(f"¡Jugador recibió {actual_damage} de daño! HP restantes: {self.current_hp}/{self.max_hp}")
        if self.current_hp <= 0:
            print("¡Has sido derrotado!")
            self.game.sound_player_death.play() # Sonido de muerte del jugador
            return True # Jugador derrotado
        return False # Jugador no derrotado

    def attack_target(self, target): # Añade un método de ataque
        """Ataca a un objetivo (enemigo)."""
        print(f"Jugador atacó a {target.__class__.__name__} en ({target.x}, {target.y})")
        self.game.sound_attack.play() # Sonido de ataque del jugador
        target_defeated = target.take_damage(self.attack)
        if target_defeated:
            self.game.sound_enemy_death.play() # Sonido de muerte de enemigo
        return target_defeated
    
    def move(self, dx, dy, current_map):
        """Intenta mover al jugador en dx, dy."""
        new_x = self.x + dx
        new_y = self.y + dy

        # 1. Primero, verifica si el nuevo tile es caminable (paredes, abismos)
        if not current_map.is_walkable(new_x, new_y):
            return False # No es un tile caminable, no se mueve

        # 2. Luego, verifica si la nueva posición está ocupada por un obstáculo
        # Itera sobre los obstáculos del mapa
        for obstacle in current_map.obstacles:
            if obstacle.x == new_x and obstacle.y == new_y:
                print("¡Colisión con un obstáculo!")
                return False # Hay un obstáculo, no se mueve

        # Si el código llega aquí, la nueva posición es caminable y no hay obstáculos
        # Guardar el tipo de tile actual del jugador antes de moverse
        previous_tile_type = current_map.tiles[self.x][self.y]

        # Actualiza la posición del jugador
        self.x = new_x
        self.y = new_y
        # Primero, verificamos si el nuevo tile es caminable
        if current_map.is_walkable(new_x, new_y):
            # Si el jugador se mueve desde la posición de entrada, cambia el tile a carretera
            if previous_tile_type  == TILE_ENTRANCE:
                current_map.tiles[self.x - dx][self.y - dy] = TILE_ENTRANCE
            # Si el jugador se mueve desde la posición de salida, cambia el tile a salida
            elif previous_tile_type  == TILE_EXIT:
                current_map.tiles[self.x - dx][self.y - dy] = TILE_EXIT # La salida sigue siendo salida

            self.game.sound_move.play() # Sonido de movimiento del jugador

            # Actualiza la posición del jugador
            self.x = new_x
            self.y = new_y

            # Si el jugador llega a la salida, haz algo (por ejemplo, print)
            if current_map.tiles[self.x][self.y] == TILE_EXIT:
                print("¡Has llegado a la salida!")
                self.game.current_state.show_message("¡Has llegado a la salida!")
                self.game.request_state_change("victory")            
            
            return True

    def get_rect(self):
        """Devuelve el rectángulo de posición del jugador en coordenadas del mundo."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)


    def draw(self, screen, camera):
        # Dibuja el jugador, aplicando el desplazamiento de la cámara
        screen.blit(self.game.player_image, camera.apply(self.get_rect()))