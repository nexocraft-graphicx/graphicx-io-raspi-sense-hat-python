from sense_hat import SenseHat

import numpy as np

npcolor2 = np.array([0, 208, 193])
npcolor3 = np.array([130, 141, 152])
npcolor4 = np.array([79, 91, 102])
npcolor5 = np.array([59, 71, 82])
npcolorred = np.array([130, 41, 52])
npcoloryellow = np.array([130, 141, 52])

nplit = (npcolor2 - 8).clip(min=0)
npdimmed = (npcolor3 - 64).clip(min=10)
npvague = (npcolor4 - 8).clip(min=10)
npdark = np.subtract(npcolor5, np.array([20, 24, 30])).clip(min=10)
npred = npcolorred
npyellow = npcoloryellow

lit = nplit.tolist()
dimmed = npdimmed.tolist()
vague = npvague.tolist()
dark = npdark.tolist()
red = npred.tolist()
yellow = npyellow.tolist()


def the_x_lit(sense):
    internal_guarded_draw(sense, dark, lit)


def the_x_dimmed(sense):
    internal_guarded_draw(sense, dark, dimmed)


def the_x_vague(sense):
    internal_draw(sense, dark, vague)


def the_x_in_red(sense):
    internal_draw(sense, dark, red)


def the_x_in_yellow(sense):
    internal_draw(sense, dark, yellow)


def internal_guarded_draw(sense, o, X):
    north = sense.get_compass()
    print("north=" + str(north) + "\n")
    if(-5.0 <= north <= 5.0):
        internal_draw(sense, o, X)
    else:
        sense.clear()


def internal_draw(sense, o, X):
    x = [
        o, o, o, o, o, o, o, o,
        o, o, o, o, o, o, X, X,
        o, X, X, o, o, X, X, o,
        o, o, X, X, X, X, o, o,
        o, o, o, X, X, o, o, o,
        o, o, X, X, X, X, o, o,
        o, X, X, o, o, X, X, o,
        X, X, o, o, o, o, o, o
    ]
    sense.set_pixels(x)


def the_x_wiped(sense):
    sense.clear(dark)


def the_x_off(sense):
    sense.clear([0, 0, 0])
