"""
Constant values for the game
"""
import arcade
import pyglet
from pyglet.input.evdev_constants import KEY_SPACE

# Detectar la resolución principal del monitor
_display = pyglet.canvas.get_display()
_screen = _display.get_screens()[0] #El monitor principal
SCREEN_WIDTH = _screen.width
SCREEN_HEIGHT = _screen.height

SCREEN_TITLE = "Python Community RPG"
TILE_SCALING = 1.0
SPRITE_SIZE = 32

# How fast does the player move
MOVEMENT_SPEED = 4
RUN_MOVEMENT_SPEED = 7
SLOW_SPEED = 1
SPEED_AUX = 4

#Contador de monedas de prueba para el mapa de prueba
Contador = 5
Puerta = True
#Contador de monedas del castillo exterior
Contador_castilloext=6
#Contador llaves del castillo principal
Contador_castilloprinc=2
#Contador llaves del castillo salida
Contador_castillosal=6
#Contador gemas coliseo main.
Contador_colossmain=6
#Contadores gemas laboatorio
CONTADOR_LAB1 = 7
CONTADOR_LAB2 = 9
# Lista de los cascos
CASCOS_LIST = ["Dashing Helmet", "Fleeting Helmet", "Charging Helmet"]

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 300
RIGHT_VIEWPORT_MARGIN = 300
BOTTOM_VIEWPORT_MARGIN = 300
TOP_VIEWPORT_MARGIN = 300

# What map, and what position we start at
STARTING_MAP = "farmhouse"
STARTING_X = 13
STARTING_Y = 10

# Key mappings
KEY_UP = [arcade.key.UP, arcade.key.W]
KEY_DOWN = [arcade.key.DOWN, arcade.key.S]
KEY_LEFT = [arcade.key.LEFT, arcade.key.A]
KEY_RIGHT = [arcade.key.RIGHT, arcade.key.D]
KEY_SPACE = [arcade.key.SPACE]
KEY_SHIFT = [arcade.key.LSHIFT]
KEY_TAB = [arcade.key.TAB]
INVENTORY = [arcade.key.I]
SEARCH = [arcade.key.E]

# Message box
MESSAGE_BOX_FONT_SIZE = 20
MESSAGE_BOX_MARGIN = 30

# How fast does the camera pan to the user
CAMERA_SPEED = 0.8

#Constantes para los cascos (Esto lo podemos usar para ver si se tienen los cascos obtenidos o no, por default estaran en False)
FLEETING_OBTAINED = False
DASHING_OBTAINED = False
CHARGING_OBTAINED = False

#cosas de pausar y reanudar la musica xd
player = None
sonido = 0
SONIDO = 0
