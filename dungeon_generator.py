# dungeon_generator.py
import random
import pygame
from room import Room
from utils.constants import *
from objects import Obstacle 

class Map:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        # Inicializa todo el mapa como ABISMO (negro)
        self.tiles = [[TILE_ABYSS for _ in range(self.height)] for _ in range(self.width)]
        self.player_start_pos = None
        self.exit_pos = None # Asegúrate de que exit_pos esté inicializado
        self.obstacles = []
        self.room_rects = [] 
   

    # Ayudante: Para crear un pasillo horizontal
    def _create_h_tunnel(self, x1, x2, y, tile_type):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.tiles[x][y] != TILE_GARAGE_FLOOR:
                    self.tiles[x][y] = tile_type

    # Ayudante: Para crear un pasillo vertical
    def _create_v_tunnel(self, y1, y2, x, tile_type):
        for y in range(min(y1, y2), max(y1, y2) + 1):
            if 0 <= x < self.width and 0 <= y < self.height:
                if self.tiles[x][y] != TILE_GARAGE_FLOOR:
                    self.tiles[x][y] = tile_type

    def generate_dungeon(self, playing_state, max_rooms=10, min_room_size=6, max_room_size=12):
        """Genera una mazmorra con habitaciones y pasillos."""
        # --- LIMPIAR ESTADO DEL MAPA ANTERIOR ---
        self.tiles = [[TILE_ABYSS for _ in range(self.height)] for _ in range(self.width)]
        self.player_start_pos = None
        self.exit_pos = None
        self.room_rects = [] # Limpiar la lista de rectángulos de habitaciones
        # self.obstacles se limpia en playing_state.place_obstacles() si es necesario

        rooms = []
        num_rooms = 0

        for r in range(max_rooms):
            # Dimensiones y posición aleatorias de la habitación
            w = random.randint(min_room_size, max_room_size)
            h = random.randint(min_room_size, max_room_size)
            x = random.randint(1, self.width - w - 1) # Asegura espacio para paredes
            y = random.randint(1, self.height - h - 1)

            # Crea un rectángulo para representar la habitación
            #new_room = pygame.Rect(x, y, w, h)
            new_room = Room(self.game, x, y, w, h, num_rooms)
            # Comprueba si se solapa con otras habitaciones
            
            intersects = False
            for other_room in rooms:                
                if new_room.intersect(other_room):                    
                    intersects = True
                    break

            if not intersects:
                # Si no se solapa, crea la habitación
                # self._create_room(new_room.left, new_room.top, new_room.right, new_room.bottom, TILE_ROAD)
                new_room.create_room(self.tiles, TILE_GARAGE_FLOOR)
                # Opcional: poner paredes alrededor de la habitación
                # Esto es más complejo si las habitaciones se solapan con pasillos,
                # por ahora simplificamos dejando TILE_ABYSS o TILE_WALL por defecto.
                # Para un estilo de "paredes de mazmorra", puedes hacer:
                # self._create_room(new_room.left - 1, new_room.top - 1, new_room.right + 1, new_room.bottom + 1, TILE_WALL)
                # Y luego rellenar el interior con TILE_ROAD.

                # Guarda el rectángulo de la habitación (para colocar obstáculos, etc.)
                self.room_rects.append(new_room)

                # Conecta la nueva habitación con la anterior si no es la primera
                if num_rooms > 0:
                    prev_room = rooms[num_rooms - 1]

                    # Coordenadas centrales
                    new_x, new_y = new_room.center
                    prev_x, prev_y = prev_room.center

                    # Conecta con pasillos (aleatoriamente horizontal y luego vertical, o viceversa)
                    if random.randint(0, 1) == 1:
                        self._create_h_tunnel(prev_x, new_x, prev_y, TILE_ROAD)
                        self._create_v_tunnel(prev_y, new_y, new_x, TILE_ROAD)
                    else:
                        self._create_v_tunnel(prev_y, new_y, prev_x, TILE_ROAD)
                        self._create_h_tunnel(prev_x, new_x, new_y, TILE_ROAD)

                 # --- Generar contenido de la habitación ---
                new_room.generate_contents(playing_state) # Pasar la instancia de PlayingState
                
                rooms.append(new_room)
                num_rooms += 1

        # Establece el punto de inicio del jugador y la salida en la primera y última habitación
        if rooms:
            first_room = rooms[0]            
            # Seleccionar una pared de la primera habitación para el inicio
            # (x, y) será una coordenada de pared adyacente al interior
            start_x_options = [first_room.left -1, first_room.right]
            start_y_options = [first_room.top -1, first_room.bottom]
            
            #Elegir aleatoriamente una pared (arriba, abajo, izquierda, derecha)
            if random.choice([True, False]): # Pared vertical (izquierda o derecha)
                self.player_start_pos = (random.choice(start_x_options), random.randint(first_room.top, first_room.bottom -1))
            else: # Pared horizontal (arriba o abajo)
                self.player_start_pos = (random.randint(first_room.left, first_room.right-1), random.choice(start_y_options))

            # Asegurarse de que la posición de inicio esté dentro de los límites del mapa
            self.player_start_pos = (max(0, min(self.player_start_pos[0], self.width - 1)),
                                     max(0, min(self.player_start_pos[1], self.height - 1)))
            self.tiles[self.player_start_pos[0]][self.player_start_pos[1]] = TILE_ENTRANCE

            last_room = rooms[-1]
            # Seleccionar una pared de la última habitación para la salida
            exit_x_options = [last_room.left -1, last_room.right]
            exit_y_options = [last_room.top -1, last_room.bottom]

            if random.choice([True, False]):
                self.exit_pos = (random.choice(exit_x_options), random.randint(last_room.top, last_room.bottom -1))
            else:
                self.exit_pos = (random.randint(last_room.left, last_room.right-1), random.choice(exit_y_options))
            
            self.exit_pos = (max(0, min(self.exit_pos[0], self.width - 1)),
                             max(0, min(self.exit_pos[1], self.height - 1)))
            self.tiles[self.exit_pos[0]][self.exit_pos[1]] = TILE_EXIT

        print(f"Mazmorra generada con {num_rooms} habitaciones.")

        # Opcional: Rellenar las zonas restantes fuera de los caminos con TILE_WALL
        for x in range(self.width):
            for y in range(self.height):
                if self.tiles[x][y] == TILE_ABYSS: # Solo si sigue siendo abismo
                    self.tiles[x][y] = TILE_ABYSS # Convierte el abismo no usado en pared      
    
    def get_room_at(self, x, y):
        """Devuelve el objeto Room en las coordenadas (x,y) o None si no está en ninguna habitación."""
        for room in self.room_rects: # room_rects es una lista de objetos Room
            if room.collidepoint(x, y): # pygame.Rect.collidepoint usa coordenadas de tile aquí
                return room
        return None
    
    def get_tile_at(self, x, y):
        # Esta función es crucial para is_walkable.
        # Si las coordenadas están fuera de los límites del mapa, es ABISMO.
        if 0 <= x < self.width and 0 <= y < self.height:
            return self.tiles[x][y]
        return TILE_ABYSS # Si está fuera de los límites del mapa, siempre es ABISMO

    def is_walkable(self, x, y):
        # Utiliza get_tile_at para obtener el tipo de tile (maneja los límites automáticamente)
        tile = self.get_tile_at(x, y)

        # Solo estos tipos de tiles son caminables
        return tile == TILE_ROAD or \
               tile == TILE_GARAGE_FLOOR or \
               tile == TILE_ENTRANCE or \
               tile == TILE_EXIT


    def draw(self, screen, camera):
        """Dibuja el mapa usando placeholders de color."""
        # Calcula los límites de los tiles visibles para la cámara
        start_tile_x = max(0, -camera.offset_x // TILE_SIZE)
        end_tile_x = min(self.width, (-camera.offset_x + camera.camera_width) // TILE_SIZE + 1)
        start_tile_y = max(0, -camera.offset_y // TILE_SIZE)
        end_tile_y = min(self.height, (-camera.offset_y + camera.camera_height) // TILE_SIZE + 1)

         # --- DIBUJAR LOS TILES DEL MAPA PRIMERO ---
        for x in range(start_tile_x, end_tile_x):
            for y in range(start_tile_y, end_tile_y):
                tile_type = self.tiles[x][y]

                # Obtén la imagen del tile del diccionario del juego
                # self.game.tile_images es la forma de accederlo desde el mapa
                # Nota: Necesitamos pasar `game` al constructor del mapa para que pueda acceder a `tile_images`.
                # Vamos a cambiar eso primero en `PlayingState` y `Map` constructor.
                # Asumamos por ahora que `self.game` está accesible aquí.
                # Pero la forma correcta es que `game_state` le pase el diccionario al `map.draw`.

                # --- Corrección importante aquí: Map.draw no tiene acceso directo a self.game ---
                # El método `draw` de Map recibe `screen` y `camera`.
                # Para acceder a las imágenes, necesitas que `PlayingState` las pase al `Map.draw`
                # O que `Map` reciba una referencia al objeto `Game` en su `__init__`.
                # La segunda opción es más limpia para esto.

                # Opción 1 (más limpia): Pasa `game` al constructor del mapa
                # Si en PlayingState tienes:
                # self.current_map = Map(MAP_WIDTH, MAP_HEIGHT)
                # DEBERÍA SER:
                # self.current_map = Map(self.game, MAP_WIDTH, MAP_HEIGHT) # <--- CAMBIO IMPORTANTE
                # Y el __init__ de Map:
                # def __init__(self, game, width, height):
                #     self.game = game # <--- AÑADE ESTO
                #     self.width = width
                #     self.height = height
                #     # ... resto del __init__

                # Asumiendo que `self.game` ahora está accesible en `Map`:
                tile_image = self.game.tile_images.get(tile_type)

                tile_rect_world  = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_rect_screen = camera.apply(tile_rect_world)

                if tile_image: # Solo dibuja si hay una imagen cargada para este tipo de tile
                    screen.blit(tile_image, tile_rect_screen)
                else: # Si no hay imagen, dibuja un placeholder de color (útil para depuración)
                    color = BLACK # O un color por defecto
                    if tile_type == TILE_ROAD: color = COLOR_ROAD
                    elif tile_type == TILE_WALL: color = COLOR_WALL
                    elif tile_type == TILE_GARAGE_FLOOR: color = COLOR_GARAGE_FLOOR
                    elif tile_type == TILE_ENTRANCE: color = COLOR_ENTRANCE
                    elif tile_type == TILE_EXIT: color = COLOR_EXIT
                    elif tile_type == TILE_ABYSS: color = COLOR_ABYSS
                    elif tile_type == TILE_OBJECT: color = COLOR_OBJECT
                    pygame.draw.rect(screen, color, tile_rect_screen)

        # --- DIBUJAR LOS OBSTÁCULOS DESPUÉS DE LOS TILES ---
        # Asegúrate de que obstacle_image se haya cargado en main.py y sea accesible aquí.
        # Asumiendo que `self.game` está accesible y `self.game.obstacle_image` existe:
        for obstacle in self.obstacles:
            obstacle_rect_world = obstacle.get_rect()
            screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
            if camera.apply(obstacle_rect_world).colliderect(screen_rect):
                # Dibuja el sprite del obstáculo en lugar del color
                obstacle_rect_screen = camera.apply(obstacle_rect_world)
                if hasattr(self.game, 'obstacle_image') and self.game.obstacle_image:
                    screen.blit(self.game.obstacle_image, obstacle_rect_screen)                 
                else: # Si no hay imagen de obstáculo, dibuja el color
                    pygame.draw.rect(screen, obstacle.color, obstacle_rect_screen)
                    