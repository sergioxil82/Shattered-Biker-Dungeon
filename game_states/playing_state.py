# game_states/playing_state.py
import pygame
import random
from .base_state import GameState
from objects import Obstacle 
from utils.constants import *
from dungeon_generator import Map
from player import Player
from camera import Camera
from enemy import Enemy
from pickup import Pickup
from hub import HUD # Asegúrate que el archivo se llame hud.py
from motorcycle import Motorcycle

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Jugando")
        self.current_level_number = self.game.target_level_number # Usar el nivel objetivo del juego
        self.max_levels = 3  

        self.current_map = Map(self.game, MAP_WIDTH, MAP_HEIGHT)
        
        self.enemies = [] 
        self.pickups = []
        self.items_on_map = []       
       
        if not hasattr(self.game, 'persistent_player'):
            self.game.persistent_player = Player(self.game, 0, 0)
            self.game.persistent_motorcycle = Motorcycle(self.game)
        
        self.player = self.game.persistent_player
        self.motorcycle = self.game.persistent_motorcycle

        self.message = ""
        self.message_timer = 0
        self.message_duration = 2000

        self.hud = HUD(self.game, self.player, self.motorcycle)
        
       
        # Crear la cámara ANTES de inicializar el nivel,
        # ya que _initialize_level() llama a self.camera.update()
        self.camera = Camera(self.player, self.current_map.width, self.current_map.height)

        # Ahora inicializar el nivel
        self._initialize_level()
        
        # Colocar obstáculos y pickups después de que el nivel y el jugador estén listos
        self.place_obstacles() 
        self.place_pickups() 
        
        # La cámara ya se actualizó en _initialize_level después de posicionar al jugador
        self.camera.update()
             
        self.awaiting_powerful_attack_target = False

    def _initialize_level(self):
        self.show_message(f"Nivel {self.current_level_number}")
                
        self.enemies = []
        self.pickups = []
        self.items_on_map = []
        
        self.current_map.generate_dungeon(self)
        self.player.x = self.current_map.player_start_pos[0]
        self.player.y = self.current_map.player_start_pos[1]

        # Actualizar la cámara para que se centre en la nueva posición del jugador
        self.camera.update() 
        
        # Es importante que place_obstacles y place_pickups se llamen DESPUÉS
        # de que el mapa y sus contenidos (enemigos/items de habitaciones) se hayan generado
        # para evitar solapamientos o limpiar contenido recién creado.
        # Si estas funciones deben ejecutarse por nivel, este es un buen lugar.
        # self.place_obstacles() # Movido a __init__ para que se ejecute una vez por estado PlayingState
        # self.place_pickups()   # o aquí si es específico del nivel y necesita el mapa generado.

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_i:
                self.player.inventory.toggle_open()
                return

            if self.player.inventory.is_open:
                action_consumed_turn = self.player.inventory.handle_input(event)
                if action_consumed_turn:
                    self.process_enemy_turn()
                return
           
            if event.key == pygame.K_s:
                if self.player.cooldown_powerful_attack > 0:
                    self.show_message("Ataque Potente en cooldown!")
                else:
                    self.show_message("Selecciona un enemigo para ATAQUE POTENTE.")
                    self.awaiting_powerful_attack_target = True
                    return
                            
            dx, dy = 0, 0
            if event.key == pygame.K_UP: dy = -1
            elif event.key == pygame.K_DOWN: dy = 1
            elif event.key == pygame.K_LEFT: dx = -1
            elif event.key == pygame.K_RIGHT: dx = 1

            if dx != 0 or dy != 0:
                if self.motorcycle and self.motorcycle.fuel_current <= 0:
                    self.show_message("¡SIN COMBUSTIBLE! Te has quedado tirado.")
                    self.game.request_state_change("game_over")
                    return
                
                target_x = self.player.x + dx
                target_y = self.player.y + dy

                target_enemy = None
                for enemy in self.enemies:
                    if enemy.x == target_x and enemy.y == target_y and enemy.is_alive:
                        target_enemy = enemy
                        break

                player_action_taken = False

                if target_enemy:
                    player_action_taken = True
                    if self.awaiting_powerful_attack_target:
                        enemy_defeated = self.player.attack_target(target_enemy, is_powerful_attack=True)
                        self.awaiting_powerful_attack_target = False
                    else:
                        enemy_defeated = self.player.attack_target(target_enemy)
                    
                    if enemy_defeated:
                        self.enemies = [e for e in self.enemies if e.is_alive]
                        print(f"Enemigo derrotado. Quedan {len(self.enemies)} enemigos.")
                        
                else:
                    collides_with_obstacle = any(obs.x == target_x and obs.y == target_y for obs in self.current_map.obstacles)
                    
                    if collides_with_obstacle:
                        player_action_taken = True
                        print("Colisión con obstáculo, el jugador no se mueve.")
                    elif not self.current_map.is_walkable(target_x, target_y):
                        player_action_taken = True
                        print("Tile no caminable, el jugador no se mueve.")
                    else:
                        if self.awaiting_powerful_attack_target:
                            self.awaiting_powerful_attack_target = False
                            self.show_message("Ataque Potente cancelado.")

                        player_moved = self.player.move(dx, dy, self.current_map)
                        if player_moved:
                            player_action_taken = True

                            if self.motorcycle:
                                self.motorcycle.consume_fuel(0.5)
                                if self.motorcycle.fuel_current <= 0:
                                    self.show_message("¡TE HAS QUEDADO SIN COMBUSTIBLE!")
                                    self.game.request_state_change("game_over")

                            for pickup in self.pickups:
                                if not pickup.is_collected and \
                                   self.player.x == pickup.x and self.player.y == pickup.y:
                                    pickup.collect(self.player)
                                    break
                            
                            items_to_remove = []
                            for item_on_map in self.items_on_map:
                                if self.player.x == item_on_map.x and self.player.y == item_on_map.y:
                                    if self.player.inventory.add_item(item_on_map):
                                        items_to_remove.append(item_on_map)
                                        self.game.sound_pickup.play()
                                    break

                            for item_to_remove in items_to_remove:
                                self.items_on_map.remove(item_to_remove)

                if player_action_taken:
                    self.process_enemy_turn()
                    self.player.end_turn_update() 
                   
            if event.key == pygame.K_p:
                pass

    def process_enemy_turn(self):
        enemies_to_process = list(self.enemies)
        for enemy in enemies_to_process:
            if enemy.is_alive:
               enemy.update_ai(self.player, self.current_map, self.enemies)

        self.camera.update()

        if self.player.x == self.current_map.exit_pos[0] and self.player.y == self.current_map.exit_pos[1]:
            print("¡Has llegado a la salida! -->", self.current_level_number, ">=", self.max_levels)
            if self.current_level_number >= self.max_levels:
                self.show_message("¡Has completado todas las misiones! ¡VICTORIA!")
                self.game.request_state_change("victory")
            else:
                # En lugar de inicializar directamente el nivel, vamos a la pantalla de transición
                # PlayingState incrementará current_level_number cuando se re-inicialice desde TransitionState
                self.game.request_state_change("transition")
            return
        
    def update(self, dt):
        if self.message_timer > 0:
            self.message_timer -= (dt * 1000)
            if self.message_timer <= 0:
                self.message = ""

    def draw(self, screen):
        screen.fill(BLACK)
        self.current_map.draw(screen, self.camera)
        self.player.draw(screen, self.camera)

        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.draw(screen, self.camera)

        for obstacle in self.current_map.obstacles:
            obstacle.draw(screen, self.camera)

        for pickup in self.pickups:
            pickup.draw(screen, self.camera)

        for item_on_map in self.items_on_map:
            item_on_map_rect_world = pygame.Rect(item_on_map.x * TILE_SIZE, item_on_map.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            screen.blit(item_on_map.image, self.camera.apply(item_on_map_rect_world))

        self.hud.draw(screen)      

        if self.message:
            message_font = pygame.font.Font(None, 36)
            message_surface = message_font.render(self.message, True, YELLOW)
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(message_surface, message_rect)
                
        self.player.inventory.draw(screen)
        
    def show_message(self, text):
        self.message = text
        self.message_timer = self.message_duration

    def place_obstacles(self):
        self.current_map.obstacles = []
        valid_obstacle_tiles = []
        
        for room_rect in self.current_map.room_rects:
            for x_coord in range(room_rect.left, room_rect.right):
                for y_coord in range(room_rect.top, room_rect.bottom):
                    if self.current_map.is_walkable(x_coord, y_coord) and \
                       (x_coord, y_coord) != self.current_map.player_start_pos and \
                       (x_coord, y_coord) != self.current_map.exit_pos: 
                        valid_obstacle_tiles.append((x_coord, y_coord))

        random.shuffle(valid_obstacle_tiles)
        num_obstacles_to_add = random.randint(3, 7)
        
        placed_count = 0
        for ox, oy in valid_obstacle_tiles:
            if placed_count >= num_obstacles_to_add:
                break
            
            is_occupied = any(enemy.x == ox and enemy.y == oy for enemy in self.enemies) or \
                          any(item.x == ox and item.y == oy for item in self.items_on_map) or \
                          any(pickup.x == ox and pickup.y == oy for pickup in self.pickups)

            if not is_occupied:
                self.current_map.obstacles.append(Obstacle(self.game, ox, oy))
                placed_count +=1
        
        print(f"Colocados {len(self.current_map.obstacles)} obstáculos.")

    def place_pickups(self):
        self.pickups = []
        valid_spawn_tiles = []

        for x_coord in range(self.current_map.width):
            for y_coord in range(self.current_map.height):
                # Permitir pickups en TILE_ROAD o TILE_GARAGE_FLOOR
                tile_type = self.current_map.get_tile_at(x_coord, y_coord)
                if (tile_type == TILE_ROAD or tile_type == TILE_GARAGE_FLOOR) and \
                   (x_coord, y_coord) != self.current_map.player_start_pos and \
                   (x_coord, y_coord) != self.current_map.exit_pos:
                    
                    is_occupied = any(obs.x == x_coord and obs.y == y_coord for obs in self.current_map.obstacles) or \
                                  any(enemy.x == x_coord and enemy.y == y_coord for enemy in self.enemies) or \
                                  any(item.x == x_coord and item.y == y_coord for item in self.items_on_map)

                    if not is_occupied:
                        valid_spawn_tiles.append((x_coord, y_coord))

        random.shuffle(valid_spawn_tiles)
        num_pickups_to_add = 2 

        placed_count = 0
        for px, py in valid_spawn_tiles:
            if placed_count >= num_pickups_to_add:
                break
            self.pickups.append(Pickup(self.game, px, py, "health_potion"))
            placed_count += 1

        print(f"Colocados {len(self.pickups)} pickups.")