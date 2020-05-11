from pyo import *
from config import *
import random
from utils import *

#dynamically keep track of current song's metadata
class GeneratorState:

    def __init__(self, median, history=None):
        self.history = history if history is not None else []
        self.median = median

    def update(self,freq, midi, dur):
        self.history.append((freq, midi, dur))

    def get_last_midi(self):
        return self.history[-1][1] if self.history else None

    def get_inertia(self, steps=2):
        assert steps >= 2
        if len(self.history) <= 1:
            return random.choice([-1, 1])
        if steps > len(self.history):
            steps = len(self.history)

        return 1 if self.history[-1] > self.history[-steps] else -1

    def get_last_dur(self):
        return self.history[-1][2] if self.history else None

    def get_median_relation(self, steps=2):
        assert steps >= 2

        if len(self.history) <= 1:
            return -1

        a = self.history[-steps][1]
        b = self.history[-1][1]
        if a == self.median:
            return 0
        if (a < self.median and b > self.median) or (a > self.median and b < self.median):
            return 1
        if b == self.median:
            return 2
        if (a < self.median and b > a and b < self.median) or (a > self.median and a < b and b > self.median):
            return 3
        return -1

class MusicGenerator:
    midi_vals = list(range(30, 90))

    def __init__(self, pitch_proximity=UNIFORM_PITCH_PROXIMITY, percent_ascending=None, step_inertia=None,
            direction_change=None, melodic_regression=None, melodic_arch=None, bpm=120, diatonoic_bias=None, duration_inertia=None):
         self.server = Server().boot()
         self.amp = Fader(fadein=0.005, fadeout=0.05, mul=.15)
         self.osc = RCOsc(freq=[100, 100], mul=self.amp).out()
         self.pat = None
         self.state = GeneratorState(self.midi_vals[len(self.midi_vals) // 2])
         self.pitch_proximity = pitch_proximity
         self.percent_ascending = percent_ascending
         self.step_inertia = step_inertia
         self.direction_change = direction_change
         self.melodic_regression = melodic_regression
         self.melodic_arch = melodic_arch
         self.bpm = bpm
         self.diatonoic_bias = diatonoic_bias
         self.duration_inertia = duration_inertia
         self.generator_fn = self.get_generator_function()

    def get_ascend_probability(self, interval):
        if interval == 0:
            return 1

        divisor = 0
        pa_ascending_prob = 0
        if self.percent_ascending:
            pa_ascending_prob = self.percent_ascending[interval] * self.percent_ascending['weight']
            divisor += self.percent_ascending['weight']

        si_ascending_prob = 0
        if self.step_inertia:
            inertia = self.state.get_inertia(self.step_inertia['step_size'])
            si_ascending_prob = self.step_inertia[inertia] * self.step_inertia['weight']
            divisor += self.step_inertia['weight']

        pcid_ascending_prob = 0
        if self.direction_change:
            inertia = self.state.get_inertia(2)
            pcid_ascending_prob = self.direction_change[interval]  if inertia == -1 else 1 - self.direction_change[interval]
            pcid_ascending_prob *= self.direction_change['weight']
            divisor += self.direction_change['weight']

        mr_ascending_prob = 0
        if self.melodic_regression:
            median_rel = self.state.get_median_relation(2)
            if median_rel >= 0:
                inertia = self.state.get_inertia(2)
                mr_ascending_prob = self.melodic_regression[median_rel] if inertia == -1 else 1 - self.melodic_regression[median_rel]
                mr_ascending_prob *= self.melodic_regression['weight']
                divisor += self.melodic_regression['weight']

        if divisor == 0:
            return .5

        return (pa_ascending_prob + si_ascending_prob + pcid_ascending_prob) / divisor

    def get_generator_function(self):
        major_scale = set(get_major_scale(60, 30, 90))
        prob_table = {}
        dur_classes = [4, 3, 2, 3/2, 1, 1/2, 1/4]

        def next_note():
            # Choose a duration for this event.
            dur_weights =  [.1, .1, .05, .2, .4, .25, .1]
            if self.duration_inertia is not None:
                last_dur = self.state.get_last_dur()
                if last_dur is None:
                    last_dur = .5
                last_dur_index = dur_classes.index(last_dur)
                for i in range(len(dur_classes)):
                    dur_weights[i] = self.duration_inertia['maintain_duration'] * (self.duration_inertia['fall_off'] ** abs(last_dur_index - i))

            timing_dur = random.choices(dur_classes, dur_weights, k=1)[0]
            dur = beatToDur(timing_dur, self.bpm)

            # Assigns the new duration to the envelope.
            self.amp.dur = dur
            # Assigns the new duration to the caller, thus the next function call
            # will be only after the current event has finished.
            self.pat.time = dur

            # Choose a new frequency.
            last_midi = self.state.get_last_midi()
            if last_midi is None:
                last_midi = self.midi_vals[len(self.midi_vals) // 2]

            for interval in range(-12, 13):
                potential_midi = last_midi + interval
                if potential_midi > self.midi_vals[-1] or potential_midi < self.midi_vals[0]:
                    prob = 0
                else:
                    prob = (1 - self.get_ascend_probability(abs(interval))) * self.pitch_proximity[abs(interval)]
                    if self.diatonoic_bias is not None and potential_midi not in major_scale:
                        prob *= 1 - self.diatonoic_bias['bias']
                prob_table[interval] = prob

            interval = get_table_sampler(prob_table)()
            midi = last_midi + interval
            freq = midiToHz(midi)
            self.state.update(freq, midi, timing_dur)

            print("o" * (midi // 5))

            # Replace oscillator's frequencies.
            self.osc .freq = [freq, freq * 1.003]

            # Start the envelope.
            self.amp.play()

        return next_note

    def play(self):
        self.pat = Pattern(function=self.generator_fn, time=0.25).play()
        self.server.gui(locals())

if __name__ == '__main__':
    generator = MusicGenerator(pitch_proximity=PITCH_PROXIMITY,
                                percent_ascending=PERCENT_ASCENDING,
                                step_inertia=STEP_INERTIA,
                                direction_change=PERCENT_CHANGE_IN_DIRECTION_BY_INTERVAL,
                                melodic_regression=MELODIC_REGRESSION,
                                melodic_arch=MELODIC_ARCH,
                                diatonoic_bias=DIATONIC_BIAS,
                                duration_inertia=DURATION_INERTIA,
                                bpm=160)
    generator.play()
