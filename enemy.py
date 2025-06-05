# enemy.py
import pygame
import random
from item import Armor, Consumable, Weapon
from utils.constants import *

class Enemy:
    def __init__(self, game, x, y, enemy_type="basic_grunt"):
        self.game = game # Referencia al objeto Game principal
        self.x = x       # Posición en coordenadas de tile
        self.y = y       # Posición en coordenadas de tile
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = ENEMY_SPEED 

        # --- Estadísticas de combate ---
        self.max_hp = 30
        self.current_hp = self.max_hp
        self.attack = 10 # Daño base que inflige
        self.defense = 2 # Reducción de daño

        self.is_alive = True # Nuevo atributo para saber si está vivo
        self.enemy_type = enemy_type

        self.load_stats_and_image_by_type()

    def take_damage(self, damage):
        """Calcula el daño recibido y actualiza HP."""
        if not self.is_alive: # No se puede dañar a un enemigo muerto
            return False

        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        print(f"Enemigo en ({self.x}, {self.y}) recibió {actual_damage} de daño. HP restantes: {self.current_hp}/{self.max_hp}")

        if self.current_hp <= 0:
            self.current_hp = 0 # Asegurarse de que no baje de 0
            self.is_alive = False
            print(f"Enemigo en ({self.x}, {self.y}) ha sido derrotado.")
            return True # Enemigo derrotado
        return False # Enemigo no derrotado

    def attack_target(self, target_player):
        """Ataca al jugador."""
        damage = self.attack # Daño base del enemigo
        actual_damage = max(0, damage - target_player.defense) # Daño real tras defensa

        print(f"{self.enemy_type.replace('_', ' ').title()} ataca a Player. Daño base: {damage}, Daño real: {actual_damage}")

        player_defeated = target_player.take_damage(actual_damage)

        # --- Lógica de efecto de estado: Veneno --- 
        if self.enemy_type == "poisonous_crawler" and random.random() < 0.4: # 40% de probabilidad de envenenar
            target_player.apply_effect("poisoned", duration=3, potency=5) # Envenena por 3 turnos, 5 de daño por turno
            self.game.current_state.show_message("¡Has sido ENVENENADO!")

        return player_defeated
    
    def get_rect(self):
        """Devuelve el rectángulo de posición del enemigo en coordenadas del mundo."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)

 
    def move(self, current_map, player_pos, all_enemies): 
        """
        Implementa un movimiento básico para el enemigo.
        Ahora, evita colisionar con obstáculos, el jugador y otros enemigos.
        """
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)] # Arriba, Abajo, Izquierda, Derecha
        # El enemigo no se movera hasta que no este cerca el jugador
        if abs(self.x - player_pos[0]) > 5 or abs(self.y - player_pos[1]) > 5:
            return

        for dx, dy in possible_moves:
            new_x = self.x + dx
            new_y = self.y + dy

            # 1. Verificar si la nueva posición es caminable (tiles de pared/abismo)
            if not current_map.is_walkable(new_x, new_y):
                continue # Pasa al siguiente movimiento posible

            # 2. Verificar colisión con obstáculos
            collides_with_obstacle = False
            for obstacle in current_map.obstacles:
                if obstacle.x == new_x and obstacle.y == new_y:
                    collides_with_obstacle = True
                    break
            if collides_with_obstacle:
                continue # Pasa al siguiente movimiento posible

            # 3. Verificar colisión con el jugador
            if new_x == player_pos[0] and new_y == player_pos[1]:
                # ¡Colisión con el jugador! Aquí, en el futuro, se iniciaría el combate.
                # Por ahora, el enemigo simplemente NO se mueve a la casilla del jugador.
                print(f"Enemigo en ({self.x}, {self.y}) intentó moverse a la posición del jugador ({new_x}, {new_y})")
                # Lógica de combate básica: El enemigo ataca al jugador
                # self.attack(player) # <-- Esto se implementaría más adelante
                continue # Pasa al siguiente movimiento posible si no puede atacar y quedarse

            # 4. Verificar colisión con otros enemigos
            collides_with_other_enemy = False
            for other_enemy in all_enemies:
                # Asegúrate de no compararse consigo mismo
                if other_enemy is self:
                    continue
                if other_enemy.x == new_x and other_enemy.y == new_y:
                    collides_with_other_enemy = True
                    break
            if collides_with_other_enemy:
                continue # Pasa al siguiente movimiento posible

            # Si el código llega aquí, la nueva posición es válida y libre
            self.x = new_x
            self.y = new_y
            self.game.sound_move.play() # Sonido de movimiento de enemigo
            break # El enemigo se ha movido con éxito, sal del bucle de movimientos
                
               
    # def update(self, current_map):
    #    """Actualiza la lógica del enemigo (movimiento, etc.)."""
    #    self.move(current_map) # Llamamos a la lógica de movimiento

    def draw(self, screen, camera):
        """Dibuja el enemigo, aplicando el desplazamiento de la cámara."""
        enemy_rect_world = self.get_rect()
        enemy_rect_screen = camera.apply(enemy_rect_world)

        # Dibuja la imagen del enemigo si está cargada
        if hasattr(self.game, 'enemy_image') and self.image:
            screen.blit(self.image, enemy_rect_screen)
        else: # Si no hay imagen, dibuja un placeholder de color (útil para depuración)
            pygame.draw.rect(screen, RED, enemy_rect_screen) # Define RED en constants.py
        
        # Dibujar la barra de vida del enemigo
        if self.current_hp > 0:
            health_ratio = self.current_hp / self.max_hp
            health_bar_width = int(self.width * health_ratio)
            health_bar_rect = pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE - 5, health_bar_width, 5)
            health_bar_rect = camera.apply(health_bar_rect)
            pygame.draw.rect(screen, GREEN, health_bar_rect)
            

    def load_stats_and_image_by_type(self):        
        
        if self.enemy_type == "basic_grunt":
            self.max_hp = 30
            self.current_hp = 30
            self.attack = 8
            self.defense = 3
            # Asume que esta imagen ya está cargada en main.py como self.game.enemy_image
            self.image = self.game.enemy_image # Imagen base del enemigo

        elif self.enemy_type == "heavy_hitter":
            self.max_hp = 60
            self.current_hp = 60
            self.attack = 15
            self.defense = 5
            # Necesitarías cargar una imagen específica para este tipo de enemigo en main.py
            # o tener una imagen más genérica y escalarla/tintarla
            self.image = self.game.heavy_hitter_image # <-- Necesitarías cargar esta en main.py
           
            if not hasattr(self.game, 'heavy_hitter_image'):               
                self.image = self.game.enemy_image # Fallback si no está cargada
      
        # Añade más tipos de enemigos aquí
        # elif self.enemy_type == "fast_scout":
        #     self.max_hp = 20
        #     self.current_hp = 20
        #     self.attack = 5
        #     self.defense = 2
        #     self.image = self.game.fast_scout_image

        # Definir qué ítems suelta este tipo de enemigo
        self.possible_drops = []
        if self.enemy_type == "basic_grunt":
            self.possible_drops.append(Consumable(self.game, "Café Turbo", "Te da un subidón de energía.", {"heal": 10}, "assets/items/coffee.png"))
        elif self.enemy_type == "heavy_hitter":
            self.possible_drops.append(Weapon(self.game, "Bate con Clavos", "¡Duele mucho!", 10, "assets/items/spiked_bat.png"))
            self.possible_drops.append(Armor(self.game, "Chaleco de Placas", "Armadura pesada.", 7, "assets/items/plate_vest.png"))

    def die(self):
        self.is_alive = False
        self.game.sound_enemy_death.play()
        self.game.current_state.show_message(f"¡{self.enemy_type.replace('_', ' ').title()} Derrotado!")
        print(f"{self.enemy_type.replace('_', ' ').title()} derrotado.")

        # --- Lógica para soltar un ítem al morir --- <-- ¡NUEVO!
        if self.possible_drops and random.random() < 0.5: # 50% de probabilidad de soltar algo
            dropped_item = random.choice(self.possible_drops)
            dropped_item.x = self.x # El ítem aparece donde murió el enemigo
            dropped_item.y = self.y
            self.game.current_state.items_on_map.append(dropped_item)
            self.game.current_state.show_message(f"¡El enemigo soltó un {dropped_item.name}!")
            print(f"Enemigo soltó {dropped_item.name} en ({self.x}, {self.y}).")


