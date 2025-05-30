# game_state.py
import pygame
from objects import Obstacle
from utils.constants import * # Importa todas las constantes
from dungeon_generator import Map # Importa la clase Map
from player import Player # Importa la clase Player
from camera import Camera
from enemy import Enemy
import random
from pickup import Pickup

# --- Clase Base para los Estados del Juego ---
class GameState:
    def __init__(self, game):
        self.game = game # Referencia a la instancia principal del juego

    def handle_input(self, event):
        """Maneja los eventos de entrada para este estado."""
        pass

    def update(self, dt):
        """Actualiza la lógica del juego para este estado.
        dt es el tiempo transcurrido desde el último frame (delta time), útil para movimientos suaves.
        """
        pass

    def draw(self, screen):
        """Dibuja los elementos en la pantalla para este estado."""
        pass

    def enter_state(self):
        """Método llamado cuando se entra en este estado."""
        pass

    def exit_state(self):
        """Método llamado cuando se sale de este estado."""
        pass

# --- Estados Específicos del Juego ---

class MenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Menú Principal") # Para depuración

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # Al pulsar cualquier tecla, cambiamos al estado de juego
            self.game.change_state(PlayingState(self.game))

    def update(self, dt):
        # Lógica de actualización para el menú (ej. animaciones de fondo, parpadeo de texto)
        pass

    def draw(self, screen):
        screen.fill(DARK_GRAY) # Fondo oscuro

        # Título del juego
        font = pygame.font.Font(None, FONT_DEFAULT_SIZE_LARGE)
        text_surface = font.render(SCREEN_TITLE, True, WHITE)
        text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        screen.blit(text_surface, text_rect)

        # Mensaje para iniciar
        font_small = pygame.font.Font(None, FONT_DEFAULT_SIZE_SMALL)
        start_text_surface = font_small.render("Pulsa cualquier tecla para empezar", True, GREEN)
        start_text_rect = start_text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        screen.blit(start_text_surface, start_text_rect)

class PlayingState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Jugando") # Para depuración
        # Aquí inicializaremos el jugador, el nivel, los enemigos, etc.
        
        # --- Inicialización del Mapa y Jugador ---
        # Inicializa el mapa
        self.current_map = Map(self.game, MAP_WIDTH, MAP_HEIGHT)
        self.current_map.generate_dungeon() # Genera el mapa

        # Inicializa el jugador
        self.player = Player(self.game,
                            self.current_map.player_start_pos[0],
                            self.current_map.player_start_pos[1])
        
        # Inicializa una lista de enemigos     
        self.enemies = [] 
        self.place_enemies()

        self.pickups = [] # <-- Nueva lista para pickups
        self.place_enemies() # Ahora un método
        self.place_obstacles() # <-- Llama a un método para colocar obstáculos
        self.place_pickups() # <-- Nuevo método para colocar pickups


        # --- Inicialización de la Cámara ---
        self.camera = Camera(self.player, self.current_map.width, self.current_map.height)
        self.camera.update() # Asegura que la cámara se centre en el jugador al inicio

        # --- Gestión de mensajes en pantalla ---
        self.message = ""
        self.message_timer = 0 # Tiempo restante para mostrar el mensaje
        self.message_duration = 2000 # Duración en milisegundos (2 segundos)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            if event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1

            if dx != 0 or dy != 0:
                # Posición objetivo del jugador
                target_x = self.player.x + dx
                target_y = self.player.y + dy

                # --- Lógica de Combate / Movimiento del Jugador ---
                # 1. Comprobar si la casilla objetivo es un enemigo
                target_enemy = None
                for enemy in self.enemies:
                    if enemy.x == target_x and enemy.y == target_y and enemy.is_alive: # Solo si el enemigo está vivo
                        target_enemy = enemy
                        break

                player_action_taken = False # Bandera para saber si el jugador realizó una acción que consuma turno

                if target_enemy:
                    # El jugador intenta moverse a la casilla de un enemigo, ¡es un ataque!
                    player_action_taken = True
                    enemy_defeated = self.player.attack_target(target_enemy)
                    
                    if enemy_defeated:
                        # Elimina al enemigo de la lista si está derrotado
                        # Hacemos una nueva lista para evitar modificarla mientras iteramos
                        self.show_message("¡Enemigo Derrotado!")
                        self.enemies = [e for e in self.enemies if e.is_alive]
                        print(f"Enemigo derrotado. Quedan {len(self.enemies)} enemigos.")
                        
                else:
                     # El jugador no intentó atacar a un enemigo.
                    # Ahora, verificar si la casilla objetivo es un OBSTÁCULO.
                    collides_with_obstacle = False
                    for obstacle in self.current_map.obstacles:
                        if obstacle.x == target_x and obstacle.y == target_y:
                            collides_with_obstacle = True
                            break
                    
                    if collides_with_obstacle:
                        # Colisión con obstáculo, el jugador no se mueve.
                        # Considera esto una acción para gastar el turno.
                        player_action_taken = True # El jugador intentó algo, su turno se gasta.
                        print("Colisión con obstáculo, el jugador no se mueve.")
                    elif not self.current_map.is_walkable(target_x, target_y):
                        # Colisión con tile no caminable (pared, abismo), el jugador no se mueve.
                        player_action_taken = True # El jugador intentó algo, su turno se gasta.
                        print("Tile no caminable, el jugador no se mueve.")
                    else:
                        # Si no hay enemigo, ni obstáculo, ni tile no caminable, el jugador se mueve.
                        player_moved = self.player.move(dx, dy, self.current_map) # El método move del jugador actualiza su posición
                        if player_moved:
                            player_action_taken = True
                            
                            # --- Comprobar recogida de Pickups (después de que el jugador se mueve) ---
                            for pickup in self.pickups:
                                if not pickup.is_collected and \
                                   self.player.x == pickup.x and self.player.y == pickup.y:
                                    pickup.collect(self.player)
                                    break # Asumimos solo un pickup por casilla
                
                # --- Turno de los Enemigos (si el jugador realizó una acción) ---
                if player_action_taken:
                    # Creamos una copia de la lista de enemigos para iterar,
                    # ya que la lista original podría modificarse si un enemigo es derrotado.
                    enemies_to_move = list(self.enemies)
                    for enemy in enemies_to_move:
                        if enemy.is_alive: # Solo los enemigos vivos se mueven y atacan
                            # Comprueba si el enemigo está adyacente al jugador para atacar
                            if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                                # El enemigo está adyacente, ataca al jugador
                                player_defeated = enemy.attack_target(self.player)
                                if player_defeated:
                                    self.show_message("¡Has sido Derrotado! GAME OVER")
                                    print("¡GAME OVER! Has sido derrotado.")                                   
                                    self.game.request_state_change("game_over") 
                                    return # Sale del manejador de input si el jugador pierde
                            else:
                                # Si no está adyacente, intenta moverse
                                # Los enemigos también necesitan saber la posición del jugador para NO pisarla.
                                enemy.move(self.current_map, (self.player.x, self.player.y), self.enemies)

                    # Actualiza la cámara después de que todos los movimientos/acciones de los enemigos han terminado
                    self.camera.update()
            
            # Para probar el cambio de estado (pausa, etc.)
            if event.key == pygame.K_p:
                # self.game.change_state(PauseState(self.game))
                pass

    def update(self, dt):
        # Aquí se actualizará la lógica principal del juego:
        # - Movimiento del jugador
        # - Actualización de enemigos
        # - Lógica de combate
        # - etc.
       # Actualiza el temporizador de mensajes
        if self.message_timer > 0:
            self.message_timer -= (dt * 1000) # Restar en milisegundos
            if self.message_timer <= 0:
                self.message = "" # Borrar el mensaje cuando el tiempo expira
            pass

    def draw(self, screen):
        # La pantalla se limpia siempre al inicio del draw
        screen.fill(BLACK) # Color de fondo que se verá fuera del mapa

        # Dibuja el mapa primero
        self.current_map.draw(screen, self.camera)

        # Luego dibuja el jugador encima del mapa
        self.player.draw(screen, self.camera)

         # Dibuja los enemigos encima del mapa y del jugador
        for enemy in self.enemies:
            if enemy.is_alive:
                enemy.draw(screen, self.camera)

         # --- Dibuja obstáculos --- 
        for obstacle in self.current_map.obstacles:
            obstacle.draw(screen, self.camera)

        # --- Dibuja pickups --- 
        for pickup in self.pickups:
            pickup.draw(screen, self.camera)

        # --- HUD del Jugador ---
        # 1. Texto de HP
        font = pygame.font.Font(None, 24) # Puedes cargar una fuente real si tienes una en assets/fonts/
        hp_text = font.render(f"HP: {self.player.current_hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (10, 10))

        # 2. Barra de Vida (opcional, pero visualmente mejor)
        bar_width = 100
        bar_height = 15
        bar_x = 10
        bar_y = 35 # Debajo del texto de HP

        # Calcular el porcentaje de vida
        hp_percentage = self.player.current_hp / self.player.max_hp
        current_bar_width = int(bar_width * hp_percentage)

        # Dibujar el fondo de la barra (rojo oscuro)
        pygame.draw.rect(screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
        # Dibujar la parte de vida (verde)
        pygame.draw.rect(screen, GREEN, (bar_x, bar_y, current_bar_width, bar_height))
        # Dibujar el borde de la barra
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2) # 2 es el grosor del borde

        # --- Mensajes de estado (más adelante) ---
        # Por ahora, solo dibuja el HUD estático. Los mensajes temporales los añadiremos después.

         # --- Dibujar Mensaje de Estado ---
        if self.message:
            message_font = pygame.font.Font(None, 36) # Fuente para el mensaje
            message_surface = message_font.render(self.message, True, YELLOW) # Define YELLOW en constants.py

            # Centrar el mensaje en la pantalla
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(message_surface, message_rect)

        pygame.display.flip()

    def show_message(self, text):
        """Muestra un mensaje temporal en pantalla."""
        self.message = text
        self.message_timer = self.message_duration

    def place_enemies(self):
        """Coloca enemigos en el mapa después de la generación."""
        self.enemies = [] # Asegurarse de que la lista esté vacía antes de añadir nuevos
        
        # Recopila todas las posiciones de la carretera válidas para enemigos
        valid_spawn_tiles = []
        for x in range(self.current_map.width):
            for y in range(self.current_map.height):
                # Si es un tile de carretera, NO es la posición del jugador, ni la salida
                if self.current_map.tiles[x][y] == TILE_ROAD and \
                   (x, y) != self.current_map.player_start_pos and \
                   (x, y) != self.current_map.exit_pos:
                    # Además, verifica que no haya un obstáculo en esta posición (en un futuro, otros pickups, etc.)
                    is_occupied_by_obstacle = False
                    for obstacle in self.current_map.obstacles:
                        if obstacle.x == x and obstacle.y == y:
                            is_occupied_by_obstacle = True
                            break
                    if not is_occupied_by_obstacle:
                        valid_spawn_tiles.append((x, y))

        num_enemies_to_add = 5 # Puedes ajustar este número
        random.shuffle(valid_spawn_tiles)
        
        for i in range(min(num_enemies_to_add, len(valid_spawn_tiles))):
            enemy_x, enemy_y = valid_spawn_tiles[i]
            self.enemies.append(Enemy(self.game, enemy_x, enemy_y))
        
        print(f"Colocados {len(self.enemies)} enemigos en el mapa.")


    def place_obstacles(self):
        """Coloca obstáculos en el mapa, preferiblemente dentro de las habitaciones,
        evitando las posiciones de inicio del jugador y la salida."""
        self.current_map.obstacles = [] # Limpiar los obstáculos existentes

        valid_obstacle_tiles = []
        
        # Iterar sobre los tiles dentro de cada habitación
        for room_rect in self.current_map.room_rects:
            for x in range(room_rect.left, room_rect.right + 1):
                for y in range(room_rect.top, room_rect.bottom + 1):
                    # Asegurarse de que sea un tile caminable (road o garage_floor)
                    # Y que no sea la posición del jugador, ni la salida.
                    if self.current_map.is_walkable(x, y) and \
                       (x, y) != self.current_map.player_start_pos and \
                       (x, y) != self.current_map.exit_pos: 
                        valid_obstacle_tiles.append((x, y))

        random.shuffle(valid_obstacle_tiles)
        num_obstacles_to_add = 5 # Ajusta el número según lo desees
        
        for i in range(min(num_obstacles_to_add, len(valid_obstacle_tiles))):
            ox, oy = valid_obstacle_tiles[i]
            
            # --- NUEVA COMPROBACIÓN: Evitar superposición con enemigos o pickups ---
            is_occupied = False
            for enemy in self.enemies:
                if enemy.x == ox and enemy.y == oy:
                    is_occupied = True
                    break
            if is_occupied:
                continue # Pasa al siguiente tile si ya está ocupado por un enemigo

            for pickup in self.pickups: # Aunque los pickups se colocan después, esta verificación es buena para futuras expansiones
                if pickup.x == ox and pickup.y == oy and not pickup.is_collected:
                    is_occupied = True
                    break
            if is_occupied:
                continue # Pasa al siguiente tile si ya está ocupado por un pickup

            self.current_map.obstacles.append(Obstacle(self.game, ox, oy))
        
        print(f"Colocados {len(self.current_map.obstacles)} obstáculos.")

    def place_pickups(self):
        """Coloca pickups en el mapa después de la generación."""
        self.pickups = [] # Limpiar la lista de pickups

        valid_spawn_tiles = []
        for x in range(self.current_map.width):
            for y in range(self.current_map.height):
                # Si es un tile de carretera, no es la posición del jugador, ni la salida, ni un obstáculo, ni un enemigo
                if self.current_map.tiles[x][y] == TILE_ROAD and \
                (x,y) != self.player.x and (x,y) != self.player.y and \
                (x,y) != self.current_map.exit_pos:
                    # Comprueba si hay un obstáculo o un enemigo en esta posición
                    is_occupied = False
                    for obstacle in self.current_map.obstacles:
                        if obstacle.x == x and obstacle.y == y:
                            is_occupied = True
                            break
                    if not is_occupied:
                        for enemy in self.enemies: # También evita enemigos
                            if enemy.x == x and enemy.y == y:
                                is_occupied = True
                                break

                    if not is_occupied:
                        valid_spawn_tiles.append((x, y))

        random.shuffle(valid_spawn_tiles)
        num_pickups_to_add = 2 # Cantidad de pociones de vida

        for i in range(min(num_pickups_to_add, len(valid_spawn_tiles))):
            px, py = valid_spawn_tiles[i]
            self.pickups.append(Pickup(self.game, px, py, "health_potion")) # Crea una poción de vida

        print(f"Colocados {len(self.pickups)} pickups.")



class GameOverState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: Game Over")
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # 'R' para Reiniciar
                 self.game.request_state_change("playing")
            elif event.key == pygame.K_ESCAPE: # ESC para Salir
                self.game.running = False

    def update(self, dt):
        pass # No hay lógica de actualización continua en este estado

    def draw(self, screen):
        screen.fill(BLACK) # Fondo negro
        game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.small_font.render("Pulsa 'R' para Reiniciar o 'ESC' para Salir", True, WHITE)

        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        screen.blit(game_over_text, game_over_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()


class VictoryState(GameState):
    def __init__(self, game):
        super().__init__(game)
        print("Entrando en el estado: ¡Victoria!")
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r: # 'R' para Reiniciar
                self.game.request_state_change("playing")
            elif event.key == pygame.K_ESCAPE: # ESC para Salir
                self.game.running = False

    def update(self, dt):
        pass # No hay lógica de actualización continua

    def draw(self, screen):
        screen.fill(BLACK) # Fondo negro
        victory_text = self.font.render("¡VICTORIA!", True, GREEN)
        restart_text = self.small_font.render("Pulsa 'R' para Reiniciar o 'ESC' para Salir", True, WHITE)

        victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        screen.blit(victory_text, victory_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()