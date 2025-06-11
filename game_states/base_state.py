# game_states/base_state.py

class GameState:
    def __init__(self, game):
        self.game = game # Referencia a la instancia principal del juego

    def handle_input(self, event):
        """Maneja los eventos de entrada para este estado."""
        pass

    def update(self, dt):
        """Actualiza la lógica del juego para este estado.
        dt es el tiempo transcurrido desde el último frame (delta time), útil para movimientos suaves.
        """
        pass

    def draw(self, screen):
        """Dibuja los elementos en la pantalla para este estado."""
        pass

    def enter_state(self):
        """Método llamado cuando se entra en este estado."""
        pass

    def exit_state(self):
        """Método llamado cuando se sale de este estado."""
        pass