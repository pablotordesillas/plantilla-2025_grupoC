"""
Main game view
"""

import json
import time
from functools import partial
from typing import Callable
import pyglet
import arcade
import arcade.gui
import rpg.constants as constants
from arcade.experimental.lights import Light
from pyglet.math import Vec2

from rpg.constants import SPEED_AUX
from rpg.message_box import MessageBox
from rpg.sprites.chacter_sprite1 import CharacterSprite_one
from rpg.sprites.character_sprite import CharacterSprite
from rpg.sprites.player_sprite import PlayerSprite
import threading

from rpg.views.main_menu_view import MainMenuView
from rpg.views.settings_view import SettingsView

class DebugMenu(arcade.gui.UIBorder, arcade.gui.UIWindowLikeMixin):
    def __init__(
        self,
        *,
        width: float,
        height: float,
        noclip_callback: Callable,
        hyper_callback: Callable,
    ):
        constants.SONIDO=0
        reproducir_musica_fondo()
        self.off_style = {
            "bg_color": arcade.color.BLACK,
        }

        self.on_style = {
            "bg_color": arcade.color.REDWOOD,
        }

        self.setup_noclip(noclip_callback)
        self.setup_hyper(hyper_callback)

        space = 10

        self._title = arcade.gui.UITextArea(
            text="DEBUG MENU",
            width=width - space,
            height=height - space,
            font_size=14,
            text_color=arcade.color.BLACK,
        )

        group = arcade.gui.UIPadding(
            bg_color=(255, 255, 255, 255),
            child=arcade.gui.UILayout(
                width=width,
                height=height,
                children=[
                    arcade.gui.UIAnchorWidget(
                        child=self._title,
                        anchor_x="left",
                        anchor_y="top",
                        align_x=10,
                        align_y=-10,
                    ),
                    arcade.gui.UIAnchorWidget(
                        child=arcade.gui.UIBoxLayout(
                            x=0,
                            y=0,
                            children=[
                                arcade.gui.UIPadding(
                                    child=self.noclip_button, pading=(5, 5, 5, 5)
                                ),
                                arcade.gui.UIPadding(
                                    child=self.hyper_button, padding=(5, 5, 5, 5)
                                ),
                            ],
                            vertical=False,
                        ),
                        anchor_x="left",
                        anchor_y="bottom",
                        align_x=5,
                    ),
                ],
            ),
        )

        # x and y don't seem to actually change where this is created. bug?
        # TODO: make this not appear at the complete bottom left (top left would be better?)
        super().__init__(border_width=5, child=group)

    def setup_noclip(self, callback: Callable):
        # disable player collision

        def toggle(*args):
            # toggle state on click
            self.noclip_status = True if not self.noclip_status else False
            self.noclip_button._style = (
                self.off_style if not self.noclip_status else self.on_style
            )
            self.noclip_button.clear()

            callback(status=self.noclip_status)

        self.noclip_status = False
        self.noclip_button = arcade.gui.UIFlatButton(
            text="noclip", style=self.off_style
        )
        self.noclip_button.on_click = toggle  # type: ignore

    def setup_hyper(self, callback: Callable):
        # increase player speed

        def toggle(*args):
            # toggle state on click
            self.hyper_status = True if not self.hyper_status else False
            self.hyper_button._style = (
                self.off_style if not self.hyper_status else self.on_style
            )
            self.hyper_button.clear()

            callback(status=self.hyper_status)

        self.hyper_status = False

        self.hyper_button = arcade.gui.UIFlatButton(text="hyper", style=self.off_style)
        self.hyper_button.on_click = toggle  # type: ignore


class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self, map_list):
        super().__init__()

        self.contadorB = 0
        self.clock_sprite = None
        self.y_guardado = None # Posicion guardada en la que se incio el temporizador
        self.x_guardado = None # Posicion guardada en la que se incio el temporizador
        self.mapa_guardado = None # Mapa guardado en el que se inicio el temporizador
        arcade.set_background_color(arcade.color.AMAZON)
        self.setup_debug_menu()

        self.ui_manager = arcade.gui.UIManager()
        self.ui_manager.enable()

        # Player sprite
        self.player_sprite = None
        self.player_sprite_list = None
        #PRUEBA
        self.smoke_list = arcade.SpriteList() #Lista para la estela del dash
        self.cooldown1 = False
        self.smokes_list = arcade.SpriteList()
        self.humo_activo = False
        self.dash_timer = 0  # Temporizador para la duración del dash
        self.dash_duration = 0.2

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        #Teclas space y shift (dash y correr)
        self.space_pressed = False
        self.shift_pressed = False
        #PRUEBA
        self.tab_pressed = False
        self.dash = False
        self.correr = False
        self.embestir = False
        self.casco_verde = False
        self.casco_azul = False
        self.casco_vikingo = False

        self.total_time = 30.0 # Tiempo (segundos) del temporizador
        self.output = "00:00:00"
        self.show_timer = False


        # Physics engine
        self.physics_engine = None

        # Maps
        self.map_list = map_list

        # Name of map we are on
        self.cur_map_name = None

        self.message_box = None

        # Selected Items Hotbar
        #self.hotbar_sprite_list = None
        #self.selected_item = 1

        f = open("../resources/data/item_dictionary.json")
        self.item_dictionary = json.load(f)

        f = open("../resources/data/characters_dictionary.json")
        self.enemy_dictionary = json.load(f)

        # Cameras
        self.camera_sprites = arcade.Camera(self.window.width, self.window.height)
        self.camera_gui = arcade.Camera(self.window.width, self.window.height)

        # Create a small white light
        x = 100
        y = 200
        radius = 150
        mode = "soft"
        color = arcade.csscolor.WHITE
        self.player_light = Light(x, y, radius, color, mode)

    #PRUEBA
        #Cooldown para el dash
        self.cooldown = False


    def switch_map(self, map_name, start_x, start_y):
        """
        Switch the current map
        :param map_name: Name of map to switch to
        :param start_x: Grid x location to spawn at
        :param start_y: Grid y location to spawn at
        """
        self.cur_map_name = map_name
        try:
            self.my_map = self.map_list[self.cur_map_name]
        except KeyError:
            raise KeyError(f"Unable to find map named '{map_name}'.")

        if self.my_map.background_color:
            arcade.set_background_color(self.my_map.background_color)

        map_height = self.my_map.map_size[1]
        self.player_sprite.center_x = (
            start_x * constants.SPRITE_SIZE + constants.SPRITE_SIZE / 2
        )
        self.player_sprite.center_y = (
            map_height - start_y
        ) * constants.SPRITE_SIZE - constants.SPRITE_SIZE / 2
        self.scroll_to_player(1.0)
        self.player_sprite_list = arcade.SpriteList()
        self.player_sprite_list.append(self.player_sprite)

        self.setup_physics()
        if self.my_map.light_layer:
            self.my_map.light_layer.resize(self.window.width, self.window.height)

    def setup_physics(self):
        if self.noclip_status:
            # make an empty sprite list so the character does not collide with anything
            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player_sprite, arcade.SpriteList()
            )
        else:
            # use the walls as normal
            self.physics_engine = arcade.PhysicsEngineSimple(
                self.player_sprite, self.my_map.scene["wall_list"]
            )

    def setup(self):
        """Set up the game variables. Call to re-start the game."""

        # Crea la sprite del jugador, junto a sus spritesheets adicionales que usará
        self.player_sprite = PlayerSprite(":characters:Male/Player-1.png",":characters:Male/Player-2.png", ":characters:Male/Player-3.png", ":characters:Male/Player-4.png")
        # Spawn the player
        start_x = constants.STARTING_X
        start_y = constants.STARTING_Y
        self.switch_map(constants.STARTING_MAP, start_x, start_y)
        self.cur_map_name = constants.STARTING_MAP
        self.dash = False
        self.correr = False
        self.embestir = False
        self.casco_azul = False
        self.casco_verde = False
        self.casco_vikingo = False
        self.show_timer = False

        self.clock_sprite= arcade.load_texture("../resources/misc/1.png")
        self.total_time = 30.0

    #FUNCIÓN DESACTIVADA TEMPORALMENTE (inventario)
    #def load_hotbar_sprites(self):
        """Load the sprites for the hotbar at the bottom of the screen.

        Loads the controls sprite tileset and selects only the number pad button sprites.
        These will be visual representations of number keypads (1️⃣, 2️⃣, 3️⃣, ..., 0️⃣)
        to clarify that the hotkey bar can be accessed through these keypresses.
        """

        #first_number_pad_sprite_index = 51
        #last_number_pad_sprite_index = 61

        #self.hotbar_sprite_list = arcade.load_spritesheet(
            #file_name="../resources/tilesets/input_prompts_kenney.png",
            #sprite_width=16,
            #sprite_height=16,
            #columns=34,
            #count=816,
            #margin=1,
        #)[first_number_pad_sprite_index:last_number_pad_sprite_index]

    def setup_debug_menu(self):
        self.debug = False

        self.debug_menu = DebugMenu(
            width=450,
            height=200,
            noclip_callback=self.noclip,
            hyper_callback=self.hyper,
        )

        self.original_movement_speed = constants.MOVEMENT_SPEED
        self.noclip_status = False

    def enable_debug_menu(self):
        self.ui_manager.add(self.debug_menu)

    def disable_debug_menu(self):
        self.ui_manager.remove(self.debug_menu)

    def noclip(self, *args, status: bool):
        self.noclip_status = status

        self.setup_physics()

    def hyper(self, *args, status: bool):
        constants.MOVEMENT_SPEED = (
            int(self.original_movement_speed * 3.5)
            if status
            else self.original_movement_speed
        )

    #FUNCIÓN DESACTIVADA TEMPORALMENTE (inventario)
    #def draw_inventory(self):
        #capacity = 10
        #vertical_hotbar_location = 40
        #hotbar_height = 80
        #sprite_height = 16

        #field_width = self.window.width / (capacity + 1)

        #x = self.window.width / 2
        #y = vertical_hotbar_location

        #arcade.draw_rectangle_filled(
        #    x, y, self.window.width, hotbar_height, arcade.color.ALMOND
        #)
        #for i in range(capacity):
            #y = vertical_hotbar_location
            #x = i * field_width + 5
            #if i == self.selected_item - 1:
                #arcade.draw_lrtb_rectangle_outline(
                    #x - 6, x + field_width - 15, y + 25, y - 10, arcade.color.BLACK, 2
                #)

            #if len(self.player_sprite.inventory) > i:
                #item_name = self.player_sprite.inventory[i]["short_name"]
            #else:
                #item_name = ""

            #hotkey_sprite = self.hotbar_sprite_list[i]
            #hotkey_sprite.draw_scaled(x + sprite_height / 2, y + sprite_height / 2, 2.0)
            # Add whitespace so the item text doesn't hide behind the number pad sprite
            #text = f"     {item_name}"
            #arcade.draw_text(text, x, y, arcade.color.ALLOY_ORANGE, 16)

    def on_draw(self):
        """
        Render the screen.
        """

        # This command should happen before we start drawing. It will clear
        # the screen to the background color, and erase what we drew last frame.
        arcade.start_render()
        cur_map = self.map_list[self.cur_map_name]

        # --- Light related ---
        # Everything that should be affected by lights gets rendered inside this
        # 'with' statement. Nothing is rendered to the screen yet, just the light
        # layer.
        with cur_map.light_layer:
            arcade.set_background_color(cur_map.background_color)

            # Use the scrolling camera for sprites
            self.camera_sprites.use()

            # Grab each tile layer from the map
            map_layers = cur_map.map_layers

            # Draw scene
            cur_map.scene.draw()

            for item in map_layers.get("searchable", []):
                arcade.Sprite(
                    filename=":misc:shiny-stars.png",
                    center_x=item.center_x,
                    center_y=item.center_y,
                    scale=0.8,
                ).draw()

            # Draw the player
            self.player_sprite_list.draw()
            self.smoke_list.draw() #Dibuja la estela del dash, Importante que este aqui o estaria debajo del mapa
            self.smokes_list.draw()
            if(self.show_timer==True): # Parte visual del temporizador

                arcade.draw_text(self.output,
                                 self.player_sprite.center_x , self.player_sprite.center_y + 200  ,
                                 arcade.color.WHITE, 20,
                                 anchor_x="center")

                arcade.draw_texture_rectangle(self.player_sprite.center_x, self.player_sprite.center_y + 250, 50, 50, self.clock_sprite)


        if cur_map.light_layer:
            # Draw the light layer to the screen.
            # This fills the entire screen with the lit version
            # of what we drew into the light layer above.
            if cur_map.properties and "ambient_color" in cur_map.properties:
                ambient_color = cur_map.properties["ambient_color"]
                # ambient_color = (ambient_color.green, ambient_color.blue, ambient_color.alpha, ambient_color.red)
            else:
                ambient_color = arcade.color.WHITE
            cur_map.light_layer.draw(ambient_color=ambient_color)

        # Use the non-scrolled GUI camera
        self.camera_gui.use()

        # Draw the inventory
        #self.draw_inventory()
        #PRUEBA
        # Draw any message boxes
        if self.message_box:
            self.message_box.on_draw()

        # draw GUI
        self.ui_manager.draw()

    def scroll_to_player(self, speed=constants.CAMERA_SPEED):
        """Manage Scrolling"""

        vector = Vec2(
            self.player_sprite.center_x - self.window.width / 2,
            self.player_sprite.center_y - self.window.height / 2,
        )
        self.camera_sprites.move_to(vector, speed)


    def on_show_view(self):
        # Set background color
        my_map = self.map_list[self.cur_map_name]
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

    def on_update(self, delta_time):
        """
        All the logic to move, and the game logic goes here.
        """

        if(self.total_time <= 0.0): # Si el temporizador llega a 0:

            if(self.show_timer==True):
                #self.my_map = self.mapa_guardado
                self.switch_map(self.mapa_guardado,self.x_guardado,self.y_guardado)
                self.player_sprite.center_x = self.x_guardado
                self.player_sprite.center_y = self.y_guardado
            self.show_timer = False

        if(self.show_timer==True): # Si el temporizador esta activo:
            self.total_time -= delta_time
            minutes = int(self.total_time) // 60
            seconds = int(self.total_time) % 60
            seconds_100s = int((self.total_time - seconds) * 100)
            self.output = f"{minutes:02d}:{seconds:02d}"


        # Calculate speed based on the keys pressed
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

        SPEED_AUX = constants.MOVEMENT_SPEED

        try:
            slow_tiles_hit = arcade.check_for_collision_with_list(self.player_sprite, self.my_map.scene["slow_list"])
            push_tiles_hit = arcade.check_for_collision_with_list(self.player_sprite, self.my_map.scene["push_list"])
            cuesta_tiles_hit =  arcade.check_for_collision_with_list(self.player_sprite, self.my_map.scene["cuesta_list"])
            if slow_tiles_hit:
                SPEED_AUX = SPEED_AUX/4
            elif push_tiles_hit:
                SPEED_AUX = -SPEED_AUX*2
            elif cuesta_tiles_hit:
                if self.shift_pressed :
                    if self.correr:
                        print("Sube la cuesta corriendo, maybe disminuir un poco la velocidad") #Deberia pasar el obstaculo
                    else:
                        print("Falta casqueto")
                else:
                    self.player_sprite.change_y = -5
                    SPEED_AUX=0

        except KeyError:
            pass  # No hay capa slow_list, ni push, así que no hacemos nada.

        try:
            timer_hit = arcade.check_for_collision_with_list(
                self.player_sprite, self.my_map.scene["timer_list"]
            )
            if len(timer_hit) > 0 and self.show_timer== False: # Activar el temporizador
                if(self.cur_map_name=="Unfinished-Cave"): # Segun el mapa hay una cantdad de tiempo distinta. Hay que decidir esto segun los obstaculos que tengamos.
                    self.total_time = 50.0
                    constants.SONIDO=1
                    reproducir_musica_fondo()
                elif(self.cur_map_name=="pyramid_main"):
                    self.total_time = 45.0
                    constants.SONIDO = 2
                    reproducir_musica_fondo()
                elif(self.cur_map_name=="coloss_main"):
                    self.total_time = 70.0
                    constants.SONIDO = 3
                    reproducir_musica_fondo()
                elif(self.cur_map_name=="castillo_principal"):
                    self.total_time = 50.0
                    constants.SONIDO = 4
                    reproducir_musica_fondo()
                else:
                    self.total_time = 30.0
                self.show_timer = True
                self.x_guardado = self.player_sprite.center_x
                self.y_guardado = self.player_sprite.center_y
                self.mapa_guardado = self.cur_map_name
        except KeyError:
            pass
        try:
            stop_hit = arcade.check_for_collision_with_list(
                self.player_sprite, self.my_map.scene["stop_list"]
            )
            if len(stop_hit) > 0 and self.show_timer == True: # Desactivar el temporizador
                self.show_timer = False
        except KeyError:
            pass

        #Para poder cambiar la sprite del jugador
        self.player_sprite.on_update(delta_time)
        cooldown = False
        self.smoke_list = arcade.SpriteList() #Hace que la lista usada para la estela del dash se actualice
        self.smoke_list.update()
        MOVING_UP = (
            self.up_pressed
            and not self.down_pressed
            and not self.right_pressed
            and not self.left_pressed
        )

        MOVING_DOWN = (
            self.down_pressed
            and not self.up_pressed
            and not self.right_pressed
            and not self.left_pressed
        )

        MOVING_RIGHT = (
            self.right_pressed
            and not self.left_pressed
            and not self.up_pressed
            and not self.down_pressed
        )

        MOVING_LEFT = (
            self.left_pressed
            and not self.right_pressed
            and not self.up_pressed
            and not self.down_pressed
        )

        MOVING_UP_LEFT = (
            self.up_pressed
            and self.left_pressed
            and not self.down_pressed
            and not self.right_pressed
        )

        MOVING_DOWN_LEFT = (
            self.down_pressed
            and self.left_pressed
            and not self.up_pressed
            and not self.right_pressed
        )

        MOVING_UP_RIGHT = (
            self.up_pressed
            and self.right_pressed
            and not self.down_pressed
            and not self.left_pressed
        )

        MOVING_DOWN_RIGHT = (
            self.down_pressed
            and self.right_pressed
            and not self.up_pressed
            and not self.left_pressed
        )
        #PRUEBA DASH
        #Conjunto de teclas para el dash en cada direccion
        MOVING_RIGHT_SPACE = (
                self.right_pressed
                and self.space_pressed
                and not self.left_pressed
                and not self.up_pressed
                and not self.down_pressed
        )
        MOVING_LEFT_SPACE = (
                self.left_pressed
                and self.space_pressed
                and not self.right_pressed
                and not self.up_pressed
                and not self.down_pressed
        )
        MOVING_UP_SPACE = (
                self.up_pressed
                and self.space_pressed
                and not self.left_pressed
                and not self.right_pressed
                and not self.down_pressed
        )
        MOVING_DOWN_SPACE = (
                self.down_pressed
                and self.space_pressed
                and not self.left_pressed
                and not self.up_pressed
                and not self.right_pressed
        )
        #PRUEBA CORRER

        #Conjuntos de teclas necesarios para que el personaje corra en cada direccion
        MOVING_UP_RUN = (
                self.up_pressed
                and not self.down_pressed
                and not self.right_pressed
                and not self.left_pressed
                and self.shift_pressed
        )
        MOVING_DOWN_RUN = (
                self.down_pressed
                and not self.up_pressed
                and not self.right_pressed
                and not self.left_pressed
                and self.shift_pressed
        )
        MOVING_RIGHT_RUN = (
                self.right_pressed
                and not self.left_pressed
                and not self.up_pressed
                and not self.down_pressed
                and self.shift_pressed
        )
        MOVING_LEFT_RUN = (
                self.left_pressed
                and not self.right_pressed
                and not self.up_pressed
                and not self.down_pressed
                and self.shift_pressed
        )
        MOVING_UP_LEFT_RUN = (
                self.up_pressed
                and self.left_pressed
                and not self.down_pressed
                and not self.right_pressed
                and self.shift_pressed
        )
        MOVING_DOWN_LEFT_RUN = (
                self.down_pressed
                and self.left_pressed
                and not self.up_pressed
                and not self.right_pressed
                and self.shift_pressed
        )
        MOVING_UP_RIGHT_RUN = (
                self.up_pressed
                and self.right_pressed
                and not self.down_pressed
                and not self.left_pressed
                and self.shift_pressed
        )
        MOVING_DOWN_RIGHT_RUN = (
                self.down_pressed
                and self.right_pressed
                and not self.up_pressed
                and not self.left_pressed
                and self.shift_pressed

        )



        if MOVING_UP:
            self.player_sprite.change_y = SPEED_AUX

        if MOVING_DOWN:
            self.player_sprite.change_y = -SPEED_AUX

        if MOVING_LEFT:
            self.player_sprite.change_x = -SPEED_AUX

        if MOVING_RIGHT:
            self.player_sprite.change_x = SPEED_AUX

        if MOVING_UP_LEFT:
            self.player_sprite.change_y = SPEED_AUX / 1.5
            self.player_sprite.change_x = -SPEED_AUX / 1.5

        if MOVING_UP_RIGHT:
            self.player_sprite.change_y = SPEED_AUX / 1.5
            self.player_sprite.change_x = SPEED_AUX / 1.5

        if MOVING_DOWN_LEFT:
            self.player_sprite.change_y = -SPEED_AUX / 1.5
            self.player_sprite.change_x = -SPEED_AUX / 1.5

        if MOVING_DOWN_RIGHT:
            self.player_sprite.change_y = -SPEED_AUX / 1.5
            self.player_sprite.change_x = SPEED_AUX / 1.5

        #PRUEBA DASH
        #Condiciones para que el personaje use el dash: que el conjunto de teclas correcto este pulsado y que no este en cooldown
        """
        COMO FUNCIONA EL DASH:
        - self.player_sprite.change_x = constants.MOVEMENT_SPEED + 5
        Sumo 5 a la velocidad de movimiento en esa dirección, si se lo sumase a la distancia directamente se haria tp
        - threading.Timer(0.15, self.activar_cooldown).start()
        Espera 0.15 segundos (para que de tiempo a hacer el dash) y se mete en la funcion cooldown para que el cooldown sea True
        - smoke = arcade.Sprite(":characters:Shadow/1.png", 1)
        - x = self.player_sprite.center_x
        - y = self.player_sprite.center_y
        - smoke.center_x = x - 5
        - smoke.center_y = y
        Define la Sprite de la estela y sus posiciones x e y
        - self.smoke_list.append(smoke)
        - threading.Timer(3, lambda: smoke.remove_from_sprite_lists()).start()
        Añade el humo a la lista (para luego ser dibujado) y tras un tiempo este es borrado
        """
        if self.dash == True: #Solo si tiene el casco azul puesto
            if MOVING_RIGHT_SPACE and self.cooldown == False:
                self.player_sprite.change_x = constants.MOVEMENT_SPEED + 5
                threading.Timer(0.15, self.activar_cooldown).start()
                smoke = arcade.Sprite(":characters:Shadow/1.png", 1)
                x = self.player_sprite.center_x
                y = self.player_sprite.center_y
                smoke.center_x = x - 5
                smoke.center_y = y
                self.smoke_list.append(smoke)
                threading.Timer(3, lambda: smoke.remove_from_sprite_lists()).start()

            if MOVING_LEFT_SPACE and self.cooldown == False:
                self.player_sprite.change_x = -constants.MOVEMENT_SPEED - 5
                threading.Timer(0.15, self.activar_cooldown).start()
                smoke = arcade.Sprite(":characters:Shadow/1.png", 1)
                x = self.player_sprite.center_x
                y = self.player_sprite.center_y
                smoke.center_x = x + 40
                smoke.center_y = y
                self.smoke_list.append(smoke)
                threading.Timer(3, lambda: smoke.remove_from_sprite_lists()).start()
            if MOVING_UP_SPACE and self.cooldown == False:
                self.player_sprite.change_y = constants.MOVEMENT_SPEED + 5
                threading.Timer(0.15, self.activar_cooldown).start()
                smoke = arcade.Sprite(":characters:Shadow/3.png", 1)
                x = self.player_sprite.center_x
                y = self.player_sprite.center_y
                smoke.center_x = x
                smoke.center_y = y - 45
                self.smoke_list.append(smoke)
            if MOVING_DOWN_SPACE and self.cooldown == False:
                self.player_sprite.change_y = -constants.MOVEMENT_SPEED - 5
                threading.Timer(0.15, self.activar_cooldown).start()
                smoke = arcade.Sprite(":characters:Shadow/3.png", 1)
                x = self.player_sprite.center_x
                y = self.player_sprite.center_y
                smoke.center_x = x
                smoke.center_y = y + 10
                self.smoke_list.append(smoke)

        if self.embestir == True: #Si puede embestir (casco vikingo)

            x = self.player_sprite.center_x
            y = self.player_sprite.center_y

            # Mover a la derecha
            if MOVING_RIGHT_SPACE and self.cooldown1 == False:
                self.player_sprite.change_x = constants.MOVEMENT_SPEED + 7
                threading.Timer(0.15, self.activar_cooldown1).start()
                if not self.humo_activo:  # Solo crea humo si no hay uno activo
                    threading.Timer(0.0, self.crear_humo, args=(x, y), kwargs={'offset_x': -20}).start()
                    threading.Timer(0.1, self.crear_humo, args=(x, y), kwargs={'offset_x': 10}).start()
                    threading.Timer(0.2, self.crear_humo, args=(x, y), kwargs={'offset_x': 40}).start()
                    threading.Timer(0.3, self.crear_humo, args=(x, y), kwargs={'offset_x': 70}).start()
                    self.humo_activo = True  # Marca que el humo está activo

            # Mover a la izquierda
            if MOVING_LEFT_SPACE and self.cooldown1 == False:
                self.player_sprite.change_x = -constants.MOVEMENT_SPEED - 7
                threading.Timer(0.15, self.activar_cooldown1).start()
                if not self.humo_activo:
                    threading.Timer(0.0, self.crear_humo, args=(x, y), kwargs={'offset_x': 20}).start()
                    threading.Timer(0.1, self.crear_humo, args=(x, y), kwargs={'offset_x': -10}).start()
                    threading.Timer(0.2, self.crear_humo, args=(x, y), kwargs={'offset_x': -40}).start()
                    threading.Timer(0.3, self.crear_humo, args=(x, y), kwargs={'offset_x': -70}).start()
                    self.humo_activo = True

            # Mover hacia arriba
            if MOVING_UP_SPACE and self.cooldown1 == False:
                self.player_sprite.change_y = constants.MOVEMENT_SPEED + 7
                threading.Timer(0.15, self.activar_cooldown1).start()
                if not self.humo_activo:
                    threading.Timer(0.0, self.crear_humo, args=(x, y), kwargs={'offset_y': -20}).start()
                    threading.Timer(0.1, self.crear_humo, args=(x, y), kwargs={'offset_y': 10}).start()
                    threading.Timer(0.2, self.crear_humo, args=(x, y), kwargs={'offset_y': 40}).start()
                    threading.Timer(0.3, self.crear_humo, args=(x, y), kwargs={'offset_y': 70}).start()
                    self.humo_activo = True

            # Mover hacia abajo
            if MOVING_DOWN_SPACE and self.cooldown1 == False:
                self.player_sprite.change_y = -constants.MOVEMENT_SPEED - 7
                threading.Timer(0.15, self.activar_cooldown1).start()
                if not self.humo_activo:
                    threading.Timer(0.0, self.crear_humo, args=(x, y), kwargs={'offset_y': 20}).start()
                    threading.Timer(0.1, self.crear_humo, args=(x, y), kwargs={'offset_y': -10}).start()
                    threading.Timer(0.2, self.crear_humo, args=(x, y), kwargs={'offset_y': -40}).start()
                    threading.Timer(0.3, self.crear_humo, args=(x, y), kwargs={'offset_y': -70}).start()
                    self.humo_activo = True

            # Actualizar animaciones
        self.smokes_list.update_animation(delta_time)
        # PRUEBA CORRER
        # Similar a cuando anda el personaje solo que ponemos RUN_MOVEMENT_SPEED que es superior
        if self.correr == True:  # Solo si tiene el casco verde puesto
            if MOVING_UP_RUN:
                self.player_sprite.change_y = SPEED_AUX * 2
            elif MOVING_DOWN_RUN:
                self.player_sprite.change_y = -SPEED_AUX * 2
            elif MOVING_LEFT_RUN:
                self.player_sprite.change_x = -SPEED_AUX * 2
            elif MOVING_RIGHT_RUN:
                self.player_sprite.change_x = SPEED_AUX * 2
            elif MOVING_UP_LEFT_RUN:
                self.player_sprite.change_y = SPEED_AUX * 2 / 1.5
                self.player_sprite.change_x = -SPEED_AUX * 2 / 1.5
            elif MOVING_UP_RIGHT_RUN:
                self.player_sprite.change_y = SPEED_AUX * 2 / 1.5
                self.player_sprite.change_x = SPEED_AUX * 2 / 1.5
            elif MOVING_DOWN_LEFT_RUN:
                self.player_sprite.change_y = -SPEED_AUX * 2 / 1.5
                self.player_sprite.change_x = -SPEED_AUX * 2 / 1.5
            elif MOVING_DOWN_RIGHT_RUN:
                self.player_sprite.change_y = -SPEED_AUX * 2 / 1.5
                self.player_sprite.change_x = SPEED_AUX * 2 / 1.5

        for smoke in self.smokes_list:
            smoke.update_animation(delta_time)

            if smoke.alpha > 0:
                smoke.alpha -= 5  # Se va haciendo transparente
            else:
                smoke.remove_from_sprite_lists()

    #PRUEBA CORRER
        # Similar a cuando anda el personaje solo que ponemos RUN_MOVEMENT_SPEED que es superior
        if self.correr == True: #Solo si tiene el casco verde puesto
            if MOVING_UP_RUN:
                self.player_sprite.change_y = SPEED_AUX*2
            elif MOVING_DOWN_RUN:
                self.player_sprite.change_y = -SPEED_AUX*2
            elif MOVING_LEFT_RUN:
                self.player_sprite.change_x = -SPEED_AUX*2
            elif MOVING_RIGHT_RUN:
                self.player_sprite.change_x = SPEED_AUX*2
            elif MOVING_UP_LEFT_RUN:
                self.player_sprite.change_y = SPEED_AUX*2 / 1.5
                self.player_sprite.change_x = -SPEED_AUX*2 / 1.5
            elif MOVING_UP_RIGHT_RUN:
                self.player_sprite.change_y = SPEED_AUX*2 / 1.5
                self.player_sprite.change_x = SPEED_AUX*2 / 1.5
            elif MOVING_DOWN_LEFT_RUN:
                self.player_sprite.change_y = -SPEED_AUX*2 / 1.5
                self.player_sprite.change_x = -SPEED_AUX*2 / 1.5
            elif MOVING_DOWN_RIGHT_RUN:
                self.player_sprite.change_y = -SPEED_AUX*2 / 1.5
                self.player_sprite.change_x = SPEED_AUX*2 / 1.5
        # Call update to move the sprite
        self.physics_engine.update()

        # Update player animation
        self.player_sprite_list.on_update(delta_time)

        self.player_light.position = self.player_sprite.position

        # Update the characters
        try:
            self.map_list[self.cur_map_name].scene["characters"].on_update(delta_time)
        except KeyError:
            # no characters on map
            pass

        # --- Manage doors ---
        map_layers = self.map_list[self.cur_map_name].map_layers

        # Is there as layer named 'doors'?
        if "doors" in map_layers:
            # Did we hit a door?
            doors_hit = arcade.check_for_collision_with_list(
                self.player_sprite, map_layers["doors"]
            )
            # We did!
            if len(doors_hit) > 0:
                try:
                    # Grab the info we need
                    map_name = doors_hit[0].properties["map_name"]
                    start_x = doors_hit[0].properties["start_x"]
                    start_y = doors_hit[0].properties["start_y"]
                except KeyError:
                    raise KeyError(
                        "Door objects must have 'map_name', 'start_x', and 'start_y' properties defined."
                    )

                # Swap to the new map
                self.switch_map(map_name, start_x, start_y)
            else:
                # We didn't hit a door, scroll normally
                self.scroll_to_player()
        else:
            # No doors, scroll normally
            self.scroll_to_player()


        if "dasheable" in map_layers:
            for dasheable in map_layers["dasheable"]:
                if dasheable in self.my_map.scene["wall_list"]:
                    self.my_map.scene["wall_list"].remove(dasheable)

                # Did we hit a door?
            dasheable_hit = arcade.check_for_collision_with_list(self.player_sprite, map_layers["dasheable"])

            if len(dasheable_hit) > 0:
                dasheable_sprite = dasheable_hit[0]  # El sprite del objeto con la que hemos colisionado

                if not self.space_pressed or self.cooldown or self.casco_azul==False:
                    self.my_map.scene["wall_list"].append(dasheable_sprite)  # El objeto bloquea el paso

        if "timer" in map_layers:
            timer_hit = arcade.check_for_collision_with_list(self.player_sprite, map_layers["timer"])
            if len(timer_hit) > 0 and self.show_timer == False:  # Activar el temporizador
                self.total_time = timer_hit[0].properties["time"]
                self.show_timer = True
                self.x_guardado = self.player_sprite.center_x
                self.y_guardado = self.player_sprite.center_y
                self.mapa_guardado = self.cur_map_name



        if "rompible" in map_layers:
            for rompible in map_layers["rompible"]:
                if rompible in self.my_map.scene["wall_list"]:
                    self.my_map.scene["wall_list"].remove(rompible)

                # Did we hit a door?
            rompible_hit = arcade.check_for_collision_with_list(self.player_sprite, map_layers["rompible"])

            if len(rompible_hit) > 0:
                rompible_sprite = rompible_hit[0]  # El sprite de la puerta con la que hemos colisionado

                if (self.space_pressed or self.cooldown) and self.casco_vikingo ==True:
                    #print("BOOOOOOOOOOM")
                    #UN RESPLANDOR Y HACE PUUUUUM
                    rompible_sprite.remove_from_sprite_lists()
                else:
                    self.my_map.scene["wall_list"].append(rompible_sprite)

        if "un_monedo" in map_layers:
            monedo_hit = arcade.check_for_collision_with_list(self.player_sprite, map_layers["un_monedo"])
            if len(monedo_hit) > 0:
                monedo_sprite = monedo_hit[0]  # El sprite de la puerta con la que hemos colisionado
                monedo_sprite.remove_from_sprite_lists()
                if self.cur_map_name=="Prueba":
                    constants.Contador -=1
                elif self.cur_map_name=="castillo_exterior":
                    constants.Contador_castilloext-=1
                elif self.cur_map_name=="castillo_principal":
                    constants.Contador_castilloprinc-=1
                elif self.cur_map_name=="coloss_main":
                    constants.Contador_colossmain-=1
                elif self.cur_map_name=="castillo_salida":
                    constants.Contador_castillosal-=1

        if "puertaD" in map_layers:

            if self.cur_map_name == "castillo_exterior":
                contador_puertaD = constants.Contador_castilloext
            elif self.cur_map_name == "castillo_principal":
                contador_puertaD = constants.Contador_castilloprinc
            else:
                contador_puertaD=0

            if contador_puertaD > 0:
                for puertaD in map_layers["puertaD"]:
                    if puertaD not in self.my_map.scene["wall_list"]:
                        self.my_map.scene["wall_list"].append(puertaD)
            elif contador_puertaD == 0:
                for puertaD in map_layers["puertaD"]:
                    if puertaD in self.my_map.scene["wall_list"]:
                        self.my_map.scene["wall_list"].remove(puertaD)
                        puertaD.remove_from_sprite_lists()

        if "puertaB" in map_layers:

            for puertaB in map_layers["puertaB"]:
                if puertaB.visible==True:
                    puertaB.visible=False
            doorsB_hit = arcade.check_for_collision_with_list(
                self.player_sprite, map_layers["puertaB"]
            )

            if len(doorsB_hit) > 0:
                doorB = doorsB_hit[0]
                self.contadorB+=1

                doorB.visible = True
                try:

                    # Grab the info we need

                    map_name = doorB.properties["map_name"]
                    start_x = doorB.properties["start_x"]
                    start_y = doorB.properties["start_y"]
                except KeyError:
                    raise KeyError(
                        "Door objects must have 'map_name', 'start_x', and 'start_y' properties defined."
                    )

                # Swap to the new map
                if(doorB.visible==True and self.contadorB==2):
                    time.sleep(0.5)
                    self.switch_map(map_name, start_x, start_y)
                    self.contadorB=0
                    doorB.visible=False

        if "puertaM" in map_layers:
            if self.cur_map_name=="Prueba":
                contador_puertaM = constants.Contador
            elif self.cur_map_name == "castillo_principal":
                contador_puertaM = constants.Contador_castilloprinc
            elif self.cur_map_name == "coloss_main":
                contador_puertaM = constants.Contador_colossmain
            elif self.cur_map_name == "castillo_salida":
                contador_puertaM = constants.Contador_castillosal
            else:
                contador_puertaM=0
            for puertaM in map_layers["puertaM"]:
                if puertaM in self.my_map.scene["wall_list"]:
                    self.my_map.scene["wall_list"].remove(puertaM)

                # Did we hit a door?
            puertaM_hit = arcade.check_for_collision_with_list(self.player_sprite, map_layers["puertaM"])

            if len(puertaM_hit) > 0:
                puertaM_sprite = puertaM_hit[0]  # El sprite de la puerta con la que hemos colisionado
                if contador_puertaM == 0:
                    if constants.Puerta == True:
                        #print("CLICK") #MONDONGOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO
                        arcade.play_sound(arcade.load_sound(":sounds:puerta.wav"))
                        constants.Puerta = False
                        def reactivar_puerta():
                            constants.Puerta = True
                        threading.Timer(5, reactivar_puerta).start()
                        puertaM_sprite.remove_from_sprite_lists() #Aqui desapareceria la puerta, sin esto solamanente lo atraviesas
                else:
                    print("Dale zelda dale")
                    self.my_map.scene["wall_list"].append(puertaM_sprite)




    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed."""

        if self.message_box:
            self.message_box.on_key_press(key, modifiers)
            return

        if key in constants.KEY_UP:
            self.up_pressed = True
        elif key in constants.KEY_DOWN:
            self.down_pressed = True
        elif key in constants.KEY_LEFT:
            self.left_pressed = True
        elif key in constants.KEY_RIGHT:
            self.right_pressed = True
        #MIRA SI EL ESPACIO ESTA PRESIONADO
        elif key in constants.KEY_SPACE:
            self.space_pressed = True
        #MIRA SI EL SHIFT ESTA PRESIONADO
        elif key in constants.KEY_SHIFT or key == arcade.key.RSHIFT:
            self.shift_pressed = True

        elif key == arcade.key.ESCAPE:
            print("game paused")
            pil_image = arcade.get_image()  #Saca una captura de pantalla del juego
            nombre_unico = f"pause_bg_{time.time()}" #Se asigna un nombre unico a cada captura, de manera que se actualiza correctamente el fondo
            bg_texture = arcade.Texture(name=nombre_unico, image=pil_image)

            #Se limpian las teclas de movimiento
            self.shift_pressed = False
            self.space_pressed = False
            self.up_pressed = False
            self.down_pressed = False
            self.left_pressed = False
            self.right_pressed = False

            #Se asigna el fondo al menú de pausa
            self.window.views["settings"] = SettingsView(background_texture=bg_texture)
            self.window.views["main_menu"] = MainMenuView(background_texture=bg_texture)
            self.window.show_view(self.window.views["main_menu"])

        elif key in constants.SEARCH: #Esto en una constante es la letra E
            self.search()

        elif key == arcade.key.KEY_1 or key == arcade.key.NUM_1:  #Casco naranja, sin efecto especial
            self.player_sprite.set_spritesheet(self.player_sprite.sprite_sheet1)
            self.casco_azul = False
            self.casco_verde = False
            self.dash = False
            self.correr = False
            self.casco_vikingo = False
            self.embestir = False

        elif key == arcade.key.KEY_2 or key == arcade.key.NUM_2: #Casco azul, posibilidad de hacer dash
            self.player_sprite.set_spritesheet(self.player_sprite.sprite_sheet2)
            self.casco_azul = True
            self.casco_verde = False
            self.dash = True
            self.correr = False
            self.casco_vikingo = False
            self.embestir = False

        elif key == arcade.key.KEY_3 or key == arcade.key.NUM_3:  #Casco verde, permite correr
            self.player_sprite.set_spritesheet(self.player_sprite.sprite_sheet3)
            self.casco_azul = False
            self.casco_verde = True
            self.dash = False
            self.correr = True
            self.casco_vikingo = False
            self.embestir = False
        elif key == arcade.key.KEY_4 or key == arcade.key.NUM_4:  #Casco de vikingo, permite embestir para romper muros
            self.player_sprite.set_spritesheet(self.player_sprite.sprite_sheet4)
            self.casco_azul = False
            self.casco_verde = False
            self.dash = False
            self.correr = False
            self.casco_vikingo = True
            self.embestir = True

        elif key == arcade.key.L:
            cur_map = self.map_list[self.cur_map_name]
            if self.player_light in cur_map.light_layer:
                cur_map.light_layer.remove(self.player_light)
            else:
                cur_map.light_layer.add(self.player_light)
        elif key == arcade.key.G:  # G
            # toggle debug
            self.debug = True if not self.debug else False
            if self.debug:
                self.enable_debug_menu()
            else:
                self.disable_debug_menu()

        elif key == arcade.key.J and self.show_timer== False: # Activar el temporizador por la tecla J
            self.total_time = 30.0
            self.show_timer = True
            self.x_guardado = self.player_sprite.center_x
            self.y_guardado = self.player_sprite.center_y
            self.mapa_guardado = self.cur_map_name

        elif key == arcade.key.K and self.show_timer == True: # Desactivar el temporizador con la tecla K
            self.show_timer = False


    def close_message_box(self):
        self.message_box = None

    def search(self):
        """Search for things"""
        map_layers = self.map_list[self.cur_map_name].map_layers
        if "searchable" not in map_layers:
            print(f"No searchable sprites on {self.cur_map_name} map layer.")
            return

        searchable_sprites = map_layers["searchable"]
        sprites_in_range = arcade.check_for_collision_with_list(
            self.player_sprite, searchable_sprites
        )
        print(f"Found {len(sprites_in_range)} searchable sprite(s) in range.")
        for sprite in sprites_in_range:
            if "item" in sprite.properties:
                self.message_box = MessageBox(
                    self, f"Found: {sprite.properties['item']}"
                )
                sprite.remove_from_sprite_lists()
                lookup_item = self.item_dictionary[sprite.properties["item"]]
                self.player_sprite.inventory.append(lookup_item)
            else:
                print(
                    "The 'item' property was not set for the sprite. Can't get any items from this."
                )

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key."""

        if key in constants.KEY_UP:
            self.up_pressed = False
        elif key in constants.KEY_DOWN:
            self.down_pressed = False
        elif key in constants.KEY_LEFT:
            self.left_pressed = False
        elif key in constants.KEY_RIGHT:
            self.right_pressed = False
        #MIRA SI EL ESPACIO YA NO ESTA PRESIONADO
        elif key in constants.KEY_SPACE:
            self.space_pressed = False
        # MIRA SI EL SHIFT YA NO ESTA PRESIONADO
        elif key in constants.KEY_SHIFT or key == arcade.key.RSHIFT:
            self.shift_pressed = False

    def on_mouse_motion(self, x, y, delta_x, delta_y):
        """Called whenever the mouse moves."""
        pass

    def on_mouse_press(self, x, y, button, key_modifiers):
        """Called when the user presses a mouse button."""
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.player_sprite.destination_point = x, y

    def on_mouse_release(self, x, y, button, key_modifiers):
        """Called when a user releases a mouse button."""
        pass

    def on_resize(self, width, height):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        self.camera_sprites.resize(width, height)
        self.camera_gui.resize(width, height)
        cur_map = self.map_list[self.cur_map_name]
        if cur_map.light_layer:
            cur_map.light_layer.resize(width, height)

    def activar_cooldown(self):
        """Activa el cooldown y lo desactiva después de 2 segundos."""
        self.cooldown = True

        # Usamos threading.Timer para desactivar después de 2 segundos
        threading.Timer(1, self.desactivar_cooldown).start()

    def desactivar_cooldown(self):
        """Desactiva el cooldown."""
        self.cooldown = False

    def crear_humo(self, x, y, offset_x=0, offset_y=0):
        smoke = arcade.AnimatedTimeBasedSprite(scale=0.5)
        smoke.center_x = x + offset_x
        smoke.center_y = y + offset_y
        smoke.alpha = 255


        rutas = [
            ":characters:Shadow/smokes_1.png",
            ":characters:Shadow/smokes_2.png",
            ":characters:Shadow/smokes_3.png",
            ":characters:Shadow/smokes_4.png",
            ":characters:Shadow/smokes_5.png",
            ":characters:Shadow/smokes_6.png",
        ]

        # Cargar las texturas
        for i, ruta in enumerate(rutas):
            frame_texture = arcade.load_texture(ruta)
            keyframe = arcade.AnimationKeyframe(i, 250, frame_texture)
            smoke.frames.append(keyframe)

        self.smokes_list.append(smoke)

        def eliminar_humo():
            smoke.remove_from_sprite_lists()
            self.humo_activo = False

        threading.Timer(0.75, eliminar_humo).start()

    def activar_cooldown1(self):
        self.cooldown1 = True
        threading.Timer(1, self.desactivar_cooldown1).start()

    def desactivar_cooldown1(self):
        self.cooldown1 = False
        self.player_sprite.change_x = 0
        self.player_sprite.change_y = 0

def reproducir_musica_fondo():
    if constants.SONIDO==0:
        sonido = arcade.load_sound(":sounds:nivel1/theme.mp3")
    if constants.SONIDO==1:
        sonido = arcade.load_sound(":sounds:nivel1/theme.mp3")
    if constants.SONIDO==2:
        sonido = arcade.load_sound(":sounds:nivel1/theme.mp3")
    if constants.SONIDO==3:
        sonido = arcade.load_sound(":sounds:nivel1/theme.mp3")
    if constants.SONIDO==4:
        sonido = arcade.load_sound(":sounds:nivel1/theme.mp3")
    def loop_sound():
        player = arcade.play_sound(sonido)
        player.push_handlers(on_eos=lambda: loop_sound())  # Reproduce de nuevo cuando termine
    loop_sound()