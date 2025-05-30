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

    def use(self, player):
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

    def equip(self, player):
        """Equipa esta arma al jugador."""
        player.equipped_weapon = self # Asigna esta arma al jugador
        player.attack = player.base_attack + self.damage_bonus # Actualiza el ataque del jugador
        self.game.current_state.show_message(f"Equipaste {self.name} (+{self.damage_bonus} daño)!")
        print(f"Jugador equipó {self.name}. Nuevo ataque: {player.attack}")
        return True # El equipamiento no consume el turno

class Armor(Item):
    def __init__(self, game, name, description, defense_bonus, image_path):
        super().__init__(game, name, description, "armor", image_path)
        self.defense_bonus = defense_bonus # Bono de defensa que proporciona esta armadura

    def equip(self, player):
        """Equipa esta armadura al jugador."""
        player.equipped_armor = self # Asigna esta armadura al jugador
        player.defense = player.base_defense + self.defense_bonus # Actualiza la defensa del jugador
        self.game.current_state.show_message(f"Equipaste {self.name} (+{self.defense_bonus} defensa)!")
        print(f"Jugador equipó {self.name}. Nueva defensa: {player.defense}")
        return True # El equipamiento no consume el turno

class Consumable(Item):
    def __init__(self, game, name, description, effect, image_path):
        super().__init__(game, name, description, "consumable", image_path)
        self.effect = effect # Un diccionario o función para el efecto (ej. {"heal": 20})

    def use(self, player):
        """Usa este consumible y aplica su efecto."""
        if self.effect.get("heal"):
            heal_amount = self.effect["heal"]
            player.current_hp = min(player.max_hp, player.current_hp + heal_amount)
            self.game.current_state.show_message(f"¡Te curas {heal_amount} HP!")
            print(f"Jugador se curó. HP: {player.current_hp}/{player.max_hp}")
            self.game.sound_pickup.play() # Reusar el sonido de pickup para curar

        # Aquí puedes añadir más efectos de consumibles
        # if self.effect.get("attack_boost"):
        #     player.attack += self.effect["attack_boost"]
        #     self.game.current_state.show_message("¡Ataque Aumentado!")

        return True # El uso de un consumible generalmente consume el turno