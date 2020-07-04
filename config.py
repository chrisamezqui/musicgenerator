UNIFORM_PITCH_PROXIMITY = {
    0 : .08,
    1 : .08,
    2 : .08,
    3 : .08,
    4 : .08,
    5 : .08,
    6 : .08,
    7 : .08,
    8 : .08,
    9 : .07,
    10 : .07,
    11 : .07,
    12 : .07
}

PITCH_PROXIMITY = {
    0 : .2,
    1 : .12,
    2 : .33,
    3 : .1,
    4 : .06,
    5 : .08,
    6 : .01,
    7 : .03,
    8 : .01,
    9 : .02,
    10 : .01,
    11 : .02,
    12 : .01
}

PERCENT_ASCENDING = {
    1 : .47,
    2 : .44,
    3 : .44,
    4 : .47,
    5 : .62,
    6 : .48,
    7 : .42,
    8 : .48,
    9 : .54,
    10 : .49,
    11 : .49,
    12 : .65,
    'weight' : 1
}

#chance to ascend given inertia
STEP_INERTIA = {
    -1 : .49,
    1 : .7,
    'step_size' : 2,
    'weight' : 1
}

PERCENT_CHANGE_IN_DIRECTION_BY_INTERVAL = {
    1 : .35,
    2 : .28,
    3 : .54,
    4 : .4,
    5 : .48,
    6 : .8,
    7 : .6,
    8 : .65,
    9 : .55,
    10 : .82,
    11 : .75,
    12 : .7,
    'weight' : 1
}

#probability of direction reversal
MELODIC_REGRESSION = {
    0 : .8, #median-departing
    1 : .72, #median-crossing
    2 : .6, #median-landing
    3 : .3, #median-approaching
    -1 : .5, #other
    'weight' : .5
}

MELODIC_ARCH = {
    1 : 7.78,
    2 : 8.7,
    3 : 8.9,
    4 : 8.91,
    5 : 8.79,
    6 : 8.55,
    7: 7.45,
    'weight' : 1
}

DIATONIC_BIAS = {
    'bias' : .2
}

DURATION_INERTIA = {
    'maintain_duration' : .4,
    'fall_off' : .7
}
