# Una clase que es una habitacion del juego donde tendra una posicion y un tamaño, un nivel. Ademas de una lista de objetos y enemigos, y una lista de puertas.
import pygame
import random
from utils.constants import *
from enemy import Enemy


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
        self.tiles = []

    def intersect(self, other):
        return (self.x < other.x + other.width and self.x + self.width > other.x and 
                self.y < other.y + other.height and self.y + self.height > other.y)
    
    def generate_contents(self):
         # Randomly place monsters and items within the room
        num_enemies = random.randint(0, 2)
        num_items = random.randint(0, 3)

        # Generate positions within the room
        
        tiles = [(x, y) for x in range(self.x + 1, self.x + self.width - 1)
                 for y in range(self.y + 1, self.y + self.height - 1)]

        random_tiles = random.sample(self.tiles, len(self.tiles))

        for tile in random_tiles:
            x, y = tile
            screen_x = x * TILE_SIZE
            screen_y = y * TILE_SIZE

            if num_enemies > 0:
                enemy = Enemy(self.game, x, y, "basic_grunt")
                self.enemies.add(enemy)
                num_enemies -= 1
                continue

            if num_items > 0:
            #    item_type = random.choice(['treasure', 'weapon', 'potion'])
            #    if item_type == 'treasure':
            #        item = Treasure((screen_x, screen_y))
            #    elif item_type == 'weapon':
            #        item = Weapon((screen_x, screen_y))
            #    else:
            #        # For 'potion', you can create a Potion class
            #        item = Potion((screen_x, screen_y))  # Placeholder
            #        item.type = 'potion'
            #    self.items.add(item)
            #    self.game.items_on_map.append(item)
                num_items -= 1
                continue
        
    def create_room(self, tiles, tile_type):  
        for x in range(min(self.left - 1, self.right + 1), max(self.left - 1, self.right + 1) + 1):
            for y in range(min(self.top - 1, self.bottom + 1), max(self.top - 1, self.bottom + 1) + 1):                 
                if 0 <= x < len(tiles) and 0 <= y < len(tiles[x]) and tiles[x][y] == TILE_ABYSS:
                    tiles[x][y] = TILE_WALL
                              
        for x in range(min(self.left, self.right), max(self.left, self.right) + 1):
            for y in range(min(self.top, self.bottom), max(self.top, self.bottom) + 1):                
                tiles[x][y] = tile_type

        