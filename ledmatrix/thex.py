from sense_hat import SenseHat

def draw_the_x(sense):
    O = [12, 12, 12]  # Dark
    X = [100, 100, 100]  # Light
    x = [
        O, O, O, O, O, O, O, O,
        O, O, O, O, O, O, X, X,
        O, X, X, O, O, X, X, O,
        O, O, X, X, X, X, O, O,
        O, O, O, X, X, O, O, O,
        O, O, X, X, X, X, O, O,
        O, X, X, O, O, X, X, O,
        X, X, O, O, O, O, O, O
    ]
    sense.set_pixels(x)


def wipe_the_x(sense):
    O = [12, 12, 12]  # Dark
    sense.clear(O)
