# dungeon_generator.py
import random
import pygame
from room import Room
from utils.constants import *

class Map:
    def __init__(self, game, width, height):
        self.game = game
        self.width = width
        self.height = height
        # Inicializa todo el mapa como ABISMO (negro)
        self.tiles = [[TILE_ABYSS for _ in range(self.height)] for _ in range(self.width)]

        # --- FOV y Niebla de Guerra ---
        # 0: HIDDEN, 1: EXPLORED, 2: VISIBLE
        self.visibility_map = [[0 for _ in range(self.height)] for _ in range(self.width)]
        self.fov_radius = 8 # Radio de visión del jugador en tiles

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
        self.visibility_map = [[0 for _ in range(self.height)] for _ in range(self.width)] # Reiniciar FOV
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
                tile_rect_world  = pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE)
                tile_rect_screen = camera.apply(tile_rect_world)
                visibility = self.visibility_map[x][y] if self.game.config.get("fov_enabled", True) else 2

                if visibility == 0: # HIDDEN
                    pygame.draw.rect(screen, BLACK, tile_rect_screen) # O no dibujar nada
                else:
                    tile_image = self.game.tile_images.get(tile_type)
                    if tile_image:
                        img_to_draw = tile_image.copy()
                        if visibility == 1: # EXPLORED (pero no visible)
                            # Aplicar un tinte oscuro
                            dark_surface = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert_alpha()
                            dark_surface.fill((0, 0, 0, 150)) # Negro con transparencia
                            img_to_draw.blit(dark_surface, (0,0))
                        screen.blit(img_to_draw, tile_rect_screen)
                    else: # Placeholder de color si no hay imagen
                        color = BLACK 
                        if tile_type == TILE_ROAD: color = COLOR_ROAD
                        elif tile_type == TILE_WALL: color = COLOR_WALL
                        elif tile_type == TILE_GARAGE_FLOOR: color = COLOR_GARAGE_FLOOR
                        elif tile_type == TILE_ENTRANCE: color = COLOR_ENTRANCE
                        elif tile_type == TILE_EXIT: color = COLOR_EXIT
                        elif tile_type == TILE_ABYSS: color = COLOR_ABYSS
                        elif tile_type == TILE_OBJECT: color = COLOR_OBJECT
                        
                        if visibility == 1: # Tinte para explorado
                            r, g, b = color
                            color = (max(0, r-100), max(0, g-100), max(0, b-100))
                        pygame.draw.rect(screen, color, tile_rect_screen)
                

        # --- DIBUJAR LOS OBSTÁCULOS DESPUÉS DE LOS TILES ---        
        for obstacle in self.obstacles:
            # Solo dibujar si el tile del obstáculo es visible o explorado
            visibility = self.visibility_map[obstacle.x][obstacle.y] if self.game.config.get("fov_enabled", True) else 2
            if visibility > 0: # VISIBLE o EXPLORED
                obstacle_rect_world = obstacle.get_rect()
                screen_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT) # Para culling
                if camera.apply(obstacle_rect_world).colliderect(screen_rect):
                    img_to_draw = obstacle.image.copy()
                    if visibility == 1: # EXPLORED
                        dark_surface = pygame.Surface((TILE_SIZE, TILE_SIZE)).convert_alpha()
                        dark_surface.fill((0, 0, 0, 150))
                        img_to_draw.blit(dark_surface, (0,0)) 
                    screen.blit(img_to_draw, camera.apply(obstacle_rect_world))
                    
    def is_transparent(self, x, y):
        """Determina si un tile bloquea la visión."""
        if 0 <= x < self.width and 0 <= y < self.height:
            # Los tiles de suelo, carretera, entrada, salida son transparentes.
            # Las paredes y obstáculos bloquean la visión.
            tile = self.tiles[x][y]
            return tile not in [TILE_WALL, TILE_OBJECT, TILE_ABYSS] # Abismo también bloquea
        return False # Fuera del mapa bloquea la visión

    def update_fov(self, player_x, player_y):
        """Calcula el campo de visión del jugador."""
        if not self.game.config.get("fov_enabled", True): # Si FOV está desactivado, todo visible
            for x in range(self.width):
                for y in range(self.height):
                    self.visibility_map[x][y] = 2 # VISIBLE
            return

        # Primero, todos los tiles que eran VISIBLE ahora son EXPLORED
        for x_v in range(self.width):
            for y_v in range(self.height):
                if self.visibility_map[x_v][y_v] == 2: # Si era VISIBLE
                    self.visibility_map[x_v][y_v] = 1 # Ahora es EXPLORED

        # El tile del jugador siempre es visible
        self.visibility_map[player_x][player_y] = 2 # VISIBLE

        # Algoritmo de Shadow Casting (simplificado para 8 octantes)
        for octant in range(8):
            self._cast_light(player_x, player_y, 1, 1.0, 0.0, octant)

    def _cast_light(self, cx, cy, row, start_slope, end_slope, octant):
        if start_slope < end_slope:
            return

        for i in range(row, self.fov_radius + 1):
            blocked = False
            dx, dy = -i, -i # Para iterar sobre las celdas de la fila actual del octante
            for j in range(i + 1): # Iterar sobre las celdas de la fila
                # Transformar coordenadas según el octante
                # Esta es la parte compleja del Shadow Casting, mapear (i, j) a (map_x, map_y)
                # según el octante.
                # Por simplicidad, aquí usaremos una aproximación de "círculo"
                # y luego refinaremos si es necesario.
                # Esta es una implementación MUY simplificada y no es Shadow Casting real.
                # Para un Shadow Casting correcto, se necesitan transformaciones por octante.
                # --- INICIO APROXIMACIÓN SIMPLE (CÍRCULO) ---
                for angle in range(0, 360, 5): # Comprobar rayos en varias direcciones
                    rad = angle * (3.14159 / 180.0)
                    for r in range(1, self.fov_radius + 1):
                        map_x = cx + int(r * pygame.math.Vector2(1, 0).rotate_rad(rad).x)
                        map_y = cy + int(r * pygame.math.Vector2(1, 0).rotate_rad(rad).y)

                        if 0 <= map_x < self.width and 0 <= map_y < self.height:
                            self.visibility_map[map_x][map_y] = 2 # VISIBLE
                            if not self.is_transparent(map_x, map_y): # Si el tile bloquea la luz
                                break # Detener este rayo
                return # Salir después de la aproximación simple
                # --- FIN APROXIMACIÓN SIMPLE ---
                # El código de Shadow Casting real iría aquí, manejando pendientes y octantes.
