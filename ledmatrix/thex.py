from sense_hat import SenseHat


def the_x_lit(sense):
    O = [59, 71, 82]  # dark
    X = [0, 208, 193]  # lit
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


def the_x_dimmed(sense):
    O = [59, 71, 82]  # dark
    X = [130, 141, 152]  # dimmed
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


def the_x_in_red(sense):
    O = [59, 71, 82]  # dark
    X = [130, 41, 52]  # red
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


def the_x_in_yellow(sense):
    O = [59, 71, 82]  # dark
    X = [130, 141, 52]  # yellow
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


def the_x_wiped(sense):
    O = [59, 71, 82]  # dark
    sense.clear(O)


def the_x_off(sense):
    O = [0, 0, 0]  # off
    sense.clear(O)
