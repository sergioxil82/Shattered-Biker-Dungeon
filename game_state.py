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
from item import Item, Weapon, Armor, Consumable

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

         # Dibuja la imagen de bienvenida en el centro de la pantalla
        screen_rect = screen.get_rect()
        image_rect = self.game.welcome_image.get_rect(center=screen_rect.center)
        screen.blit(self.game.welcome_image, image_rect)       

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
        
        # Inicializa las listas     
        self.enemies = [] 
        self.pickups = []
        self.items_on_map = []
        
        self.place_enemies()
        self.place_enemies() # Ahora un método
        self.place_obstacles() # <-- Llama a un método para colocar obstáculos
        self.place_pickups() # <-- Nuevo método para colocar pickups
        self.place_items_on_map()


        # --- Inicialización de la Cámara ---
        self.camera = Camera(self.player, self.current_map.width, self.current_map.height)
        self.camera.update() # Asegura que la cámara se centre en el jugador al inicio

        # --- Gestión de mensajes en pantalla ---
        self.message = ""
        self.message_timer = 0 # Tiempo restante para mostrar el mensaje
        self.message_duration = 2000 # Duración en milisegundos (2 segundos)
       
        self.awaiting_powerful_attack_target = False

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            # --- Lógica de Inventario ---
            if event.key == pygame.K_i:
                self.player.inventory.toggle_open()
                return # No hacer nada más si abrimos/cerramos inventario

            if self.player.inventory.is_open:
                action_consumed_turn = self.player.inventory.handle_input(event)
                if action_consumed_turn:
                    self.process_enemy_turn()
                return # Consumir el evento si el inventario lo manejó
           

            # --- Lógica de Habilidades (antes del movimiento/ataque normal) ---
            if event.key == pygame.K_s: # Tecla para la habilidad
                if self.player.cooldown_powerful_attack > 0:
                    self.show_message("Ataque Potente en cooldown!")
                else:
                    # Si no está en cooldown, el jugador intentará usar la habilidad
                    # en el próximo ataque. Necesitamos un estado para esto.
                    self.show_message("Selecciona un enemigo para ATAQUE POTENTE.")
                    self.awaiting_powerful_attack_target = True # <-- ¡NUEVA VARIABLE!
                    return # Consumir el evento, no moverse todavía
                            
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
                    player_action_taken = True
                    if self.awaiting_powerful_attack_target: # Si estábamos esperando un objetivo para la habilidad
                        enemy_defeated = self.player.attack_target(target_enemy, is_powerful_attack=True)
                        self.awaiting_powerful_attack_target = False # Resetear la bandera
                    else:
                        enemy_defeated = self.player.attack_target(target_enemy)
                    
                    if enemy_defeated:
                        # Elimina al enemigo de la lista si está derrotado
                        # Hacemos una nueva lista para evitar modificarla mientras iteramos
                        # self.show_message("¡Enemigo Derrotado!")
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
                        # Si el jugador se mueve, cancela la selección de habilidad
                        if self.awaiting_powerful_attack_target:
                            self.awaiting_powerful_attack_target = False
                            self.show_message("Ataque Potente cancelado.")

                        player_moved = self.player.move(dx, dy, self.current_map)
                        if player_moved:
                            player_action_taken = True
                            
                            # --- Comprobar recogida de Pickups (después de que el jugador se mueve) ---
                            for pickup in self.pickups:
                                if not pickup.is_collected and \
                                   self.player.x == pickup.x and self.player.y == pickup.y:
                                    pickup.collect(self.player)
                                    break # Asumimos solo un pickup por casilla
                            
                            # --- Comprobar recogida de Items del mapa --- <-- ¡NUEVA LÓGICA AQUÍ!
                            # Crear una copia invertida para eliminar de forma segura mientras iteramos
                            items_to_remove = []
                            for item_on_map in self.items_on_map:
                                if self.player.x == item_on_map.x and self.player.y == item_on_map.y:
                                    if self.player.inventory.add_item(item_on_map): # Usar inventario del jugador
                                        items_to_remove.append(item_on_map)
                                        # Suena un sonido de recogida
                                        self.game.sound_pickup.play()
                                    break # Un ítem por casilla

                            for item_to_remove in items_to_remove:
                                self.items_on_map.remove(item_to_remove)

                # --- Turno de los Enemigos (si el jugador realizó una acción) ---
                if player_action_taken:
                    self.process_enemy_turn()
                    # --- Actualizar cooldowns del jugador después de su turno ---
                    self.player.end_turn_update() 
                   
            
            # Para probar el cambio de estado (pausa, etc.)
            if event.key == pygame.K_p:
                # self.game.change_state(PauseState(self.game))
                pass

    # --- Nuevo método para procesar el turno de los enemigos ---
    def process_enemy_turn(self):
        enemies_to_process = list(self.enemies)
        for enemy in enemies_to_process:
            if enemy.is_alive:
                if abs(enemy.x - self.player.x) + abs(enemy.y - self.player.y) == 1:
                    player_defeated = enemy.attack_target(self.player)
                    if player_defeated:
                        self.show_message("¡Has sido Derrotado! GAME OVER")
                        self.game.request_state_change("game_over")
                        return # Salir si el jugador pierde
                else:
                    enemy.move(self.current_map, (self.player.x, self.player.y), self.enemies)

        # Actualiza la cámara después de que todos los movimientos/acciones de los enemigos han terminado
        self.camera.update()

        # Comprobar la condición de victoria (después del turno del enemigo)
        if self.player.x == self.current_map.exit_pos[0] and self.player.y == self.current_map.exit_pos[1]:
            self.show_message("¡Has encontrado la salida! ¡VICTORIA!")
            self.game.request_state_change("victory")
            return # Salir si el jugador gana
        
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

        # --- Dibuja ítems en el mapa --- 
        for item_on_map in self.items_on_map:
            # Los ítems no se "recogen" de forma instantánea al pasar, solo al interactuar.
            # Para simplificar ahora, si el jugador se mueve sobre ellos, se recogen.
            # La lógica de recolección está en handle_input
            item_on_map_rect_world = pygame.Rect(item_on_map.x * TILE_SIZE, item_on_map.y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            screen.blit(item_on_map.image, self.camera.apply(item_on_map_rect_world))

        # Dibuja el HUD (barra de vida, etc.) 
        self.draw_hud(screen)       

        # --- Dibujar Mensaje de Estado ---
        if self.message:
            message_font = pygame.font.Font(None, 36) # Fuente para el mensaje
            message_surface = message_font.render(self.message, True, YELLOW) # Define YELLOW en constants.py

            # Centrar el mensaje en la pantalla
            message_rect = message_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(message_surface, message_rect)
                
        # --- Dibuja Inventario si está abierto (delegado al inventario del jugador) ---
        self.player.inventory.draw(screen) # El inventario solo se dibuja si is_open es True
        

    def draw_hud(self, screen):
        """Dibuja la interfaz de usuario (HUD) en la pantalla."""
        # Barra de vida
        hp_bar_width = 150
        hp_bar_height = 20
        hp_bar_x = 10
        hp_bar_y = 10
        
        # Color de la barra de vida (verde si está bien, amarillo si medio, rojo si bajo)
        hp_percentage = self.player.current_hp / self.player.max_hp
        if hp_percentage > 0.6:
            hp_color = GREEN
        elif hp_percentage > 0.25:
            hp_color = YELLOW
        else:
            hp_color = RED

        pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_bar_width * hp_percentage, hp_bar_height))
        pygame.draw.rect(screen, WHITE, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2) # Borde blanco

        # Texto de HP
        hp_text = self.game.font.render(f"HP: {self.player.current_hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))

        # Ataque y Defensa
        attack_text = self.game.font.render(f"Ataque: {self.player.attack}", True, WHITE)
        defense_text = self.game.font.render(f"Defensa: {self.player.defense}", True, WHITE)
        screen.blit(attack_text, (10, hp_bar_y + hp_bar_height + 10))
        screen.blit(defense_text, (10, hp_bar_y + hp_bar_height + 40))

        # Cooldown de Habilidad
        skill_cooldown_text = self.game.font.render(
            f"Ataque Potente CD: {self.player.cooldown_powerful_attack}",
            True, WHITE if self.player.cooldown_powerful_attack == 0 else YELLOW
        )
        screen.blit(skill_cooldown_text, (10, SCREEN_HEIGHT - 60))

        # Instrucciones de habilidad (opcional, si tienes un font_small, si no, usa el font normal)
        # Asegúrate de tener el font_small cargado en main.py si lo usas.
        try:
            skill_inst_text = self.game.font_small.render("S: Ataque Potente", True, WHITE)
        except AttributeError: # Si self.game.font_small no existe, usa el font normal
            skill_inst_text = self.game.font.render("S: Ataque Potente", True, WHITE)
            
        screen.blit(skill_inst_text, (10, SCREEN_HEIGHT - 30))

        # Efectos de Estado
        y_offset_effects = SCREEN_HEIGHT - 90
        for effect_name, effect_data in self.player.status_effects.items():
            effect_text = self.game.font.render( # Usamos el font normal aquí, puedes ajustar
                f"{effect_name.title()} ({effect_data['duration']}t)",
                True, YELLOW if effect_name == "poisoned" else WHITE # Color diferente para veneno
            )
            # Dibuja los efectos desde la esquina inferior derecha, apilando hacia arriba
            screen.blit(effect_text, (SCREEN_WIDTH - effect_text.get_width() - 10, y_offset_effects))
            y_offset_effects -= 25 # Mueve el siguiente texto 25 píxeles hacia arriba

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
            # Decidir aleatoriamente el tipo de enemigo
            enemy_type = "basic_grunt"
            if random.random() < 0.3: # 30% de probabilidad de ser un Heavy Hitter
                enemy_type = "heavy_hitter"
            # Puedes añadir más condiciones para otros tipos de enemigos aquí

            self.enemies.append(Enemy(self.game, enemy_x, enemy_y, enemy_type))            
        
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

    def place_items_on_map(self):
        """Coloca ítems (armas, armaduras, consumibles) en el mapa."""
        self.items_on_map = []
        valid_item_spawn_tiles = []

        for room_rect in self.current_map.room_rects:
            for x in range(room_rect.left, room_rect.right + 1):
                for y in range(room_rect.top, room_rect.bottom + 1):
                    # Evita superposición con jugador, salida, obstáculos, enemigos y pickups existentes
                    if self.current_map.is_walkable(x, y) and \
                    (x, y) != self.player.x and (x, y) != self.player.y and \
                    (x, y) != self.current_map.exit_pos:

                        is_occupied = False
                        for obstacle in self.current_map.obstacles:
                            if obstacle.x == x and obstacle.y == y:
                                is_occupied = True
                                break
                        if is_occupied: continue

                        for enemy in self.enemies:
                            if enemy.x == x and enemy.y == y:
                                is_occupied = True
                                break
                        if is_occupied: continue

                        for pickup in self.pickups:
                            if pickup.x == x and pickup.y == y and not pickup.is_collected:
                                is_occupied = True
                                break
                        if is_occupied: continue

                        valid_item_spawn_tiles.append((x, y))

        random.shuffle(valid_item_spawn_tiles)

        # Ejemplos de ítems para colocar
        items_to_spawn = [
            Weapon(self.game, "Llave Inglesa", "Un arma de mano oxidada.", 5, "assets/items/wrench.png"),
            Armor(self.game, "Chaleco Cuero", "Protección básica de motero.", 3, "assets/items/leather_vest.png"),
            Consumable(self.game, "Café Turbo", "Te da un subidón de energía.", {"heal": 10}, "assets/items/coffee.png"),
            Weapon(self.game, "Bate con Clavos", "¡Duele mucho!", 10, "assets/items/spiked_bat.png")
        ]

        for i in range(min(len(items_to_spawn), len(valid_item_spawn_tiles))):
            item = items_to_spawn[i]
            ix, iy = valid_item_spawn_tiles[i]
            # Le damos al ítem una posición para que se pueda dibujar
            item.x = ix
            item.y = iy
            self.items_on_map.append(item)

        print(f"Colocados {len(self.items_on_map)} ítems en el mapa.")

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
        screen.fill(RED) # Llena la pantalla con rojo o el color de fondo que prefieras

        # Dibuja la imagen de derrota en el centro de la pantalla
        screen_rect = screen.get_rect()
        image_rect = self.game.game_over_image.get_rect(center=screen_rect.center)
        screen.blit(self.game.game_over_image, image_rect)
        #game_over_text = self.font.render("GAME OVER", True, RED)
        restart_text = self.small_font.render("Pulsa 'R' para Reiniciar o 'ESC' para Salir", True, WHITE)

        #game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        #screen.blit(game_over_text, game_over_rect)
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
        screen.fill(GREEN) # Llena la pantalla con verde o el color de fondo que prefieras

        # Dibuja la imagen de victoria en el centro de la pantalla
        screen_rect = screen.get_rect()
        image_rect = self.game.victory_image.get_rect(center=screen_rect.center)
        screen.blit(self.game.victory_image, image_rect)

        #victory_text = self.font.render("¡VICTORIA!", True, GREEN)
        restart_text = self.small_font.render("Pulsa 'R' para Reiniciar o 'ESC' para Salir", True, WHITE)

        # victory_rect = victory_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))

        # screen.blit(victory_text, victory_rect)
        screen.blit(restart_text, restart_rect)
        pygame.display.flip()