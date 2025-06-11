# hud.py
import pygame
from utils.constants import *

class HUD:
    def __init__(self, game, player, motorcycle=None):
        self.game = game
        self.player = player
        self.motorcycle = motorcycle # La motocicleta del jugador, puede ser None

        # Propiedades del medidor de combustible
        self.fuel_gauge_width = 20
        self.fuel_gauge_height = 100
        self.fuel_gauge_x = SCREEN_WIDTH - self.fuel_gauge_width - 30 # Margen derecho
        self.fuel_gauge_y = 10 # Margen superior
        self.num_fuel_bars = 10 # Número de rayitas en el medidor

    def update_motorcycle(self, motorcycle):
        """Actualiza la referencia a la motocicleta si cambia (ej. el jugador monta/desmonta)"""
        self.motorcycle = motorcycle

    def draw(self, screen):
        """Dibuja toda la interfaz de usuario (HUD) en la pantalla."""
        # --- Barra de vida del Jugador ---
        hp_bar_width = 150
        hp_bar_height = 20
        hp_bar_x = 10
        hp_bar_y = 10

        hp_percentage = 0
        if self.player.max_hp > 0: # Evitar división por cero si max_hp es 0
            hp_percentage = self.player.current_hp / self.player.max_hp

        if hp_percentage > 0.6:
            hp_color = GREEN
        elif hp_percentage > 0.25:
            hp_color = YELLOW
        else:
            hp_color = RED

        pygame.draw.rect(screen, hp_color, (hp_bar_x, hp_bar_y, hp_bar_width * hp_percentage, hp_bar_height))
        pygame.draw.rect(screen, WHITE, (hp_bar_x, hp_bar_y, hp_bar_width, hp_bar_height), 2)

        hp_text = self.game.font.render(f"HP: {self.player.current_hp}/{self.player.max_hp}", True, WHITE)
        screen.blit(hp_text, (hp_bar_x + hp_bar_width + 10, hp_bar_y))

        # --- Ataque y Defensa del Jugador ---
        attack_text = self.game.font.render(f"Ataque: {self.player.attack}", True, WHITE)
        defense_text = self.game.font.render(f"Defensa: {self.player.defense}", True, WHITE)
        screen.blit(attack_text, (10, hp_bar_y + hp_bar_height + 10))
        screen.blit(defense_text, (10, hp_bar_y + hp_bar_height + 40))

        # --- Cooldown de Habilidad del Jugador ---
        skill_cooldown_text = self.game.font.render(
            f"Ataque Potente CD: {self.player.cooldown_powerful_attack}",
            True, WHITE if self.player.cooldown_powerful_attack == 0 else YELLOW
        )
        screen.blit(skill_cooldown_text, (10, SCREEN_HEIGHT - 60))

        try:
            skill_inst_text = self.game.font_small.render("S: Ataque Potente", True, WHITE)
        except AttributeError:
            skill_inst_text = self.game.font.render("S: Ataque Potente", True, WHITE)
        screen.blit(skill_inst_text, (10, SCREEN_HEIGHT - 30))

        # --- Efectos de Estado del Jugador ---
        y_offset_effects = SCREEN_HEIGHT - 90
        for effect_name, effect_data in self.player.status_effects.items():
            effect_text = self.game.font.render(
                f"{effect_name.title()} ({effect_data['duration']}t)",
                True, YELLOW if effect_name == "poisoned" else WHITE
            )
            screen.blit(effect_text, (SCREEN_WIDTH - effect_text.get_width() - 10, y_offset_effects))
            y_offset_effects -= 25

        # --- Medidor de Combustible de la Motocicleta ---
        if self.motorcycle: # Solo dibujar si hay una motocicleta
            # Fondo y borde del medidor
            gauge_rect = pygame.Rect(self.fuel_gauge_x, self.fuel_gauge_y, self.fuel_gauge_width, self.fuel_gauge_height)
            pygame.draw.rect(screen, COLOR_FUEL_BACKGROUND, gauge_rect)
            pygame.draw.rect(screen, COLOR_FUEL_BORDER, gauge_rect, 2) # Borde de 2px

            # Etiquetas "F" y "E"
            font_fuel = self.game.font_small # O un font específico si lo tienes
            f_text = font_fuel.render("F", True, COLOR_FUEL_BORDER)
            e_text = font_fuel.render("E", True, COLOR_FUEL_BORDER)
            screen.blit(f_text, (self.fuel_gauge_x + self.fuel_gauge_width / 2 - f_text.get_width() / 2, self.fuel_gauge_y - f_text.get_height() - 2))
            screen.blit(e_text, (self.fuel_gauge_x + self.fuel_gauge_width / 2 - e_text.get_width() / 2, self.fuel_gauge_y + self.fuel_gauge_height + 2))

            # Barras de combustible
            bar_height = (self.fuel_gauge_height - 4) / self.num_fuel_bars # -4 para un pequeño padding interno
            bar_width_inner = self.fuel_gauge_width - 4 # -4 para padding interno

            fuel_percentage = 0
            if self.motorcycle.fuel_max > 0:
                 fuel_percentage = self.motorcycle.fuel_current / self.motorcycle.fuel_max

            num_bars_to_show = int(fuel_percentage * self.num_fuel_bars)

            for i in range(self.num_fuel_bars):
                if i < num_bars_to_show:
                    # Determinar color de la barra
                    bar_color = COLOR_FUEL_FULL # Azul por defecto
                    # La barra más baja (índice 0) es la última en encenderse al llenar, primera en apagarse al vaciar
                    # Las barras se dibujan de abajo hacia arriba en términos de índice (0 es la más baja)
                    # pero visualmente se llenan de abajo hacia arriba.
                    
                    # Si la barra actual es la última visible (más baja) y el combustible es crítico
                    if i == 0: 
                        bar_color = COLOR_FUEL_EMPTY
                    elif i == 1:
                        bar_color = COLOR_FUEL_LOW
                    
                    # Posición Y de la barra (se dibujan de arriba hacia abajo en la pantalla)
                    # La barra '0' está en la parte inferior del medidor visualmente.
                    bar_y = self.fuel_gauge_y + 2 + (self.num_fuel_bars - 1 - i) * bar_height
                    bar_rect = pygame.Rect(self.fuel_gauge_x + 2, bar_y, bar_width_inner, bar_height -1) # -1 para espaciado
                    pygame.draw.rect(screen, bar_color, bar_rect)