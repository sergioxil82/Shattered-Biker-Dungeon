# item.py
import pygame
from utils.constants import *

class Item:
    def __init__(self, game, name, description, item_type, image_path):
        self.game = game
        self.name = name
        self.description = description
        self.item_type = item_type # Ej: "weapon", "armor", "consumable"

        self.image = None
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
            if self.image.get_width() != TILE_SIZE: # Escalar si es necesario
                self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            print(f"Error cargando imagen para ítem {name} en {image_path}. Usando placeholder.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(PURPLE) # Un color de placeholder

    def use(self, player, motorcycle=None):
        """Método placeholder. Las subclases implementarán su propia lógica."""
        print(f"Usando {self.name}...")
        self.game.current_state.show_message(f"Usas el {self.name}!")
        return False # Retorna False si el uso no consume el turno

    def __str__(self):
        return self.name

class Weapon(Item):
    def __init__(self, game, name, description, damage_bonus, image_path):
        super().__init__(game, name, description, "weapon", image_path)
        self.damage_bonus = damage_bonus # Bono de daño que proporciona esta arma
    

class Armor(Item):
    def __init__(self, game, name, description, defense_bonus, image_path):
        super().__init__(game, name, description, "armor", image_path)
        self.defense_bonus = defense_bonus # Bono de defensa que proporciona esta armadura
   

class Consumable(Item):
    def __init__(self, game, name, description, effect, image_path):
        super().__init__(game, name, description, "consumable", image_path)
        self.effect = effect # Un diccionario o función para el efecto (ej. {"heal": 20})

    def use(self, player, motorcycle=None):
        """Usa este consumible y aplica su efecto."""
        if self.effect.get("heal"):
            heal_amount = self.effect["heal"]
            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
            self.game.current_state.show_message(f"¡Te curas {heal_amount} HP!")
            print(f"Jugador se curó. HP: {player.current_hp}/{player.max_hp}")
            self.game.sound_pickup.play() # Reusar el sonido de pickup para curar

        elif self.effect.get("refuel") and motorcycle: # Comprobar que motorcycle no sea None
            refuel_amount = self.effect["refuel"]
            motorcycle.refuel(refuel_amount)
            self.game.current_state.show_message(f"¡Moto reabastecida +{refuel_amount} comb.!")
            print(f"Moto reabastecida. Combustible: {motorcycle.fuel_current}/{motorcycle.fuel_max}")
            # Podrías añadir un sonido específico para reabastecer

        elif self.effect.get("repair_moto") and motorcycle: # Comprobar que motorcycle no sea None
            repair_amount = self.effect["repair_moto"]
            motorcycle.repair(repair_amount)
            self.game.current_state.show_message(f"¡Moto reparada +{repair_amount} comb.!")
            print(f"Moto reaprada. Estado: {motorcycle.current_hp}/{motorcycle.max_hp}")

        return True # El uso de un consumible generalmente consume el turno