"""
Settings
"""
import arcade
import arcade.gui
import rpg.constants as constants
from rpg.constants import SCREEN_WIDTH, SCREEN_HEIGHT


class SettingsView(arcade.View):
    def __init__(self, background_texture = None):
        super().__init__()
        self.started = False

        # --- Required for all code that uses UI element, a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        # Fondo
        self.background_texture = background_texture

        # Recuadro
        self.panel_texture = arcade.load_texture(":misc:recuadro.PNG")

        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", align_y=-20, child=self.v_box
                # Align_y sirve para desplazar verticalmente TODOS los botones (positivo arriba, negativo abajo)
            )
        )

    def on_draw(self):
        arcade.start_render()
        self.clear()

        if self.background_texture:
            arcade.draw_scaled_texture_rectangle(  # Se dibuja la captura de pantalla del juego como textura
                self.window.width // 2,
                self.window.height // 2,
                self.background_texture,
                scale=1.0
            )

        arcade.draw_lrtb_rectangle_filled(  # Se dibuja un overlay negro transparente
            0, self.window.width, self.window.height, 0, (0, 0, 0, 160)
        )

        arcade.draw_scaled_texture_rectangle(  # Se dibuja el recuadro del menú
            self.window.width // 2,
            self.window.height // 2,
            self.panel_texture,
            scale=1.0
        )
        self.manager.draw()

    def setup(self):
        pass

    def on_show_view(self):
        self.manager.enable()
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.window.views["main_menu"])
