import radio
from microbit import display, Image

radio.config(channel=73, length=251)
radio.on()

while True:
    msg = radio.receive()
    if msg:
        # TODO: validate that it is a valid frame
        try:
            display.show(eval(msg))
        except Exception as e:
            print(e.message)
            pass
