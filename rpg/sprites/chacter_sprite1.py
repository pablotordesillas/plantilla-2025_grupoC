"""
Animated sprite for characters that walk around.
"""


import arcade

from enum import Enum
from rpg.constants import SPRITE_SIZE

Direction = Enum("Direction", "DOWN LEFT RIGHT UP")

SPRITE_INFO = {
    Direction.DOWN: [0, 1, 2, 3],
    Direction.LEFT: [4, 5, 6, 7],
    Direction.RIGHT: [8, 9, 10, 11],
    Direction.UP: [12, 13, 14, 15],
}


class CharacterSprite_one(arcade.Sprite):
    def __init__(self, sheet_name, sheet_name2, sheet_name3, sheet_name4):
        super().__init__()
        self.sprite_sheet1 = arcade.load_spritesheet(
            sheet_name,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE,
            columns=4,
            count=16,
        )
        self.sprite_sheet2 = arcade.load_spritesheet(
            sheet_name2,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE,
            columns=4,
            count=16,
        )
        self.sprite_sheet3 = arcade.load_spritesheet(
            sheet_name3,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE,
            columns=4,
            count=16,
        )
        self.sprite_sheet4 = arcade.load_spritesheet(
            sheet_name4,
            sprite_width=SPRITE_SIZE,
            sprite_height=SPRITE_SIZE,
            columns=4,
            count=16,
        )
        #Defines tantas spritesheets como vaya a tener el personaje
        self.textures = self.sprite_sheet1 #Anteriormente sprite_sheet1 era textures, esto es para que siga llendo el codigo
        self.using_alt_sheet = False #Dice si estas usando la segunda spritesheet
        self.using_third_sheet = False #Dice si estas usando la tercera spritesheet

        self.current_direction = Direction.DOWN

        self.should_update = 0
        self.cur_texture_index = 0
        self.texture = self.textures[self.cur_texture_index]
        self.inventory = []
    def on_update(self, delta_time):
        if not self.change_x and not self.change_y:
            return

        # self.center_x += self.change_x
        # self.center_y += self.change_y

        if self.should_update <= 4:
            self.should_update += 1
        else:
            self.should_update = 0
            self.cur_texture_index += 1

        direction = Direction.LEFT
        slope = self.change_y / (self.change_x + 0.0001)
        if abs(slope) < 0.8:
            if self.change_x > 0:
                direction = Direction.RIGHT
            else:
                # technically not necessary, but for readability
                direction = Direction.LEFT
        else:
            if self.change_y > 0:
                direction = Direction.UP
            else:
                direction = Direction.DOWN

        if self.cur_texture_index not in SPRITE_INFO[direction]:
            self.cur_texture_index = SPRITE_INFO[direction][0]

        self.current_direction = direction
        self.texture = self.textures[self.cur_texture_index]

    def set_spritesheet(self, sheet):
        self.textures = sheet

        # Encontrar el índice relativo actual (dentro de los 4 frames de la dirección)
        relative_index = SPRITE_INFO[self.current_direction].index(self.cur_texture_index)

        # Usar el mismo índice relativo en la nueva spritesheet para la misma dirección
        self.cur_texture_index = SPRITE_INFO[self.current_direction][relative_index]
        self.texture = self.textures[self.cur_texture_index]