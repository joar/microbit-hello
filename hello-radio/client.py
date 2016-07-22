import math
import microbit
import radio


radio.on()
radio.config(channel=73,
             power=7,
             length=251)


now = microbit.running_time


def hypot(x, y):
    return math.sqrt(math.pow(x, 2) + math.pow(y, 2))


def send_image(image):
    radio.send(repr(image))


# TODO: Use namedtuples
class State:
    __slots__ = (
        'programs',
        'active',
        '_active_index',
    )

    def __init__(self, programs=None):
        self.programs = programs or []
        self.active = None
        self._active_index = 0

    def start_next(self):
        self._active_index = ((self._active_index + 1) %
                              (len(self.programs)))
        try:
            new_program = self.programs[self._active_index]
            print('Starting {!r}'.format(new_program))
            self.active = new_program()
            print('Started {!r}'.format(self.active))
        except IndexError:
            print('No programs available')

    def __repr__(self):
        return '<State active={!r} programs={!r}>'.format(self.active,
                                                          self.programs)


class Handlers:
    __slots__ = (
        'button_a',
        'button_b',
        'interrupt',
    )

    def __init__(self, button_a=None, button_b=None, interrupt=None):
        self.button_a = button_a
        self.button_b = button_b
        self.interrupt = interrupt


DEFAULT_HANDLERS = Handlers(button_a=lambda *a: STATE.start_next())

STATE = State()
HANDLERS = DEFAULT_HANDLERS


class Input(Exception):
    name = 'interrupt'


class ButtonA(Input):
    name = 'button_a'


class ButtonB(Input):
    name = 'button_b'


def program(func):
    """Registering decorator for programs"""
    STATE.programs.append(func)
    return func


def check_input():
    button_a = microbit.button_a.get_presses()
    button_b = microbit.button_b.get_presses()

    if button_a:
        raise ButtonA

    if button_b:
        raise ButtonB


def sleep(millis):
    t = microbit.running_time()
    while microbit.running_time() < t + millis:
        check_input()
        yield


brightness_max = 9
half_brightness_max = brightness_max / 2
two_pi = math.pi * 2

origo_x, origo_y = 2, 2

max_distance = hypot(origo_x, origo_y)
double_max_distance = max_distance * 2
gradient3_image = microbit.Image().copy()


@program
def draw_gradient0():
    offset = 0
    last_t = now()

    while True:
        for x in range(0, 5):
            dist_x = x - origo_x
            for y in range(0, 5):
                dist_y = y - origo_y

                distance = (math.fabs(hypot(dist_x, dist_y)) /
                            double_max_distance)
                distance = (distance + offset) % 1

                sin = math.sin(distance * two_pi - math.pi)

                value = round(sin * half_brightness_max + half_brightness_max)

                gradient3_image.set_pixel(x, y, value)

        send_image(gradient3_image)
        microbit.display.show(gradient3_image)

        t_now = now()
        delta_t = t_now - last_t
        offset += delta_t * 0.001
        last_t = t_now
        yield from sleep(10)


print(STATE)

while True:
    if STATE.active is None:
        STATE.start_next()

    try:
        next(STATE.active)
    except Input as exc:
        print('Input: {!r}'.format(exc))
        handler = getattr(HANDLERS, exc.name)

        if handler is not None:
            print('Executing handler {!r}({!r}) for {!r}'.format(
                handler, exc, exc.name))
            handler(exc)
    except StopIteration:
        print('{!r} stopped'.format(STATE.active))
        STATE.active = None
