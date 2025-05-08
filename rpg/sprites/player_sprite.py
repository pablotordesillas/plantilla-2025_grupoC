import arcade

from rpg.sprites.chacter_sprite1 import CharacterSprite_one
from rpg.sprites.character_sprite import CharacterSprite


class PlayerSprite(CharacterSprite_one):
    def __init__(self, sheet_name, sheet_name2, sheet_name3, sheet_name4):
        super().__init__(sheet_name, sheet_name2, sheet_name3, sheet_name4)
        self.sound_update = 0
        self.footstep_sound = arcade.load_sound(":sounds:nivel1/pasos.mp3") #cambialo reventado de mierda
        print(self.footstep_sound)

    def on_update(self, delta_time):
        super().on_update(delta_time)
        if not self.change_x and not self.change_y:
            #self.sound_update = 0
            #print("a")
            return

        if self.should_update > 4:
            self.sound_update += 1
            print(self.sound_update)

        if self.sound_update >= 6:
            arcade.play_sound(self.footstep_sound)
            self.sound_update = 0
            print("c")

