from sense_hat import SenseHat

import time
import numpy as np

npcolor2 = np.array([0, 208, 193])
npcolor3 = np.array([130, 141, 152])
npcolor4 = np.array([79, 91, 102])
npcolor5 = np.array([59, 71, 82])
npcolorred = np.array([130, 41, 52])
npcoloryellow = np.array([130, 141, 52])

nplit = (npcolor2 - 7).clip(min=0)
# npdimmed = (npcolor3 - 16).clip(min=10)
npdimmed = npcolor3
# npvague = (npcolor4 - 7).clip(min=10)
npvague = npcolor4
# npdark = np.subtract(npcolor5, np.array([20, 24, 30])).clip(min=10)
# npdark = (npcolor5 - 20).clip(min=10)
npdark = np.array([12, 10, 12])
npred = npcolorred
npyellow = npcoloryellow

lit = nplit.tolist()
dimmed = npdimmed.tolist()
vague = npvague.tolist()
dark = npdark.tolist()
red = npred.tolist()
yellow = npyellow.tolist()

is_red = False


def the_x_lit(sense):
    internal_guarded_draw(sense, dark, lit)


def the_x_dimmed(sense):
    internal_guarded_draw(sense, dark, dimmed)


def the_x_vague(sense):
    if (is_red == False):
        internal_draw(sense, dark, vague)


def the_x_in_red(sense):
    internal_draw(sense, dark, red)
    is_red = True


def the_x_in_yellow(sense):
    if (is_red == False):
        internal_draw(sense, dark, yellow)


def internal_guarded_draw(sense, o, X):
    time.sleep(0.1)
    compassraw = sense.get_compass_raw()
    print("compassraw=" + str(compassraw) + "\n")
    time.sleep(0.1)
    north = sense.get_compass()
    print("north=" + str(north) + "\n")
    time.sleep(0.1)
    orientation = sense.get_orientation_degrees()
    print("p: {pitch}, r: {roll}, y: {yaw}".format(**orientation))
    if (-5.0 <= north <= 5.0):
        internal_draw(sense, o, X)
    else:
        # sense.clear()
        internal_draw(sense, o, X)


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
    if (is_red == False):
        sense.clear(dark)


def the_x_off(sense):
    sense.clear([0, 0, 0])
