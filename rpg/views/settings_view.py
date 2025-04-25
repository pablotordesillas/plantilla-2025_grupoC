"""
Settings
"""
import arcade
import rpg.constants as constants


class SettingsView(arcade.View):
    def __init__(self, background_texture = None):
        super().__init__()
        self.started = False
        # Fondo
        self.background_texture = background_texture
        # Recuadro
        self.panel_texture = arcade.load_texture(":misc:recuadro.PNG")

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

    def setup(self):
        pass

    def on_show_view(self):
        arcade.set_background_color(arcade.color.ALMOND)
        arcade.set_viewport(0, self.window.width, 0, self.window.height)

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.ESCAPE:
            self.window.show_view(self.window.views["main_menu"])
