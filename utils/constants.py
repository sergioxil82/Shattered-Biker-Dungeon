# utils/constants.py

# --- Configuración de la Pantalla ---
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 960
SCREEN_TITLE = "Shattered Biker Dungeon"
FPS = 60 # Frames por segundo

# --- Colores (RGB) ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)
DARK_RED = (139, 0, 0)
PURPLE = (128,0,128)

# --- Configuración del Juego (Ejemplos iniciales, se expandirán) ---
TILE_SIZE = 32 # Tamaño de cada "tile" en píxeles (importante para gráficos basados en cuadrícula)
PLAYER_SPEED = 5 # Velocidad de movimiento del jugador (en píxeles por frame o tiles por turno, según el sistema de movimiento)

# --- Enemigos
ENEMY_SPEED = 1

# --- Fuentes ---
# Usaremos None para la fuente por defecto de Pygame o especificar rutas a archivos .ttf
FONT_DEFAULT_SIZE_LARGE = 74
FONT_DEFAULT_SIZE_MEDIUM = 48
FONT_DEFAULT_SIZE_SMALL = 36

# --- Configuración del Mapa/Nivel ---
MAP_WIDTH = 60  # Ancho del mapa en tiles
MAP_HEIGHT = 45 # Alto del mapa en tiles

# Tipos de Tiles (usaremos números para representarlos en la matriz del mapa)
TILE_WALL = 0       # Pared / Obstáculo intransitable
TILE_ROAD = 1       # Carretera / Suelo transitable
TILE_GARAGE_FLOOR = 2 # Suelo de garaje / Zona de interiores
TILE_ENTRANCE = 3   # Entrada / Punto de inicio
TILE_EXIT = 4       # Salida / Objetivo del nivel
TILE_ABYSS = 5      # Tipo de tile para el abismo
TILE_OBJECT = 6     # Tipo de tile para los objetos

# Colores para los placeholders de tiles
COLOR_ROAD = DARK_GRAY
COLOR_WALL = YELLOW
COLOR_GARAGE_FLOOR = GRAY
COLOR_ENTRANCE = GREEN
COLOR_EXIT = RED
COLOR_ABYSS = WHITE
COLOR_OBJECT = BLUE
