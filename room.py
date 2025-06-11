# Una clase que es una habitacion del juego donde tendra una posicion y un tamaño, un nivel. Ademas de una lista de objetos y enemigos, y una lista de puertas.
import pygame
import random
from utils.constants import *
from enemy import Enemy
from item import Weapon, Armor, Consumable

class Room(pygame.Rect):
    def __init__(self, game, x, y, width, height, level):
        super().__init__(x, y, width, height)
        self.game = game
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.level = level
        self.objects = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.doors = pygame.sprite.Group()
        self.center = (self.x + self.width/2, self.y + self.height/2)        

    def intersect(self, other):
        return (self.x < other.x + other.width and self.x + self.width > other.x and 
                self.y < other.y + other.height and self.y + self.height > other.y)
    
   
    def generate_contents(self, playing_state):
        """Genera enemigos e ítems dentro de esta habitación y los añade a PlayingState."""
        
        # Obtener tiles caminables dentro de la habitación (excluyendo bordes si son paredes)
        # Asumimos que los tiles internos de la habitación ya son caminables (TILE_GARAGE_FLOOR)
        possible_spawn_points = []
        for r_x in range(self.left, self.right): # Iterar sobre el interior de la habitación
            for r_y in range(self.top, self.bottom):
                # Asegurarse de que no sea la posición de inicio del jugador ni la salida del mapa
                if (r_x, r_y) != playing_state.current_map.player_start_pos and \
                   (r_x, r_y) != playing_state.current_map.exit_pos:
                    possible_spawn_points.append((r_x, r_y))
        
        random.shuffle(possible_spawn_points)
        
        # --- Generar Enemigos (solo si no es la habitación inicial) ---
        if self.level != 0: # La habitación 0 es la inicial
            num_enemies_to_spawn = random.randint(0, 5)
            for _ in range(num_enemies_to_spawn):
                if not possible_spawn_points: break # No más puntos disponibles
                
                spawn_x, spawn_y = possible_spawn_points.pop()
                
                enemy_type = "basic_grunt"
                if random.random() < 0.3:
                    enemy_type = "heavy_hitter"
                
                initial_state = random.choice(["idle", "alert"])
                
                new_enemy = Enemy(self.game, spawn_x, spawn_y, enemy_type, room_rect=self)
                new_enemy.state = initial_state # Establecer estado inicial
                playing_state.enemies.append(new_enemy)
                print(f"Room {self.level} generó {enemy_type} en ({spawn_x},{spawn_y}) en estado {initial_state}")
        else:
            print(f"Room {self.level} (inicial) no generará enemigos.")

        # --- Generar Ítems ---
        num_items_to_spawn = random.randint(0, 3)
        available_items = [
            Weapon(self.game, "Llave Inglesa", "Un arma de mano oxidada.", 5, "assets/items/wrench.png"),
            Armor(self.game, "Chaleco Cuero", "Protección básica de motero.", 3, "assets/items/leather_vest.png"),
            Consumable(self.game, "Café Turbo", "Te da un subidón de energía.", {"heal": 10}, "assets/items/coffee.png"),
            Weapon(self.game, "Bate con Clavos", "¡Duele mucho!", 10, "assets/items/spiked_bat.png"),
            Consumable(self.game, "Bidón Gasolina", "Rellena combustible de la moto.", {"refuel": 50}, "assets/items/gas_can.png")
        ]
        for _ in range(num_items_to_spawn):
            if not possible_spawn_points or not available_items: break
            
            spawn_x, spawn_y = possible_spawn_points.pop()
            item_to_place = random.choice(available_items) # Podrías querer evitar duplicados o tener una lista más grande
            item_to_place.x = spawn_x
            item_to_place.y = spawn_y
            playing_state.items_on_map.append(item_to_place)
            print(f"Room {self.level} generó {item_to_place.name} en ({spawn_x},{spawn_y})")
        
    def create_room(self, tiles, tile_type):  
        for x in range(min(self.left - 1, self.right + 1), max(self.left - 1, self.right + 1) + 1):
            for y in range(min(self.top - 1, self.bottom + 1), max(self.top - 1, self.bottom + 1) + 1):                 
                if 0 <= x < len(tiles) and 0 <= y < len(tiles[x]) and tiles[x][y] == TILE_ABYSS:
                    tiles[x][y] = TILE_WALL
                              
        for x in range(min(self.left, self.right), max(self.left, self.right) + 1):
            for y in range(min(self.top, self.bottom), max(self.top, self.bottom) + 1):  
                if 0 <= x < len(tiles) and 0 <= y < len(tiles[x]):              
                    tiles[x][y] = tile_type

        