# player.py
import pygame
from utils.constants import *
from inventory import Inventory

class Player:
    def __init__(self, game, start_x, start_y):
        self.game = game
        self.x = start_x # Posición en coordenadas de tile
        self.y = start_y # Posición en coordenadas de tile
        self.color = ORANGE # Color para el placeholder del jugador (ya no usado si tienes imagen)
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.speed = PLAYER_SPEED # Velocidad de movimiento (en tiles por ahora)

        # Estadísticas base
        self.base_attack = 10
        self.base_defense = 5
        self.max_hp = 100
        self.current_hp = self.max_hp

        # Estadísticas actuales (afectadas por el equipo)
        self.attack = self.base_attack
        self.defense = self.base_defense

        # Inventario
        self.inventory = Inventory(self.game, self, capacity=10) # Crear instancia de Inventory

        # Habilidades y cooldowns
        self.cooldown_powerful_attack = 0 # Turnos restantes para el cooldown
        self.max_cooldown_powerful_attack = 5 # Cooldown de la habilidad (5 turnos)

        # Efectos de estado
        self.status_effects = {} # Diccionario: {"efecto_nombre": {"duration": X, "potency": Y}}

    
    def take_damage(self, damage):
        """Calcula el daño recibido y actualiza HP."""
        # Daño = Ataque_enemigo - Defensa_jugador (mínimo 1 de daño)
        actual_damage = max(1, damage - self.defense)
        self.current_hp -= actual_damage
        self.game.sound_hit.play() # Sonido de recibir daño
        print(f"¡Jugador recibió {actual_damage} de daño! HP restantes: {self.current_hp}/{self.max_hp}")
        if self.current_hp <= 0:
            print("¡Has sido derrotado!")
            self.game.sound_player_death.play() # Sonido de muerte del jugador
            return True # Jugador derrotado
        return False # Jugador no derrotado
    # --- Métodos de Combate (modificados para incluir habilidades) ---
    def attack_target(self, target_enemy, is_powerful_attack=False):
        """Ataca a un enemigo, con opción de ataque potente."""
        damage = self.attack
        if is_powerful_attack:
            if self.cooldown_powerful_attack > 0:
                self.game.current_state.show_message("Ataque Potente en cooldown!")
                return False # No se puede usar, no consume el turno

            damage *= 1.5 # 50% más de daño para el ataque potente
            self.cooldown_powerful_attack = self.max_cooldown_powerful_attack
            self.game.current_state.show_message(f"¡Lanzas un ATAQUE POTENTE! ({damage:.0f} daño)")
        else:
            self.game.current_state.show_message(f"Atacas al enemigo. ({damage} daño)")

        # Aplica la defensa del enemigo
        actual_damage = max(0, damage - target_enemy.defense)

        print(f"Player ataca a {target_enemy.enemy_type}. Daño base: {damage}, Daño real: {actual_damage}")

        enemy_defeated = target_enemy.take_damage(actual_damage)
        return enemy_defeated

    # --- Nuevo método para actualizar cooldowns y efectos de estado al final del turno ---
    def end_turn_update(self):
        """Actualiza cooldowns y duraciones de efectos de estado al final de cada turno del jugador."""
        if self.cooldown_powerful_attack > 0:
            self.cooldown_powerful_attack -= 1
            if self.cooldown_powerful_attack == 0:
                self.game.current_state.show_message("¡Ataque Potente listo!")

        # Aquí se manejarían otros efectos de estado del jugador (ej. envenenado, boost de ataque temporal)
        # Procesar efectos de estado
        effects_to_remove = []
        for effect_name, effect_data in list(self.status_effects.items()): # Usar list() para iterar mientras modificamos
            if effect_name == "poisoned":
                poison_damage = effect_data["potency"]
                self.current_hp -= poison_damage
                self.game.current_state.show_message(f"El veneno te daña {poison_damage} HP.")
                print(f"Jugador envenenado. HP: {self.current_hp}/{self.max_hp}")
                if self.current_hp <= 0:
                    self.game.current_state.show_message("¡Has sucumbido al veneno! GAME OVER")
                    self.game.request_state_change("game_over")
                    return # El jugador murió, no seguir procesando

            effect_data["duration"] -= 1
            if effect_data["duration"] <= 0:
                effects_to_remove.append(effect_name)
                self.game.current_state.show_message(f"El efecto '{effect_name}' ha terminado.")

        for effect_name in effects_to_remove:
            del self.status_effects[effect_name]

        # Asegurarse de que la HP no baje de 0 por veneno si no se pasa a game over
        self.current_hp = max(0, self.current_hp)
    
    def move(self, dx, dy, current_map):
        """Intenta mover al jugador en dx, dy."""
        new_x = self.x + dx
        new_y = self.y + dy

        # 1. Primero, verifica si el nuevo tile es caminable (paredes, abismos)
        if not current_map.is_walkable(new_x, new_y):
            return False # No es un tile caminable, no se mueve

        # 2. Luego, verifica si la nueva posición está ocupada por un obstáculo
        # Itera sobre los obstáculos del mapa
        for obstacle in current_map.obstacles:
            if obstacle.x == new_x and obstacle.y == new_y:
                print("¡Colisión con un obstáculo!")
                return False # Hay un obstáculo, no se mueve

        # Si el código llega aquí, la nueva posición es caminable y no hay obstáculos
        # Guardar el tipo de tile actual del jugador antes de moverse
        original_player_x, original_player_y = self.x, self.y

        # Actualiza la posición del jugador
        self.x = new_x
        self.y = new_y
        # Primero, verificamos si el nuevo tile es caminable
        if current_map.is_walkable(new_x, new_y):
            # Si el jugador se mueve desde la posición de entrada o salida (que ahora son paredes),
            # restaura el tile original a TILE_WALL.
            if current_map.tiles[original_player_x][original_player_y] == TILE_ENTRANCE or \
               current_map.tiles[original_player_x][original_player_y] == TILE_EXIT:
                # No cambiamos el tile de la entrada/salida a TILE_WALL inmediatamente,
                # ya que el jugador podría querer volver a entrar/salir si se implementa esa lógica.
                # Por ahora, simplemente nos movemos. El tile de entrada/salida permanece.
                pass

            self.game.sound_move.play() # Sonido de movimiento del jugador

            # Actualiza la posición del jugador
            self.x = new_x
            self.y = new_y

            # Si el jugador llega a la salida, haz algo (por ejemplo, print)
            if current_map.tiles[self.x][self.y] == TILE_EXIT:
                print("¡Has llegado a la salida!")
                self.game.current_state.show_message("¡Has llegado a la salida!")
                self.game.request_state_change("victory")            
            
            return True

    def get_rect(self):
        """Devuelve el rectángulo de posición del jugador en coordenadas del mundo."""
        return pygame.Rect(self.x * TILE_SIZE, self.y * TILE_SIZE, self.width, self.height)


    def draw(self, screen, camera):
        # Dibuja el jugador, aplicando el desplazamiento de la cámara
        screen.blit(self.game.player_image, camera.apply(self.get_rect()))
       
    
    # --- Nuevo método para aplicar efectos de estado ---
    def apply_effect(self, effect_name, duration, potency=0):
        self.status_effects[effect_name] = {"duration": duration, "potency": potency}
        print(f"Efecto de estado '{effect_name}' aplicado al jugador. Duración: {duration}, Potencia: {potency}")
