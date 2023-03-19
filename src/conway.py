import pyglet

pyglet.options["debug_gl"] = False
pyglet.options["shadow_window"] = False
pyglet.options["vsync"] = True
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

from .timer import Timer
from .life import Life
from .constants import *
from .colors import *

import ctypes
import array
import sys

rules = {
    "life": [[0, 0, 0, 2, 0, 0, 0, 0, 0], [-1, -1, 1, 1, -1, -1, -1, -1, -1]],
    "highlife": [[0, 0, 0, 2, 0, 0, 2, 0, 0], [-1, -1, 1, 1, -1, -1, -1, -1, -1]],
    "dotlife": [[0, 0, 0, 2, 0, 0, 2, 0, 0], [1, 0, 1, 1, -1, -1, -1, -1, -1]],
    "lowdeath": [
        [0, 0, 0, 2, 0, 0, 2, 0, 2],
        [-1, -1, 1, 1, 1, -1, -1, -1, -1],
    ],
    "pedestrian": [[0, 0, 0, 2, 0, 0, 0, 0, 2], [-1, -1, 1, 1, -1, -1, -1, -1, -1]],
    "2x2": [[0, 0, 0, 2, 0, 0, 2, 0, 0], [-1, 1, 1, -1, -1, 1, -1, -1, -1]],
    "diamoeba": [[0, 0, 0, 2, 0, 2, 2, 2, 2], [-1, 1, -1, -1, -1, 1, 1, 1, 1]],
    "honey": [[0, 0, 0, 2, 0, 0, 0, 0, 2], [-1, -1, 1, 1, -1, -1, -1, -1, 1]],
}


class MyWindow(pyglet.window.Window):
    def __init__(self, *a, **ka):
        super().__init__(*a, visible=False, **ka)

        self.rule_descriptions = list(rules.keys())

        rule_name = None

        try:
            rule_switch = sys.argv.index("-r")
        except ValueError:
            pass
        else:
            try:
                rule_name = sys.argv[rule_switch + 1]
            except IndexError:
                pass

        if rule_name not in rules:
            print(rule_name, "not found. Valid rules:")
            print(" | ".join(self.rule_descriptions))
            rule_name = "life"

        rule_set = rules[rule_name]

        self.rule_name = rule_name

        self.colors = 0
        self.game_obj = Life(WIDTH, HEIGHT, all_colors[self.colors], rule_set)

        self.framerate = FRAMERATE
        self.randomization_factor = FACTOR

        self.set_location(
            self.screen.width // 2 - self.width // 2,
            self.screen.height // 2 - self.height // 2,
        )

        self.batch = pyglet.graphics.Batch()
        self.text_batch = pyglet.graphics.Batch()
        self.texture = pyglet.image.Texture.create(WIDTH, HEIGHT)

        self.label = pyglet.text.Label(
            "",
            x=8,
            y=self.height - 8,
            anchor_x="left",
            anchor_y="top",
            multiline=True,
            width=self.width // 2,
            batch=self.text_batch,
            color=(255, 255, 0, 255),
        )

        self.life = [array.array("b", b"\x00" * WIDTH * HEIGHT) for _ in range(2)]
        self.buffer = array.array("B", b"\x00" * WIDTH * HEIGHT * 4)

        self.sprites = []
        for _ in range(4):
            sprite = pyglet.sprite.Sprite(self.texture, 0, 0, batch=self.batch)
            sprite.scale = ZOOM
            self.sprites.append(sprite)

        self.sprites[1].x = -WIDTH * ZOOM
        self.sprites[2].x = -WIDTH * ZOOM
        self.sprites[2].y = -HEIGHT * ZOOM
        self.sprites[3].y = -HEIGHT * ZOOM

        self.world = 0

        self.game_obj.randomize(self, self.randomization_factor)

        self.life_timer = Timer()
        self.render_timer = Timer()
        self.draw_timer = Timer()

        self.zoom = ZOOM

        pyglet.clock.schedule_interval(self.run, 1 / self.framerate)
        pyglet.clock.schedule_interval(self.get_avg, 1.0)

        self.label.text = f"Rule set: {self.rule_name}"

        self.running = True
        self.set_visible(True)

    def get_avg(self, *a):
        self.label.text = (
            f"Rule set: {self.rule_name}\n"
            f"New generation: {self.life_timer.avg:.7f}\n"
            f"Display rendering time: {self.render_timer.avg:.7f}\n"
            f"Draw time: {self.draw_timer.avg:.7f}\n"
            f"Framerate: {((1/60)/self.life_timer.avg)*60:.2f}\n\n"
            "Click and drag in window to reposition\nTab: toggle HUD\n0-9: alter generation speed\n"
            "Space: randomize field\np: Pause/unpause\n[ or ]: switch color palette\n\n"
            f"Rules: {' | '.join(self.rule_descriptions)}"
        )

    def on_mouse_drag(self, x, y, dx, dy, *a):
        for _ in self.sprites:
            _.x = ((_.x + dx) % (WIDTH * ZOOM * 2)) - WIDTH * ZOOM
            _.y = ((_.y + dy) % (HEIGHT * ZOOM * 2)) - HEIGHT * ZOOM

    def on_key_press(self, symbol, modifiers):
        print(symbol, modifiers)
        if symbol == 65289:
            self.label.visible = not self.label.visible
        elif 48 <= symbol <= 57:
            if modifiers == 1:
                self.randomization_factor = symbol - 48
            else:
                self.framerate = int(((symbol - 47) / 10) * FRAMERATE)
                if self.running:
                    pyglet.clock.unschedule(self.run)
                    pyglet.clock.schedule_interval(self.run, 1 / self.framerate)

        elif symbol in (91, 93):
            direction = symbol - 92
            self.colors = (self.colors + direction) % len(all_colors)
            self.game_obj.set_colors(all_colors[self.colors])
            if not self.running:
                self.on_draw()
        elif symbol == 32:
            self.game_obj.randomize(self, self.randomization_factor)
            if not self.running:
                self.run()
        if self.running:
            if symbol == 112 or symbol == 46:
                self.running = not self.running
                pyglet.clock.unschedule(self.run)
        else:
            if symbol == 46:
                self.run()
            elif symbol == 112:
                self.running = not self.running
                pyglet.clock.schedule_interval(self.run, 1 / self.framerate)

        return super().on_key_press(symbol, modifiers)

    def run(self, *a):
        with self.life_timer:
            self.game_obj.generation(self)
        self.invalid = True

    def on_draw(self):
        self.invalid = False

        with self.render_timer:
            self.game_obj.render(self)
        self.texture.blit_into(
            pyglet.image.ImageData(WIDTH, HEIGHT, "RGBA", self.buffer.tobytes()),
            0,
            0,
            0,
        )
        with self.draw_timer:
            self.clear()
            self.batch.draw()
            self.text_batch.draw()


def main():
    w = MyWindow(int(WIDTH * ZOOM), int(HEIGHT * ZOOM))
    import gc

    try:
        ctypes.windll.winmm.timeBeginPeriod(1)
    except:
        pass
    gc.freeze()
    pyglet.app.run()


if __name__ == "__main__":
    main()
