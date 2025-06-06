# enemy.py
import pygame
import random
from item import Armor, Consumable, Weapon
from utils.constants import *

class Enemy:
    def __init__(self, game, x, y, enemy_type="basic_grunt", room_rect=None):
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

        # --- IA de Estados ---
        self.state = "idle"  # "idle", "surprised", "alert", "attack"
        self.surprise_timer = 0  # Turnos restantes en estado sorprendido
        self.patrol_target = None  # Coordenadas (x,y) para patrullar en estado "alert"
        self.last_known_player_pos = None
        self.home_room_rect = room_rect # Habitación de origen para patrullar
        self.name = self.enemy_type.replace('_', ' ').title() # Para mensajes

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

        print(f"{self.name} ataca a Player. Daño base: {damage}, Daño real: {actual_damage}")

        player_defeated = target_player.take_damage(actual_damage)

        # --- Lógica de efecto de estado: Veneno --- 
        if self.enemy_type == "poisonous_crawler" and random.random() < 0.4: # 40% de probabilidad de envenenar
            target_player.apply_effect("poisoned", duration=3, potency=5) # Envenena por 3 turnos, 5 de daño por turno
            self.game.current_state.show_message("¡Has sido ENVENENADO!")

        return player_defeated
    def _get_distance_to_player(self, player):
        return abs(self.x - player.x) + abs(self.y - player.y) # Distancia Manhattan

    def _move_towards_target(self, target_pos, current_map, all_enemies, player_pos_for_collision_check):
        """Intenta moverse un paso hacia target_pos, evitando obstáculos y otros enemigos."""
        dx_total = target_pos[0] - self.x
        dy_total = target_pos[1] - self.y

        possible_steps = []
        if dx_total != 0:
            possible_steps.append((1 if dx_total > 0 else -1, 0))
        if dy_total != 0:
            possible_steps.append((0, 1 if dy_total > 0 else -1))
        
        random.shuffle(possible_steps) # Añade algo de variabilidad si ambas direcciones son válidas

        for dx, dy in possible_steps:
            new_x = self.x + dx
            new_y = self.y + dy

            if not current_map.is_walkable(new_x, new_y):
                continue

            collides_with_obstacle = any(obs.x == new_x and obs.y == new_y for obs in current_map.obstacles)
            if collides_with_obstacle:
                continue

            # Evitar colisión con el jugador a menos que el objetivo sea el jugador y estemos atacando
            if new_x == player_pos_for_collision_check[0] and new_y == player_pos_for_collision_check[1]:
                if target_pos != player_pos_for_collision_check: # Si el objetivo no es el jugador, no chocar
                    continue

            collides_with_other_enemy = any(
                other_enemy is not self and other_enemy.x == new_x and other_enemy.y == new_y
                for other_enemy in all_enemies if other_enemy.is_alive
            )
            if collides_with_other_enemy:
                continue
            
            self.x = new_x
            self.y = new_y
            # self.game.sound_move.play() # El sonido se puede gestionar en PlayingState o aquí
            return True # Movimiento exitoso
        return False # No se pudo mover

    def _behavior_idle(self, player, current_map):
        if self._get_distance_to_player(player) <= 2:
            self.state = "surprised"
            self.surprise_timer = 1 # 1 turno de sorpresa
            self.game.current_state.show_message(f"¡{self.name} te ha visto!")
            print(f"{self.name} cambió a estado: surprised")

    def _behavior_surprised(self, player, current_map):
        self.surprise_timer -= 1
        if self.surprise_timer <= 0:
            self.state = "attack"
            print(f"{self.name} cambió a estado: attack (desde surprised)")
        # El enemigo no hace nada más en este estado (vulnerable)

    def _behavior_alert(self, player, current_map, all_enemies):
        player_room = current_map.get_room_at(player.x, player.y)
        enemy_room = current_map.get_room_at(self.x, self.y)

        if player_room and enemy_room and player_room == enemy_room and self._get_distance_to_player(player) <= 5 : # Ve al jugador en la misma habitación
            self.state = "attack"
            self.patrol_target = None
            print(f"{self.name} cambió a estado: attack (desde alert, jugador en misma habitación)")
            return

        if not self.patrol_target or (self.x == self.patrol_target[0] and self.y == self.patrol_target[1]):
            target_room_to_patrol = self.home_room_rect
            if self.last_known_player_pos: # Si tiene una última posición conocida del jugador
                room_of_last_pos = current_map.get_room_at(self.last_known_player_pos[0], self.last_known_player_pos[1])
                if room_of_last_pos:
                    target_room_to_patrol = room_of_last_pos
            
            if target_room_to_patrol: # Patrulla la habitación (home o donde vio al jugador)
                self.patrol_target = (random.randint(target_room_to_patrol.left, target_room_to_patrol.right -1),
                                      random.randint(target_room_to_patrol.top, target_room_to_patrol.bottom -1))
            elif self.last_known_player_pos: # Si no hay habitación pero sí última pos, ir allí
                 self.patrol_target = self.last_known_player_pos
            else: # Movimiento aleatorio si no hay objetivo claro
                self._move_randomly(current_map, all_enemies, (player.x, player.y))
                return

        if self.patrol_target:
            self._move_towards_target(self.patrol_target, current_map, all_enemies, (player.x, player.y))

    def _behavior_attack(self, player, current_map, all_enemies):
        dist_to_player = self._get_distance_to_player(player)
        player_room = current_map.get_room_at(player.x, player.y)
        enemy_room = current_map.get_room_at(self.x, self.y)

        if dist_to_player > 5 and (player_room != enemy_room or not player_room or not enemy_room) : # Jugador lejos Y en diferente contexto de habitación
            self.state = "alert"
            self.last_known_player_pos = (player.x, player.y)
            self.patrol_target = None
            print(f"{self.name} cambió a estado: alert (jugador se alejó o cambió de habitación)")
            return

        if dist_to_player <= 1: # Adyacente
            self.attack_target(player)
        else: # Perseguir
            self._move_towards_target((player.x, player.y), current_map, all_enemies, (player.x, player.y))

    def _move_randomly(self, current_map, all_enemies, player_pos_for_collision_check):
        """Movimiento aleatorio simple, similar al 'move' original."""
        possible_moves = [(0, -1), (0, 1), (-1, 0), (1, 0)]
        random.shuffle(possible_moves)
        for dx, dy in possible_moves:
            if self._move_towards_target((self.x + dx, self.y + dy), current_map, all_enemies, player_pos_for_collision_check):
                break

    def update_ai(self, player, current_map, all_enemies):
        if not self.is_alive:
            return

        if self.state == "idle":
            self._behavior_idle(player, current_map)
        elif self.state == "surprised":
            self._behavior_surprised(player, current_map)
        elif self.state == "alert":
            self._behavior_alert(player, current_map, all_enemies)
        elif self.state == "attack":
            self._behavior_attack(player, current_map, all_enemies)

    def get_rect(self):
        """Devuelve el rectángulo de posición del enemigo en coordenadas del mundo."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)
 
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
        self.game.current_state.show_message(f"¡{self.name} Derrotado!")
        print(f"{self.name} derrotado.")

        # --- Lógica para soltar un ítem al morir --- <-- ¡NUEVO!
        if self.possible_drops and random.random() < 0.5: # 50% de probabilidad de soltar algo
            dropped_item = random.choice(self.possible_drops)
            dropped_item.x = self.x # El ítem aparece donde murió el enemigo
            dropped_item.y = self.y
            self.game.current_state.items_on_map.append(dropped_item)
            self.game.current_state.show_message(f"¡El enemigo soltó un {dropped_item.name}!")
            print(f"Enemigo soltó {dropped_item.name} en ({self.x}, {self.y}).")


