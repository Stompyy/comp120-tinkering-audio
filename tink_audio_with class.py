import wave, struct, sys, math, winsound, pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 300
WINDOW_HEIGHT = 100

LENGTH_OF_TRACK = 1
SAMPLE_LENGTH = 44100 * LENGTH_OF_TRACK
FREQUENCY = float(1000)
SAMPLE_RATE = float(44100)
BIT_DEPTH = 32767           # 2 to the power (16 - 1 for sign) -1 for zero
load_file = True

volume = 0.5

values = []
new_file_frames = 132300

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
window.fill((255, 255, 255))
font = pygame.font.SysFont(None, 48)
levelText = font.render('m = mmmMMM', True, (0, 0, 0))
window.blit(levelText, (0, 0))
pygame.display.update()

notes = {'A' : 440 * math.pow(2, 0.0/12.0),
         'Bb': 440 * math.pow(2, 1.0/12.0),
         'B' : 440 * math.pow(2, 2.0/12.0),
         'C' : 440 * math.pow(2, 3.0/12.0),
         'C#': 440 * math.pow(2, 4.0/12.0),
         'D' : 440 * math.pow(2, 5.0/12.0),
         'D#': 440 * math.pow(2, 6.0/12.0),
         'E' : 440 * math.pow(2, 7.0/12.0),
         'F' : 440 * math.pow(2, 8.0/12.0),
         'F#': 440 * math.pow(2, 9.0/12.0),
         'G' : 440 * math.pow(2, 10.0/12.0),
         'G#': 440 * math.pow(2, 11.0/12.0)}

# notes lists
scale = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
wonderwall = ['E', 'E', 'G', 'G', 'D', 'D', 'A', 'A']
come_as_you_are = ['E', 'E', 'F', 'F#', 'F#', 'A', 'F#', 'A', 'F#', 'F#', 'F', 'E', 'E', 'B', 'E', 'B']
new_song_list = ['G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',]
walking = ['F', 'E',
           'F', 'E',
           'F', 'E',
           'F', 'E']
gunshot = ['G#']

# Attack, sustain, release values
quick = (0.02, 0.03, 0.08)
medium = (0.05, 0.1, 0.2)
slow = (0.1, 0.2, 0.3)
gunshot_speed = (0.05, 0.1, 0.8)


def clamp(value):
    if value > BIT_DEPTH:
        clamped_value = BIT_DEPTH
    elif value < - BIT_DEPTH:
        clamped_value = -BIT_DEPTH
    else:
        clamped_value = value
    return clamped_value


class Sound:
    def write_file(self, new_file_name, values_list):
        packed_list = []
        self.file = wave.open(new_file_name, 'w')
        self.file.setparams((1, 2, 44100, 132300, 'NONE', 'not compressed'))

        for i in xrange(self.file.getnframes()-1):
            packed_list.append(struct.pack("<h", int(values_list[i])))  # [0])) , unpacked_frame[1]))

        self.file.writeframes(''.join(packed_list))
        self.file.close()


class LoadSound(Sound):
    def __init__(self, name):
        """loads the file"""
        self.file = wave.open(name, "rb")

    def read_file(self):
        """returns an unpacked list of values of the sound wave"""
        unpacked_list = []
        step = BIT_DEPTH / 200  # auto tune step

        for i in xrange(self.file.getnframes()):
            current_frame = self.file.readframes(1)
            unpacked_frame = struct.unpack("<h", current_frame)
            unpacked_list.append(unpacked_frame[0])

        return unpacked_list

    def echo(self, echo_length):
        values_list = self.read_file()
        new_value_list = []
        for i in xrange(self.file.getnframes()-1):
            if i < echo_length:
                new_value_list.append(values_list[i])
            else:
                new_value_list.append(clamp(values_list[i] + values_list[i - echo_length]))
        return new_value_list

    def auto_tune(self, step_magnitude):
        values_list = self.read_file()
        new_values_list = []
        for i in xrange(self.file.getnframes()):
            value = values_list[i]
            new_value = step_magnitude * abs(value / step_magnitude)
            new_values_list.append(new_value)
        return new_values_list


class CreateSound(Sound):
    """Creates a file with name 'name' """
    def __init__(self, name):
        self.file = wave.open(name, 'w')
        self.new_values_list = []
        self.name = name

    def set_parameters(self, nchannels, sampwidth, framerate, nframes, comptype, compname):
        """sets the parameters of the .wav file"""

        # probably unnecessary to have in a function. Just do after creating an instance
        self.file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    def sound_envelope(self, frequency, attack_sustain_release):
        self.new_values_list = []
        attack_frames = attack_sustain_release[0] * SAMPLE_RATE
        sustain_frames = attack_sustain_release[1] * SAMPLE_RATE
        release_frames = attack_sustain_release[2] * SAMPLE_RATE
        total_frames = attack_frames + sustain_frames + release_frames
        current_volume = 0.0

        for frame in xrange(int(total_frames)):
            if frame < attack_frames:
                current_volume += BIT_DEPTH / attack_frames   # BIT_DEPTH is max volume
            elif frame > attack_frames + sustain_frames:
                current_volume -= BIT_DEPTH / release_frames
            else:
                current_volume = BIT_DEPTH

            pure_tone_frame = math.sin(frame * frequency / SAMPLE_RATE) * current_volume * 2.0 * math.pi
            self.new_values_list.append(struct.pack("<h", clamp(pure_tone_frame)))

        self.file.writeframes(''.join(self.new_values_list))

    def play_song(self, notes_list, attack_sustain_release):
        for note in notes_list:
            self.sound_envelope(notes[note], attack_sustain_release)
        winsound.PlaySound(self.name, winsound.SND_FILENAME)


def mmmMMM():
    """doc string"""
    list1 = []
    for i in xrange(0, SAMPLE_LENGTH):
        base_sound_wave_value = math.sin(2.0 * math.pi * FREQUENCY * (i / SAMPLE_RATE))

        # takes base value and brings up to correct BIT_DEPTH * volume
        # volume = i / SAMPLE_LENGTH increases volume over time. #leetfx
        value = base_sound_wave_value * BIT_DEPTH * i / SAMPLE_LENGTH
        list1.append(value)
        unpacked_values_list_for_echo.append(value)

        packed_value = struct.pack('<h', value)
        values.append(packed_value)
        print packed_value
    return list1


def noise():
    """doc string"""
    list1 = []
    for i in xrange(0,SAMPLE_LENGTH):
        value_1 = math.sin(math.pi * FREQUENCY * (i / float(44100))) + math.sin(
            math.pi / float(1.01) * FREQUENCY * (i / float(44100)))
        value = (value_1 * (volume * BIT_DEPTH))
        list1.append(value)
        value = (value_1 * (volume * 32000))
        packed_value = struct.pack('<h', value)
        values.append(packed_value)
    return list1


def echo_two():
    echolist = noise()
    counter = 0
    for i in echolist:
        counter +=1
        if i <1000:
            value = i
        else:
            value = i + (echolist[counter-1000]*0.8)
        if value > 32000:
            value = 32000
        packed_value = struct.pack('<h', value)
        values.append(packed_value)

new_song = CreateSound('newsong.wav')
new_song.set_parameters(1, 2, 44100, 132300, 'NONE', 'not compressed')
new_song.play_song(new_song_list, quick)
# new_song.play_song(new_song_list, medium)

gunshot_instance = CreateSound('gunsh.wav')
gunshot_instance.set_parameters(1, 2, 44100, 132300, 'NONE', 'not compressed')
gunshot_instance.play_song(gunshot, gunshot_speed)

walking_instance = CreateSound('walking.wav')
walking_instance.set_parameters(1, 2, 44100, 132300, 'NONE', 'not compressed')
walking_instance.play_song(walking, medium)
