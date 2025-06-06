"""
Loading screen
"""
import arcade
from rpg.draw_bar import draw_bar
from rpg.load_game_map import load_maps
from rpg.views.game_view import GameView
from rpg.views.main_menu_view import MainMenuView
from rpg.views.settings_view import SettingsView
from rpg.message_box import MessageBox
from rpg.constants import ContadorIni
import random
import threading

class LoadingView(arcade.View):
    def __init__(self):
        super().__init__()
        self.started = False
        self.progress = 0
        self.map_list = None
        self.background = arcade.load_texture(":misc:loading_screen.png")
        self.loading_text_texture = arcade.load_texture(":misc:loading_text.png")
        arcade.set_background_color(arcade.color.BLACK_OLIVE)
        self.message_box = None
        self.messages_list = ["Press 'I' to open the tips menu!", "Watch out for traps!", "Don't forget to vibe to the songs from time to time!", "Use 1-4 to change helmets, they make funny sounds!" ]

    def on_draw(self):
        arcade.start_render()
        self.started = True
        #Se dibuja la imagen de la pantalla de carga
        arcade.draw_lrwh_rectangle_textured((self.window.width - self.background.width) / 2,(self.window.height - self.background.height) / 2, self.background.width, self.background.height, self.background)
        #Barra de carga
        draw_bar(
            current_amount=self.progress,
            max_amount=100,
            center_x=self.window.width / 2,
            center_y=120,
            width=400,
            height=40,
            color_a=arcade.color.BLACK,
            color_b=arcade.color.WHITE,
        )
        #Borde alrededor de la barra de carga
        arcade.draw_rectangle_outline(center_x= self.window.width/2, center_y = 120, width=400, height = 40, color=arcade.color.BISTRE, border_width=10)
        #Texto loading
        arcade.draw_texture_rectangle(self.window.width/2, 180, self.loading_text_texture.width, self.loading_text_texture.height, self.loading_text_texture)

        if self.message_box:
            self.message_box.on_draw()

    def setup(self):
        self.background = arcade.load_texture(":misc:loading_screen.png")
        self.loading_text_texture = arcade.load_texture(":misc:loading_text.png")
    def close_message_box(self):
        self.message_box = None

    def on_update(self, delta_time: float):
        # Dictionary to hold all our maps
        global ContadorIni
        if self.started:
            done, self.progress, self.map_list = load_maps()
            if ContadorIni//7 > 3:
                ContadorIni = 0
            self.message_box = MessageBox(self, self.messages_list[ContadorIni//7], 2)
            ContadorIni +=1
            threading.Timer(delta_time*2, self.close_message_box).start()
            if done:
                self.window.views["game"] = GameView(self.map_list)
                self.window.views["game"].setup()
                #self.window.views["inventory"] = InventoryView()
                #self.window.views["inventory"].setup()
                self.window.views["main_menu"] = MainMenuView()
                self.window.views["settings"] = SettingsView()
                self.window.views["settings"].setup()
                #self.window.views["battle"] = BattleView()
                #self.window.views["battle"].setup()

                self.window.show_view(self.window.views["game"])


