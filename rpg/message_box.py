import arcade

from rpg.constants import MESSAGE_BOX_FONT_SIZE, MESSAGE_BOX_MARGIN


class MessageBox:
    def __init__(self, view, message, value:int):
        self.value = value
        if value==0:
            self.message = message
            self.view = view
            self.width = 500
            self.height = 50
        elif value == 1:
            self.message = message
            self.view = view
            self.width = 800
            self.height = 300
        elif value == 2:
            self.message = message
            self.view = view
            self.width = 800
            self.height = 100
        else:
            self.message = message
            self.view = view
            self.width = 500
            self.height = 200


    def on_draw(self):
        if self.value == 0 or self.value == 1:
            cx = self.view.window.width / 2
            cy = self.view.window.height / 2
        else:
            cx = self.view.window.width/2
            cy = self.view.window.height/4

        arcade.draw_rectangle_filled(
            cx,
            cy,
            self.width,
            self.height,
            (41,41,41,255),
        )
        arcade.draw_rectangle_outline(
            cx,
            cy,
            self.width,
            self.height,
            (19,19,19,255),
            6,
        )

        arcade.draw_text(
            self.message,
            cx,
            cy,
            arcade.color.WHITE,
            MESSAGE_BOX_FONT_SIZE,
            anchor_x="center",
            anchor_y="center",
            align="center",
            width=500,
        )

    def on_key_press(self, _key, _modifiers):
        self.view.close_message_box()
