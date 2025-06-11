# motorcycle.py
class Motorcycle:
    def __init__(self, game):
        self.game = game
        self.fuel_max = 100.0  # Capacidad máxima de combustible
        self.fuel_current = 75.0 # Combustible actual (ejemplo)
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
