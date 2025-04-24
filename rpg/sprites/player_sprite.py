import arcade

from rpg.sprites.chacter_sprite1 import CharacterSprite_one
from rpg.sprites.character_sprite import CharacterSprite


class PlayerSprite(CharacterSprite_one):
    def __init__(self, sheet_name):
        super().__init__(sheet_name)
        self.sound_update = 0
        self.footstep_sound = arcade.load_sound(":sounds:footstep00.wav") #cambialo reventado de mierda

    def on_update(self, delta_time):
        super().on_update(delta_time)

        if not self.change_x and not self.change_y:
            self.sound_update = 0
            return

        if self.should_update > 3:
            self.sound_update += 1
            print("a")

        if self.sound_update >= 3:
            arcade.play_sound(self.footstep_sound)
            self.sound_update = 0
