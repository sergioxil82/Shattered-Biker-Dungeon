# motorcycle.py
class Motorcycle:
    def __init__(self, game):
        self.game = game
        self.fuel_max = 100.0  # Capacidad máxima de combustible
        self.fuel_current = 75.0 # Combustible actual (ejemplo)
        self.max_hp = 150.0 # HP máximo de la moto
        self.current_hp = 100.0 # HP actual de la moto
        # ... otros atributos como estado, velocidad, etc.

    def consume_fuel(self, amount):
        self.fuel_current -= amount
        if self.fuel_current < 0:
            self.fuel_current = 0

    def refuel(self, amount):
        self.fuel_current += amount
        if self.fuel_current > self.fuel_max:
            self.fuel_current = self.fuel_max
        print(f"Moto reabastecida. Combustible actual: {self.fuel_current}/{self.fuel_max}")
    
    def take_damage(self, amount):
        self.current_hp -= amount
        if self.current_hp < 0:
            self.current_hp = 0
        print(f"Moto recibió {amount} de daño. HP actual: {self.current_hp}/{self.max_hp}")
        # Aquí podrías añadir lógica para cuando la moto se destruye

    def repair(self, amount):
        self.current_hp += amount
        if self.current_hp > self.max_hp:
            self.current_hp = self.max_hp
        print(f"Moto reparada. HP actual: {self.current_hp}/{self.max_hp}")

