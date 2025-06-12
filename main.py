import pygame
import sys
import json
from utils.constants import *
from game_states import MenuState, PlayingState, GameOverState, VictoryState, TransitionState  # Importa las clases de estado

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(SCREEN_TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.config = self.load_config()

        # Diccionario para almacenar las imágenes de los tiles por su tipo
        self.tile_images = {}

         # --- Carga de Assets ---
        self.load_assets() # Llama al método para cargar imágenes

        # Estado del juego 
        self.current_state = None
        self.target_level_number = 1 # Nivel a cargar la próxima vez que se entre a PlayingState
        self.change_state(MenuState(self)) # Inicializa el juego con el estado de menú
    

    def load_config(self):
        """Carga la configuración desde config.json."""
        try:
            with open("config.json", 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print("Advertencia: config.json no encontrado. Usando valores por defecto.")
            return {"fov_enabled": True} # Valores por defecto si el archivo no existe
        
    def load_assets(self):
        """Carga todas las imágenes, sonidos, etc. del juego."""
        try:
            # Carga la imagen del jugador
            # .convert_alpha() es importante para imágenes con transparencia
            self.player_image = pygame.image.load("assets/sprites/player_biker.png").convert_alpha()
            if self.player_image.get_width() != TILE_SIZE or self.player_image.get_height() != TILE_SIZE:
                 self.player_image = pygame.transform.scale(self.player_image, (TILE_SIZE, TILE_SIZE))

            # --- Carga de imágenes de tiles ---
            # Asocia cada tipo de tile (constante) con la ruta de su imagen
            tile_paths = {
                TILE_ROAD: "assets/tiles/road.png",
                TILE_WALL: "assets/tiles/wall.png",
                #TILE_ABYSS: "assets/tiles/abyss.png", # Puedes usar una imagen negra
                TILE_ENTRANCE: "assets/tiles/entrance.png",
                TILE_EXIT: "assets/tiles/exit.png",
                # Añade aquí otros tiles si los tienes, como TILE_GARAGE_FLOOR
                TILE_GARAGE_FLOOR: "assets/tiles/garage_floor.png",
                TILE_OBJECT: "assets/tiles/obstacle.png"
            }
           
            self.welcome_image = pygame.image.load("assets/screens/welcome.png").convert_alpha() 
            if self.welcome_image.get_width() != SCREEN_WIDTH or self.welcome_image.get_height() != SCREEN_HEIGHT:
                self.welcome_image = pygame.transform.scale(self.welcome_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.victory_image = pygame.image.load("assets/screens/victory.png").convert_alpha()  
            if self.victory_image.get_width() != SCREEN_WIDTH or self.victory_image.get_height() != SCREEN_HEIGHT:
                self.victory_image = pygame.transform.scale(self.victory_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.game_over_image = pygame.image.load("assets/screens/game_over.png").convert_alpha()
            if self.game_over_image.get_width() != SCREEN_WIDTH or self.game_over_image.get_height() != SCREEN_HEIGHT:
                self.game_over_image = pygame.transform.scale(self.game_over_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

            # --- Cargar imagen para la pantalla de transición ---
            self.transition_screen_image = pygame.image.load("assets/screens/transition_road.png").convert() # O .convert_alpha()
            if self.transition_screen_image.get_width() != SCREEN_WIDTH or self.transition_screen_image.get_height() != SCREEN_HEIGHT:
                self.transition_screen_image = pygame.transform.scale(self.transition_screen_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

            for tile_type, path in tile_paths.items():
                image = pygame.image.load(path).convert_alpha() # .convert_alpha() para transparencia
                # Asegúrate de que la imagen del tile tenga el tamaño correcto
                if image.get_width() != TILE_SIZE or image.get_height() != TILE_SIZE:
                    image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
                self.tile_images[tile_type] = image

            # --- Carga de imágenes de obstáculos ---
            # Si los obstáculos son solo un color, no necesitas imagen.
            # Pero si quieres un sprite para ellos:
            self.obstacle_image = pygame.image.load("assets/tiles/obstacle.png").convert_alpha()
            if self.obstacle_image.get_width() != TILE_SIZE:
                self.obstacle_image = pygame.transform.scale(self.obstacle_image, (TILE_SIZE, TILE_SIZE))

            # Carga la imagen del enemigo genérico
            self.enemy_image = pygame.image.load("assets/sprites/enemy_basic.png").convert_alpha() # Asegúrate de tener esta imagen
            if self.enemy_image.get_width() != TILE_SIZE:
                self.enemy_image = pygame.transform.scale(self.enemy_image, (TILE_SIZE, TILE_SIZE))

            # Carga la imagen para el Heavy Hitter
            self.heavy_hitter_image = pygame.image.load("assets/sprites/enemy_heavy.png").convert_alpha() # Necesitas esta imagen
            if self.heavy_hitter_image.get_width() != TILE_SIZE:
                self.heavy_hitter_image = pygame.transform.scale(self.heavy_hitter_image, (TILE_SIZE, TILE_SIZE))

            # Carga la imagen para el Acid Spitter
            self.acid_spitter_image = pygame.image.load("assets/sprites/enemy_biker.png").convert_alpha() # Necesitas esta imagen
            if self.acid_spitter_image.get_width() != TILE_SIZE:
                self.acid_spitter_image = pygame.transform.scale(self.acid_spitter_image, (TILE_SIZE, TILE_SIZE))

            # --- Carga de imágenes de pickups ---
            self.pickup_health_image = pygame.image.load("assets/sprites/health_potion.png").convert_alpha()
            if self.pickup_health_image.get_width() != TILE_SIZE:
                self.pickup_health_image = pygame.transform.scale(self.pickup_health_image, (TILE_SIZE, TILE_SIZE))
            # self.pickup_attack_image = pygame.image.load("assets/sprites/attack_boost.png").convert_alpha()
            # if self.pickup_attack_image.get_width() != TILE_SIZE:
            #     self.pickup_attack_image = pygame.transform.scale(self.pickup_attack_image, (TILE_SIZE, TILE_SIZE))

            # --- Carga de Fuentes ---
            pygame.font.init() # Inicializa el módulo de fuentes de Pygame si no lo está
            self.font = pygame.font.Font(None, 24) # Fuente principal (tamaño 24)
            self.font_small = pygame.font.Font(None, 18) # Fuente más pequeña (tamaño 18) para instrucciones, etc.

            # --- Carga de sonidos ---
            self.sound_attack = pygame.mixer.Sound("assets/sounds/attack.wav")
            self.sound_hit = pygame.mixer.Sound("assets/sounds/hit.wav") # Sonido de recibir daño
            self.sound_player_death = pygame.mixer.Sound("assets/sounds/player_death.wav")
            self.sound_enemy_death = pygame.mixer.Sound("assets/sounds/enemy_death.wav")
            self.sound_move = pygame.mixer.Sound("assets/sounds/move.wav") # Sonido de movimiento.
            self.sound_pickup = pygame.mixer.Sound("assets/sounds/pickup.wav")


            print("Assets cargados correctamente.")

        except pygame.error as e:
            print(f"Error al cargar asset: {e}")            
            pygame.quit()
            sys.exit() # Detiene el juego si los assets no se cargan
            
    def change_state(self, new_state):
        """Cambia el estado actual del juego."""
        if self.current_state:
            self.current_state.exit_state() # Llama al método de salida del estado actual
        self.current_state = new_state
        self.current_state.enter_state() # Llama al método de entrada del nuevo estado

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            # Delega el manejo de entrada al estado actual
            self.current_state.handle_input(event)

            # Aquí añadiremos la lógica para manejar el teclado, ratón, etc.
            # Por ejemplo, para el movimiento del jugador, interacciones.

    def update(self):
        # Aquí se actualizará la lógica del juego:
        # - Movimiento de personajes
        # - Lógica de combate
        # - Actualización de objetos
        # - Generación de niveles (si es necesario en tiempo real)
        # - Manejo de estados del juego (menú, jugando, etc.)
        # Lógica de actualización según el estado del juego
        dt = self.clock.get_time() / 1000.0 # Delta time en segundos
        # Delega la actualización al estado actual
        self.current_state.update(dt)

    def draw(self):
        # Delega el dibujo al estado actual
        self.current_state.draw(self.screen)
        pygame.display.flip()        

    def run(self):
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
    
    def request_state_change(self, new_state_name):
        """
        Solicita un cambio de estado del juego.
        Este método centraliza los cambios de estado para evitar importaciones circulares.
        """
        if new_state_name == "menu":
            self.change_state(MenuState(self))
        elif new_state_name == "playing":
            self.change_state(PlayingState(self))
        elif new_state_name == "game_over":
            self.change_state(GameOverState(self))
        elif new_state_name == "victory":
            self.change_state(VictoryState(self))
        elif new_state_name == "transition":
            # TransitionState necesita saber a qué nivel va           
            if isinstance(self.current_state, PlayingState):
                # Preparamos el siguiente nivel para cuando volvamos a PlayingState
                self.target_level_number = self.current_state.current_level_number + 1
                self.change_state(TransitionState(self, self.target_level_number))
            else: # No debería ocurrir desde otro estado que no sea Playing
                self.target_level_number = 1
                self.change_state(TransitionState(self, self.target_level_number))
        else:
            print(f"Error: Estado '{new_state_name}' desconocido.")

if __name__ == "__main__":
    game = Game()
    game.run()