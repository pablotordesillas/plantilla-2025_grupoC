import arcade
import time
import rpg.constants as const
from rpg.sprites.chacter_sprite1 import CharacterSprite_one

class PlayerSprite(CharacterSprite_one):
    def __init__(self, sheet_name, sheet_name2, sheet_name3, sheet_name4):
        super().__init__(sheet_name, sheet_name2, sheet_name3, sheet_name4)
        self.sound_update = 0
        self.footstep_sounds = {
            0: arcade.load_sound(":sounds:nivel1/pasos.wav"),
            1: arcade.load_sound(":sounds:nivel0/pasos.wav"),
            2: arcade.load_sound(":sounds:nivel1/pasos.wav"),
            3: arcade.load_sound(":sounds:nivel0/pasos.wav"),
            4: arcade.load_sound(":sounds:nivel0/pasos.wav"),
            5: arcade.load_sound(":sounds:nivel1/pasos.wav")
        }

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if not self.change_x and not self.change_y:
            return
        speed = (self.change_x ** 2 + self.change_y ** 2) ** 0.5
        self.sound_update += speed * delta_time
        if self.sound_update >= 1.0:
            sonido_actual = self.footstep_sounds.get(const.SONIDO)
            if sonido_actual:
                arcade.play_sound(sonido_actual)
            self.sound_update = 0
