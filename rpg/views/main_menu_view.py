# """
# Main Menu
# """
import arcade
import arcade.gui


class MainMenuView(arcade.View):
    """
    This class acts as the game view for the main menu screen and its buttons. Accessed by hitting ESC. That logic can be referenced in game_view.py
    """

    def __init__(self, background_texture = None):
        super().__init__()

        # --- Required for all code that uses UI element, a UIManager to handle the UI.
        self.manager = arcade.gui.UIManager()

        # Create a vertical BoxGroup to align buttons
        self.v_box = arcade.gui.UIBoxLayout()

        #Recuadro
        self.panel_texture = arcade.load_texture(":misc:recuadro.PNG")

        #Fondo
        self.background_texture = background_texture

        #Botón play
        self.play_normal = arcade.load_texture(":misc:play_normal.png")
        self.play_hover = arcade.load_texture(":misc:play_hover.png")

        #Botón settings
        self.settings_normal = arcade.load_texture(":misc:settings_normal.png")
        self.settings_hover = arcade.load_texture(":misc:settings_hover.png")

        #Botón new game
        self.new_game_normal = arcade.load_texture(":misc:new_game_normal.png")
        self.new_game_hover = arcade.load_texture(":misc:new_game_hover.png")

        #Botón exit
        self.exit_normal = arcade.load_texture(":misc:exit_normal.png")
        self.exit_hover = arcade.load_texture(":misc:exit_hover.png")

        play_button = arcade.gui.UITextureButton(texture=self.play_normal, texture_hovered=self.play_hover)
        self.v_box.add(play_button.with_space_around(bottom=10))
        play_button.on_click = self.on_click_resume

        settings_button = arcade.gui.UITextureButton(texture=self.settings_normal, texture_hovered=self.settings_hover)
        self.v_box.add(settings_button.with_space_around(bottom=10))
        settings_button.on_click = self.on_click_settings

        #OPCIÓN DESACTIVADA TEMPORALMENTE
        #battle_button = arcade.gui.UIFlatButton(text="Battle Screen", width=200)
        #self.v_box.add(battle_button.with_space_around(bottom=20))
        #battle_button.on_click = self.on_click_battle

        new_game_button = arcade.gui.UITextureButton(texture=self.new_game_normal, texture_hovered=self.new_game_hover)
        self.v_box.add(new_game_button.with_space_around(bottom=10))
        new_game_button.on_click = self.on_click_new_game

        exit_button = arcade.gui.UITextureButton(texture=self.exit_normal, texture_hovered=self.exit_hover)
        self.v_box.add(exit_button.with_space_around(bottom=20))
        exit_button.on_click = self.on_click_quit
        # Create a widget to hold the v_box widget, that will center the buttons
        self.manager.add(
            arcade.gui.UIAnchorWidget(
                anchor_x="center_x", anchor_y="center_y", align_y=-20, child=self.v_box
            )
        )

    def on_show_view(self):
        self.manager.enable()
        #arcade.set_background_color(arcade.color.ALMOND)

    def on_hide_view(self):
        self.manager.disable()

    def on_draw(self):
        """
        Method that redraws the UI buttons each time we call the pause menu. See game_view.py for more.
        input: None
        output: None
        """
        self.clear()

        if self.background_texture:
            arcade.draw_scaled_texture_rectangle(  #Se dibuja la captura de pantalla del juego como textura
                self.window.width // 2,
                self.window.height // 2,
                self.background_texture,
                scale=1.0
            )

        arcade.draw_lrtb_rectangle_filled(  #Se dibuja un overlay negro transparente
            0, self.window.width, self.window.height, 0, (0, 0, 0, 160)
        )

        arcade.draw_scaled_texture_rectangle(   #Se dibuja el recuadro del menú
            self.window.width // 2,
            self.window.height // 2,
            self.panel_texture,
            scale=1.0
        )
        self.manager.draw()

    # call back methods for buttons:
    def on_click_resume(self, event):
        print("show game view")
        self.window.show_view(self.window.views["game"])

    def on_click_settings(self, event):
        print("show settings view")
        self.window.show_view(self.window.views["settings"])

    # BATTLE SCREEN DESACTIVADO TEMPORALMENTE
    #def on_click_battle(self, event):
        #print("battle screen")
        #self.window.views["battle"].setup()
        #self.window.show_view(self.window.views["battle"])

    def on_click_new_game(self, event):
        print("restart game")
        self.window.views["game"].setup()
        self.window.show_view(self.window.views["game"])

    def on_click_quit(self, event):
        print("quitting")
        self.window.close()

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:
            print("show game view")
            self.window.show_view(self.window.views["game"])
