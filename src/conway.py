WIDTH = 200
HEIGHT = 200
ZOOM = 5
FRAMERATE = 30

import ctypes
import array

import pyglet

pyglet.options["debug_gl"] = False
pyglet.image.Texture.default_mag_filter = pyglet.gl.GL_NEAREST

from timer import Timer
from life import Life


class MyWindow(pyglet.window.Window):
    def __init__(self, *a, **ka):
        super().__init__(*a, **ka)
        self.game_obj = Life(WIDTH, HEIGHT)

        self.batch = pyglet.graphics.Batch()
        self.texture = pyglet.image.Texture.create(WIDTH, HEIGHT)

        self.life = [array.array("b", b"\x00" * WIDTH * HEIGHT) for _ in range(2)]
        self.buffer = array.array("B", b"\x00" * WIDTH * HEIGHT * 4)

        self.sprites = []
        for _ in range(4):
            self.sprites.append(
                pyglet.sprite.Sprite(
                    self.texture,
                    0,
                    0,
                    batch=self.batch,
                )
            )

        self.sprites[1].x = -WIDTH
        self.sprites[2].x = WIDTH
        self.sprites[2].y = HEIGHT
        self.sprites[3].y = -HEIGHT

        self.world = 0

        self.game_obj.randomize(self, 5)

        self.life_timer = Timer()
        self.render_timer = Timer()
        self.draw_timer = Timer()

        self.zoom = ZOOM

        pyglet.clock.schedule_interval(self.run, 1 / FRAMERATE)
        pyglet.clock.schedule_interval(self.get_avg, 1.0)

        print("New generation / Display rendering / Draw")

        self.running = True

    def get_avg(self, *a):
        print(self.life_timer.avg, self.render_timer.avg, self.draw_timer.avg)

    def on_mouse_drag(self, x, y, dx, dy, *a):
        for _ in self.sprites:
            _.x = (_.x + (dx / ZOOM)) % (WIDTH * 2) - WIDTH
            _.y = (_.y + (dy / ZOOM)) % (HEIGHT * 2) - HEIGHT

    def on_key_press(self, symbol, modifiers):
        if self.running:
            if symbol == 112:
                self.running = not self.running
                pyglet.clock.unschedule(self.run)
            if symbol == 32:
                self.game_obj.randomize(self, 5)
        else:
            if symbol == 32:
                self.run()
            elif symbol == 112:
                self.running = not self.running
                pyglet.clock.schedule_interval(self.run, 1 / FRAMERATE)

        return super().on_key_press(symbol, modifiers)

    def run(self, *a):
        with self.life_timer:
            self.game_obj.generation(self)

        with self.render_timer:
            self.game_obj.render(self)
        self.texture.blit_into(
            pyglet.image.ImageData(WIDTH, HEIGHT, "RGBA", self.buffer.tobytes()),
            0,
            0,
            0,
        )
        self.invalid = True

    def on_draw(self):
        self.invalid = False
        with self.draw_timer:
            pyglet.gl.glViewport(
                0, 0, WIDTH * (self.zoom ** 2), HEIGHT * (self.zoom ** 2)
            )
            self.clear()
            self.batch.draw()


def main():
    w = MyWindow(WIDTH * ZOOM, HEIGHT * ZOOM)
    import gc

    try:
        ctypes.windll.winmm.timeBeginPeriod(2)
    except:
        pass
    gc.freeze()
    pyglet.app.run()


if __name__ == "__main__":
    main()
