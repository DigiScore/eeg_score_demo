import score_draw
from random import random, choice, seed
from time import sleep

from random import choice
from brainbit import BrainbitReader

from neoscore.core import neoscore
from neoscore.core.music_font import MusicFont

from neoscore.core.rich_text import RichText
from neoscore.core.text import Text
from neoscore.core.units import ZERO, Mm
from neoscore.western.staff import Staff
from neoscore.western.chordrest import Chordrest
from neoscore.western.clef import Clef
from neoscore.western.duration import Duration
from neoscore.western.barline import Barline


class Main:
    def __init__(self):
        # start brainbit reading
        self.bb = BrainbitReader()
        self.bb.start()

        # get all midi note lists for s a t b
        self.s, self.a, self.t, self.b = score_draw.get_midi_lists()
        self.part_list = [self.s, self.a, self.t, self.b]

        # start neoscore
        neoscore.setup()

        # build digital score UI
        self.make_UI()

        # build first bar
        self.eegdata = self.bb.read()
        self.beat_size = 20
        self.build_bar(1)
        self.build_bar(2)

    def build_bar(self, bar):
        if bar == 1:
            start_pos = Mm(10)
            self.notes_on_staff_list_1 = []

        else:
            start_pos = Mm(100)
            self.notes_on_staff_list_2 = []

        # populate the bar on each part until full
        for i, part in enumerate(self.part_list):
            seed(self.eegdata[i])
            # one beat = 20 mm's
            note_duration_sum = 0
            while note_duration_sum < 80:
                # position in bar
                pos_x = Mm(note_duration_sum) + start_pos

                # 70% chance of note or rest
                if random() >= 0.3:
                    # get a random note from original source list,
                    pitch, octave, raw_duration = self.get_note(part)

                    # double length of original duration
                    raw_duration *= 2

                    # calc neonote (octave and name)
                    if pitch[-1] == "#":
                        pitch = f"{pitch[0]}s"
                    elif pitch[-1] == "-":
                        pitch = f"{pitch[0]}f"

                    if octave > 4:
                        ticks = octave - 4
                        for tick in range(ticks):
                            pitch += "'"
                    elif octave < 4:
                        for tick in range(octave):
                            pitch += ","

                    # get name & octave as neoscore format
                    neoname = [pitch.lower()]

                    # calculate duration
                    if isinstance(raw_duration, float):
                        raw_duration, neoduration = self.calc_duration(raw_duration)
                    else:
                        raw_duration, neoduration = self.calc_duration(1)
                    length = raw_duration * self.beat_size

                # or its a crotchet rest
                else:
                    length = 20
                    neoduration = Duration(1, 4)
                    neoname = []

                    # print note on neoscore
                if note_duration_sum + length > 80:
                    break
                else:
                    n = Chordrest(pos_x, self.staff_list[i], neoname, neoduration)
                    if bar == 1:
                        self.notes_on_staff_list_1.append(n)
                    else:
                        self.notes_on_staff_list_2.append(n)

                note_duration_sum += length

    def calc_duration(self, raw_duration):
        if raw_duration < 0.25:
            neo_duration = (1, 16)
        elif raw_duration == 0.25:
            neo_duration = (1, 16)
        elif raw_duration == 0.5:
            neo_duration = (1, 8)
        elif raw_duration == 0.75:
            neo_duration = (3, 8)
        elif raw_duration == 1:
            neo_duration = (1, 4)
        elif raw_duration == 1.5:
            neo_duration = (3, 4)
        elif raw_duration == 2:
            neo_duration = (1, 2)

        else:
            neo_duration = (1, 4)
            raw_duration = 1

        return raw_duration, Duration(neo_duration[0], neo_duration[1])

    def get_note(self, part):
        # seed(eegdata[i])
        pitch, octave, duration = choice(part)
        # calc neonote (octave and name)
        if pitch[-1] == "#":
            pitch = f"{pitch[0]}s"
        elif pitch[-1] == "-":
            pitch = f"{pitch[0]}f"

        if 2 <= octave <= 6:
            octave = 4
        if octave > 4:
            ticks = octave - 4
            for tick in range(ticks):
                pitch += "'"
        elif octave < 4:
            for tick in range(octave):
                pitch += ","

        pitch = pitch.lower()
        return pitch, octave, duration

    def make_UI(self):
        annotation = """
        DEMO digital score using EEG brain wave data
        and deconstructed source music.
        Players instructions:
        Dynamics = piano
        Time Sig = 4/4
        Tempo = 60 BPM
        
        """
        # add text at top
        RichText((Mm(1), Mm(1)), None, annotation, width=Mm(120))
        # mfont = MusicFont("Bravura", Mm)
        self.eeg_output = Text((ZERO, Mm(30)), None, "")

        # make 4 2 bar staves
        self.s_staff = Staff((ZERO, Mm(70)), None, Mm(180))
        self.a_staff = Staff((ZERO, Mm(90)), None, Mm(180))
        self.t_staff = Staff((ZERO, Mm(110)), None, Mm(180))
        self.b_staff = Staff((ZERO, Mm(130)), None, Mm(180))
        self.staff_list = [self.s_staff, self.a_staff, self.t_staff, self.b_staff]

        # add barlines
        Barline(Mm(90), [self.s_staff, self.b_staff])
        Barline(Mm(180), [self.s_staff, self.b_staff])

        # add clefs
        Clef(ZERO, self.s_staff, "treble")
        Clef(ZERO, self.a_staff, "treble")
        Clef(ZERO, self.t_staff, "alto")
        Clef(ZERO, self.b_staff, "bass")

        # mark conductor points
        bar1_origin = Mm(10)
        self.conductor_1_1 = Text((bar1_origin, Mm(45)), None, "1")
        self.conductor_1_2 = Text((bar1_origin + Mm(40), Mm(45)), None, "2")
        self.conductor_2_1 = Text((bar1_origin + Mm(90), Mm(45)), None, "3")
        self.conductor_2_2 = Text((bar1_origin + Mm(130), Mm(45)), None, "4")
        self.conductor_list = [self.conductor_1_1,
                               self.conductor_1_2,
                               self.conductor_2_1,
                               self.conductor_2_2
                               ]

    def change_beat(self, beat):
        if beat > 4:
            beat -= 4
        # flatten all scales
        for b in self.conductor_list:
            b.scale = 1
        # boost the beat
        self.conductor_list[beat-1].scale = 3

    def refresh_func(self, time):
        # get data from brainbit
        self.eegdata = self.bb.read()
        # print(f"EEG read = {data}")
        self.eeg_output.text = f"eeg output = T2 {round(self.eegdata[0], 2)}; " \
                               f"T4 {round(self.eegdata[1], 2)}; " \
                               f"N1 {round(self.eegdata[2], 2)}; " \
                               f"N2 {round(self.eegdata[3], 2)}"

        # calc which beat and change score
        beat = (int(time) % 8) + 1 # 8 beats = 2 bars
        self.change_beat(beat)
        if beat == 1:
            for n in self.notes_on_staff_list_2:
                n.remove()
            self.build_bar(2)
        elif beat == 5:
            for n in self.notes_on_staff_list_1:
                n.remove()
            self.build_bar(1)
        # sleep(0.05)


if __name__ == "__main__":
    run = Main()
    neoscore.show(run.refresh_func,
                  display_page_geometry=False)