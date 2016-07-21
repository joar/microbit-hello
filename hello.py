import microbit


# TODO: Use namedtuples
class State:
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
    def __init__(self, button_a=None, button_b=None, interrupt=None):
        self.button_a = button_a
        self.button_b = button_b
        self.interrupt = interrupt


DEFAULT_HANDLERS = Handlers(button_a=lambda: STATE.start_next())

STATE = State()
HANDLERS = DEFAULT_HANDLERS


class Input(Exception):
    name = 'interrupt'


class ButtonA(Input):
    name = 'button_a'


class ButtonB(Input):
    name = 'button_b'


def program(func):
    STATE.programs.append(func)

    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)

    for i in ['name', 'qualname', 'annotations', 'doc', 'module']:
        name = '__{}__'.format(i)
        try:
            setattr(wrapper, name, getattr(func, name))
        except AttributeError:
            pass

    try:
        wrapper.__dict__.update(func.__dict__)
    except AttributeError:
        pass

    return wrapper


def handle(event, *args, **kwargs):
    handler = getattr(HANDLERS, event)

    if handler is not None:
        print('Executing handler {!r}(*{!r}, **{!r}) for {!r}'.format(
            handler, args, kwargs, event))
        return handler(*args, **kwargs)


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


def render_clocks(self):
    microbit.display.show(microbit.Image.ALL_CLOCKS, loop=True, delay=100)


@program
def draw_gradient1():
    offset = 0
    max_value = 9
    max_index = 5

    while True:
        for x in range(0, 5):
            for y in range(0, 5):
                pos = y
                offset_pos = (offset + pos) % max_index
                relative_pos = offset_pos / max_index
                value = round(relative_pos * max_value)
                microbit.display.set_pixel(x, y, value)

        yield from sleep(100)
        offset += 1
        offset %= max_index


@program
def draw_gradient2():
    offset = 0
    max_value = 9
    max_index = 5

    while True:
        for x in range(0, 5):
            for y in range(0, 5):
                pos = x * y
                offset_pos = (offset + pos) % max_index
                relative_pos = offset_pos / max_index
                value = round(relative_pos * max_value)
                microbit.display.set_pixel(x, y, value)

        yield from sleep(100)
        offset += 1
        offset %= max_index


@program
def long_running():
    while True:
        microbit.display.scroll('Hello', wait=False)
        yield from sleep(1000 * 1000)


print(STATE)

while True:
    if STATE.active is None:
        STATE.start_next()

    try:
        next(STATE.active)
    except Input as exc:
        print('Input: {!r}'.format(exc))
        handle(exc.name)
    except StopIteration:
        print('{!r} stopped'.format(STATE.active))
        STATE.active = None
