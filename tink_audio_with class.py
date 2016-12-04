import wave, struct, sys, math, winsound, pygame
from pygame.locals import *

"""write a list of notes to play, and a tuple of the three time periods:
    ________
  /         \
 /           \
/             \
attack
    sustain
        release
e.g. (0.2, 0.5, 0.4)

Declare an instance of CreateSound('filename.wav')
then:
instance.play_sound(notes_list, tuple)
You'll see at the end
Can't get anything to sound decent though
probably not imaginative enough

Alternatively can create a custom note with def custom_note(n)
where if n > 12 gets very high pitched or n < 0 very low

instance.sound_envelope(frequency, tuple) creates the sine wave so maybe
directly messing with the frequency argument will be best for gunshots etc.
Need to tell it to play like with new_gun instance below at the bottom.

easy enough but annoyingly difficult to get anything to sound decent

volume is an outside variable: volume
Didn't see any need to pass it into sound_envelope function as an argument
but it's easily enough done. Volume is multiplied in the pure_tone_frame = ... line
just careful not to mix it up with the current_volume variable. That's the
envelope bit.
"""

pygame.init()
pygame.mixer.init()

LENGTH_OF_TRACK = 1
SAMPLE_LENGTH = 44100 * LENGTH_OF_TRACK
FREQUENCY = float(1000)
SAMPLE_RATE = float(44100)
BIT_DEPTH = 32767           # 2 to the power (16 - 1 for sign) -1 for zero
load_file = True
# standard_parameters = 1, 2, 44100, 132300, 'NONE', 'not compressed'

volume = 0.5

values = []
new_file_frames = 132300


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
tense_list = ['G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',
                 'G', 'F#', 'F', 'E',]
walking_list = ['F', 'E',
                'F', 'E',
                'F', 'E',
                'F', 'E']
gunshot_list = ['G#']
growl_list = ['A', 'A', 'Bb', 'Bb',
              'B', 'B', 'C', 'C',
              'C', 'C', 'Bb', 'Bb',
              'B', 'B', 'A', 'A', ]
equip_list = ['B', 'E']


# Attack, sustain, release values
quickest = (0.02, 0.0, 0.02)
quick = (0.02, 0.03, 0.08)
medium = (0.05, 0.1, 0.2)
slow = (0.1, 0.2, 0.3)
gunshot_speed = (0.02, 0.02, 0.2)
equip_speed = (0.0, 0.1, 0.0)


def custom_note(n):
    return 440 * math.pow(2, n/12.0)


def clamp(value_list):
    biggest_value = 0
    lowest_value = 0
    clamped_list = []
    for i in value_list:
        if i > biggest_value:
            biggest_value = i
        if i < lowest_value:
            lowest_value = i
    if biggest_value > -lowest_value:
        multiplier = BIT_DEPTH/biggest_value
    if -lowest_value > biggest_value:
        multiplier = BIT_DEPTH/-lowest_value
    for i in value_list:
        clamped_list.append(i*multiplier)
    return clamped_list

def clamp_1(list):
    clamped_list = []
    for value in list:
        if value > BIT_DEPTH:
            clamped_list.append(BIT_DEPTH)
        elif value < - BIT_DEPTH:
            clamped_list.append(-BIT_DEPTH)
        else:
            clamped_list.append(value)
        return clamped_list



class Sound:

    def write_file(self, values_list, file_name):
        self.file = wave.open(file_name, 'w')
        self.file.setparams((1, 2, 44100, 132300, 'NONE', 'not compressed'))

        for value in values_list:
            packed_value = (struct.pack("<h", value))
            self.file.writeframes(packed_value)
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
        self.file.setparams((1, 2, 44100, 132300, 'NONE', 'not compressed'))

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
        current_volume = 1

        for frame in xrange(int(total_frames)):
            if frame < attack_frames:
                current_volume += BIT_DEPTH / attack_frames   # BIT_DEPTH is max volume
            elif frame > attack_frames + sustain_frames:
                current_volume -= BIT_DEPTH / release_frames
            else:
                current_volume = BIT_DEPTH

            pure_tone_frame = math.sin(frame * frequency / SAMPLE_RATE) * current_volume * 2.0 * math.pi * volume
            self.new_values_list.append(pure_tone_frame)
        return clamp_1(self.new_values_list)


    def play_song(self, notes_list, attack_sustain_release):
        for note in notes_list:
            final_list = self.sound_envelope(notes[note], attack_sustain_release)
        return final_list



def Teleport():
    """doc string"""
    value_list = []
    for i in xrange(0,SAMPLE_LENGTH):
        value_1 = math.sin(math.pi * FREQUENCY*0.75 * (i / float(44100))) + math.sin(
            math.pi / float(1.01) * FREQUENCY*0.75 * (i / float(44100)))
        value = (value_1 * (volume * BIT_DEPTH))
        value_list.append(value)
    return value_list

def echo(list):
    counter = 0
    new_list = []
    for i in list:
        if counter < 6000:
            new_list.append(i)

        else:
            new_list.append(((list[counter-1000])+ i))
        counter += 1
    return new_list

Make_Sound = Sound()

new_gun = CreateSound('newgun.wav')
new_gun.sound_envelope(custom_note(-9), gunshot_speed)
#winsound.PlaySound(new_gun.name, winsound.SND_FILENAME)

new_song = CreateSound('newsong.wav')
#new_song.play_song(tense_list, quick)
#new_song.play_song(tense_list, medium)

gunshot_instance = CreateSound('gunsh.wav')
#gunshot_instance.play_song(gunshot_list, gunshot_speed)

walking_instance = CreateSound('walking.wav')
#walking_instance.play_song(walking_list, medium)

raptor_growl = CreateSound('rapgrowl.wav')
raptor_growl.play_song(growl_list, quickest)

equip = CreateSound('equip.wav')
#equip.play_song(equip_list, equip_speed)

headphone_killer = CreateSound('fubar.wav')

#winsound.PlaySound(headphone_killer.name, winsound.SND_FILENAME)

Make_Sound.write_file((new_gun.sound_envelope(custom_note(-9), gunshot_speed)),"testme.wav" )
Make_Sound.write_file(Teleport(),"teleport.wav")
Make_Sound.write_file(echo(Teleport()),"echo.wav")
Make_Sound.write_file(raptor_growl.play_song(growl_list, quickest), "testmetoo.wav")


