from microbit import *


def debug(text):
    pass
    # print(text)


def Promise():
    while True:
        debug('promise: Waiting for resolution')
        resolved = yield
        if resolved:
            debug('promise: resolved')
            yield
            break


class EventLoop:
    __slots__ = (
        'call_after',
        'tasks',
        'todo',
    )

    def __init__(self):
        self.tasks = []
        self.call_after = []

    def sleep(self, millis, promise=None):
        if promise is None:
            promise = Promise()

        debug('sleep({!r})'.format(millis))

        t = running_time()

        self.call_after.append((t + millis, promise.send, [True]))
        return promise


loop = EventLoop()


def run_loop():
    while True:
        debug('run_loop: step')
        current_time = running_time()

        taken_care_of = []

        for reminder in loop.call_after:
            time, func, args = reminder

            if time < current_time:
                debug('Calling {!r} after {!r}'.format(func, time))
                taken_care_of.append(reminder)
                func(*args)

        for reminder in taken_care_of:
            loop.call_after.remove(reminder)

        try:
            task = loop.tasks.pop(0)
            if isinstance(task, tuple):
                task = task[0](*task[1])
        except IndexError:
            debug('No tasks')
            break

        try:
            #debug('run_loop: task.send(None), task={!r}'.format(task))
            res = task.send(None)
            #debug('run_loop: task.send(None), res={!r}'.format(res))
            loop.tasks.append(task)
        except StopIteration:
            debug('run_loop: StopIteration')


def coroutine(func):
    """

    :param func: Generator
    :return:
    """
    def wrapper(*args, **kwargs):
        task = func(*args, **kwargs)
        loop.tasks.append(task)
        return task

    return wrapper


@coroutine
def print_number(number):
    debug('number: sleeping')
    res = yield from loop.sleep(1000)
    debug('number: {!r}'.format(number))


@coroutine
def sleep_print(millis):
    yield from loop.sleep(millis)
    print(millis)


@coroutine
def do_stuff():
    debug('main')
    yield from print_number(1)

t_start = running_time()

sleep_print(300)
sleep_print(200)
sleep_print(700)
sleep_print(500)
sleep_print(100)
print('Starting')
run_loop()

print('took: {}'.format(running_time() - t_start))

