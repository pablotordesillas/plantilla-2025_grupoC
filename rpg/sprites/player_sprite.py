import arcade
import time
from rpg.sprites.chacter_sprite1 import CharacterSprite_one
from rpg.sprites.character_sprite import CharacterSprite


class PlayerSprite(CharacterSprite_one):
    def __init__(self, sheet_name, sheet_name2, sheet_name3, sheet_name4):
        super().__init__(sheet_name, sheet_name2, sheet_name3, sheet_name4)
        self.sound_update = 0
        self.footstep_sound = arcade.load_sound(":sounds:nivel0/pasos.mp3") #cambialo reventado de mierda
        print(self.footstep_sound)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if not self.change_x and not self.change_y:
            return
        speed = (self.change_x ** 2 + self.change_y ** 2) ** 0.5
        self.sound_update += speed * delta_time
        if self.sound_update >= 1.0:
            arcade.play_sound(self.footstep_sound)
            self.sound_update = 0