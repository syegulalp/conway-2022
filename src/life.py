# cython: language_level=3
# cython: boundscheck=False
# cython: wraparound=False
# cython: initializedcheck=False
# cython: cdivision = True
# cython: always_allow_keywords =False
# cython: unraisable_tracebacks = False
# cython: binding = False

import cython

if cython.compiled:
    from cython.cimports.cpython import array as arr  # type: ignore
    from cython.cimports.libc.stdlib import rand  # type: ignore
    from cython.cimports.cpython.mem import PyMem_Malloc, PyMem_Free  # type: ignore
else:
    import array as arr
    from random import random

    def rand():
        return int(random() * 100)


@cython.cfunc
def ptr(arr_obj: arr.array) -> cython.p_char:
    array_ptr: cython.p_char = arr_obj.data.as_chars
    return array_ptr


@cython.cclass
class Life:
    lookupdata: cython.p_int
    height: cython.int
    width: cython.int
    array_size: cython.int
    display_size: cython.int
    size: cython.int
    colors: cython.uchar[4][4]

    @cython.cdivision(False)
    def __init__(self, width: cython.int, height: cython.int):
        index: cython.size_t = 0
        y: cython.int
        x: cython.int
        y3: cython.int
        x3: cython.int
        y4: cython.int

        self.colors = [
            [255, 0, 0, 255],
            [0, 0, 0, 255],
            [0, 255, 0, 255],
            [0, 0, 255, 255],
        ]

        self.height = height
        self.width = width
        self.size = height * width
        self.array_size = self.size * 8
        self.display_size = self.size * 4
        if cython.compiled:
            self.lookupdata = cython.cast(
                cython.p_int, PyMem_Malloc(self.array_size * cython.sizeof(cython.int))
            )
        else:
            self.lookupdata = arr.array("i", [0] * self.array_size)

        with cython.nogil:
            for y in range(0, height):                
                for x in range(0, width):
                    for y3 in range(y - 1, y + 2):
                        y3 = y3 % height
                        y4 = y3 * width
                        for x3 in range(x - 1, x + 2):
                            x3 = x3 % height
                            if x3 == x and y3 == y:
                                continue
                            self.lookupdata[index] = y4 + x3
                            index += 1

    def __dealloc__(self):
        PyMem_Free(self.lookupdata)

    def randomize(self, game, factor: cython.char):
        if cython.compiled:
            world: cython.p_char = ptr(game.life[game.world])
        else:
            world: arr.array = game.life[game.world]

        x: cython.size_t

        for x in range(0, self.size):
            world[x] = rand() % factor == 1

    def generation(self, game):
        total: cython.int
        x: cython.int
        index: cython.size_t = 0

        if cython.compiled:
            this_world: cython.p_char = ptr(game.life[game.world])
            other_world: cython.p_char = ptr(game.life[not game.world])
        else:
            this_world: arr.array = game.life[game.world]
            other_world: arr.array = game.life[not game.world]

        l = self.lookupdata

        with cython.nogil:
            for position in range(0, self.size):
                total = 0
                for neighbor in range(0, 8):
                    total += this_world[l[index]] > 0
                    index += 1

                if this_world[position] > 0:
                    other_world[position] = 1 if 1 < total < 4 else -1
                else:
                    other_world[position] = 2 if total == 3 else 0

        game.world = not game.world

    def render(self, game):

        if cython.compiled:
            world: cython.p_char = ptr(game.life[game.world])
            imagebuffer: cython.p_char = ptr(game.buffer)
        else:
            world: arr.array = game.life[game.world]
            imagebuffer: arr.array = game.buffer

        display_size: cython.size_t = self.display_size
        world_pos: cython.size_t = 0
        color_byte: cython.size_t
        display_pos: cython.size_t
        world_value: cython.char

        with cython.nogil:
            for display_pos in range(0, display_size, 4):
                world_value = world[world_pos]
                for color_byte in range(0, 4):
                    imagebuffer[display_pos + color_byte] = self.colors[
                        world_value + 1
                    ][color_byte]
                world_pos += 1
