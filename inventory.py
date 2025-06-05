# inventory.py
import pygame
from utils.constants import *

class Inventory:
    def __init__(self, game, owner, capacity=8):
        self.game = game
        self.owner = owner 
        self.capacity = capacity
        self.items = []
        self.selected_item_index = 0
        self.is_open = False

        # UI properties
        self.width = 350 
        self.height = 450
        self.x = (SCREEN_WIDTH - self.width) // 2
        self.y = (SCREEN_HEIGHT - self.height) // 2
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        self.font_title = pygame.font.Font(None, 36)
        self.font_item = pygame.font.Font(None, 24)
        self.font_desc = pygame.font.Font(None, 18)
        self.font_instructions = pygame.font.Font(None, 20)

        self.equipped_weapon = None
        self.equipped_armor = None

    def toggle_open(self):
        self.is_open = not self.is_open
        if self.is_open:
            if not self.items:
                self.selected_item_index = -1 # No hay nada que seleccionar
            elif self.selected_item_index == -1 and self.items: # Si estaba en -1 pero ahora hay items
                self.selected_item_index = 0
            elif self.selected_item_index >= len(self.items): # Si el índice quedó fuera de rango
                self.selected_item_index = len(self.items) -1
        return self.is_open

    def add_item(self, item):
        if len(self.items) < self.capacity:
            self.items.append(item)
            self.game.current_state.show_message(f"Recogiste: {item.name}")
            if len(self.items) == 1 or self.selected_item_index == -1 : # Si es el primer item o no había selección
                self.selected_item_index = 0
            return True
        else:
            self.game.current_state.show_message("Inventario lleno!")
            return False

    def remove_item(self, item_index):
        if 0 <= item_index < len(self.items):
            item = self.items.pop(item_index)
            if not self.items:
                self.selected_item_index = -1
            elif self.selected_item_index >= len(self.items):
                self.selected_item_index = len(self.items) - 1
            return item
        return None

    def get_selected_item(self):
        if self.items and 0 <= self.selected_item_index < len(self.items):
            return self.items[self.selected_item_index]
        return None

    def _equip_item(self, item):
        if item.item_type == "weapon":
            self.equipped_weapon = item
            self.owner.attack = self.owner.base_attack + item.damage_bonus
            self.game.current_state.show_message(f"Equipaste: {item.name} (+{item.damage_bonus} daño)")
        elif item.item_type == "armor":
            self.equipped_armor = item
            self.owner.defense = self.owner.base_defense + item.defense_bonus
            self.game.current_state.show_message(f"Equipaste: {item.name} (+{item.defense_bonus} defensa)")
        print(f"Jugador equipó {item.name}. Stats actualizados.")

    def _unequip_item(self, item_type):
        if item_type == "weapon" and self.equipped_weapon:
            self.game.current_state.show_message(f"Desequipaste: {self.equipped_weapon.name}")
            self.owner.attack = self.owner.base_attack
            self.equipped_weapon = None
        elif item_type == "armor" and self.equipped_armor:
            self.game.current_state.show_message(f"Desequipaste: {self.equipped_armor.name}")
            self.owner.defense = self.owner.base_defense
            self.equipped_armor = None
        print(f"Jugador desequipó {item_type}. Stats restaurados a base.")

    def use_selected_item(self):
        item = self.get_selected_item()
        if not item:
            return False 

        action_consumed_turn = False
        if item.item_type == "consumable":
            if item.use(self.owner): 
                self.remove_item(self.selected_item_index)
                action_consumed_turn = True 
        elif item.item_type in ["weapon", "armor"]:
            is_currently_equipped = (item.item_type == "weapon" and self.equipped_weapon == item) or \
                                  (item.item_type == "armor" and self.equipped_armor == item)

            if is_currently_equipped:
                self._unequip_item(item.item_type)
            else: 
                if item.item_type == "weapon" and self.equipped_weapon:
                    self._unequip_item("weapon") 
                elif item.item_type == "armor" and self.equipped_armor:
                    self._unequip_item("armor")
                self._equip_item(item)
            action_consumed_turn = False 
        return action_consumed_turn

    def handle_input(self, event):
        if not self.is_open:
            return False

        action_taken_consumes_turn = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                if self.items and self.selected_item_index > 0:
                    self.selected_item_index -= 1
                elif self.items and self.selected_item_index == -1 : # Si no había selección, ir al primero
                    self.selected_item_index = 0
            elif event.key == pygame.K_DOWN:
                if self.items and self.selected_item_index < len(self.items) - 1:
                    self.selected_item_index += 1
                elif self.items and self.selected_item_index == -1 : # Si no había selección, ir al primero
                    self.selected_item_index = 0
            elif event.key == pygame.K_RETURN: 
                if self.get_selected_item():
                    action_taken_consumes_turn = self.use_selected_item()
            elif event.key == pygame.K_i or event.key == pygame.K_ESCAPE:
                self.toggle_open()
        return action_taken_consumes_turn

    def draw(self, screen):
        if not self.is_open:
            return

        pygame.draw.rect(screen, GRAY, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 2) 

        title_surf = self.font_title.render("Inventario", True, BLACK)
        screen.blit(title_surf, (self.x + 10, self.y + 10))

        item_y_start = self.y + 50
        line_h = 25 
        desc_h = 18 
        spacing = 5

        for i, item in enumerate(self.items):
            text_color = YELLOW if i == self.selected_item_index else BLACK
            item_name_surf = self.font_item.render(f"{item.name} ({item.item_type})", True, text_color)
            current_y = item_y_start + i * (line_h + desc_h + spacing)
            screen.blit(item_name_surf, (self.x + 20, current_y))

            if i == self.selected_item_index:
                desc_surf = self.font_desc.render(item.description, True, DARK_GREEN)
                screen.blit(desc_surf, (self.x + 25, current_y + line_h))

                stat_text = ""
                if item.item_type == "weapon": stat_text = f"Daño: +{item.damage_bonus}"
                elif item.item_type == "armor": stat_text = f"Defensa: +{item.defense_bonus}"
                elif item.item_type == "consumable" and item.effect.get("heal"): stat_text = f"Cura: {item.effect['heal']} HP"
                
                if stat_text:
                    stat_surf = self.font_desc.render(stat_text, True, BLUE)
                    screen.blit(stat_surf, (self.x + self.width - 120, current_y + line_h // 2))

        stats_y_start = self.y + self.height - 120
        screen.blit(self.font_item.render(f"HP: {self.owner.current_hp}/{self.owner.max_hp}", True, BLACK), (self.x + 20, stats_y_start))
        screen.blit(self.font_item.render(f"Ataque: {self.owner.attack} (Base: {self.owner.base_attack})", True, BLACK), (self.x + 20, stats_y_start + 30))
        screen.blit(self.font_item.render(f"Defensa: {self.owner.defense} (Base: {self.owner.base_defense})", True, BLACK), (self.x + 20, stats_y_start + 60))

        equipped_x_start = self.x + self.width - 180 
        equipped_y_start = self.y + 50 
        screen.blit(self.font_item.render("Equipado:", True, BLACK), (equipped_x_start, equipped_y_start))
        weapon_name = self.equipped_weapon.name if self.equipped_weapon else "Nada"
        screen.blit(self.font_item.render(f"Arma: {weapon_name}", True, BLACK), (equipped_x_start, equipped_y_start + 25))
        armor_name = self.equipped_armor.name if self.equipped_armor else "Nada"
        screen.blit(self.font_item.render(f"Armadura: {armor_name}", True, BLACK), (equipped_x_start, equipped_y_start + 50))

        instructions_surf = self.font_instructions.render("Flechas: Mover, Enter: Usar/Equipar, I/ESC: Cerrar", True, BLACK)
        screen.blit(instructions_surf, (self.x + 10, self.y + self.height - 25))