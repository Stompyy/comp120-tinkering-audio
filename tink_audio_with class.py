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
        print self.file.getnchannels()

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

    def set_parameters(self, nchannels, sampwidth, framerate, nframes, comptype, compname):
        """sets the parameters of the .wav file"""

        # probably unnecessary to have in a function. Just do after creating an instance
        self.file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    def sound_envelope(self, max_volume, frequency):
        new_values_list = []
        attack_time = 0.05 * SAMPLE_RATE
        sustain_time = 0.1 * SAMPLE_RATE
        release_time = 0.2 * SAMPLE_RATE
        total_time = attack_time + sustain_time + release_time
        current_volume = 0.0

        for frame in xrange(int(total_time)):
            if frame < attack_time:
                current_volume += max_volume / attack_time
            elif frame > attack_time + sustain_time:
                current_volume -= max_volume / release_time
            else:
                current_volume = max_volume

            pure_tone_frame = math.sin(frame * frequency / SAMPLE_RATE) * current_volume * 2.0 * math.pi
            new_values_list.append(struct.pack("<h", clamp(pure_tone_frame)))

        self.file.writeframes(''.join(new_values_list))

    def play_scale(self):
        scale = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
        for note in scale:
            self.sound_envelope(BIT_DEPTH, notes[note])

    def wonderwall(self):
        wonderwall = ['E', 'E', 'G', 'G', 'D', 'D', 'A', 'A']
        for note in wonderwall:
            self.sound_envelope(BIT_DEPTH, notes[note])

    def come_as_you_are(self):
        come_as_you_are = ['E', 'E', 'F', 'F#', 'F#', 'A', 'F#', 'A', 'F#', 'F#', 'F', 'E', 'E', 'B', 'E', 'B']
        for note in come_as_you_are:
            self.sound_envelope(BIT_DEPTH, notes[note])


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





scale = CreateSound('scale.wav')
scale.set_parameters(1, 2, 44100, 132300, 'NONE', 'not compressed')
scale.wonderwall()
# winsound.PlaySound('scale.wav', winsound.SND_FILENAME)

wonderwall_echo = LoadSound('scale.wav')
wonderwall_echo.write_file('wonderecho.wav', wonderwall_echo.echo(1000))
winsound.PlaySound('wonderecho.wav', winsound.SND_FILENAME)

nirvana = CreateSound('comeasyouare.wav')
nirvana.set_parameters(1, 2, 44100, 132300, 'NONE', 'not compressed')
nirvana.come_as_you_are()
winsound.PlaySound('comeasyouare.wav', winsound.SND_FILENAME)



#gun = LoadSound("gunshot2.wav")
#gun.write_file('gun3.wav', gun.echo(1000))

winsound.PlaySound('gun3.wav', winsound.SND_FILENAME)



"""
controls = {'m': (mmmMMM, "mmmMMM"),
            'n': (noise, "noise"),
            'p': (echo_two, "mmmMMM")}
for letters in controls:
    print letters + " makes a sound like " + controls[letters][1]


'create instance of sound'
# gun = LoadSound("gunshot2.wav")
# gun.write_file("gun3.wav", gun.read_file())

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        keys = pygame.key.get_pressed()

        if event.type == pygame.KEYDOWN:
            key_pressed = pygame.key.name(event.key)
            if key_pressed in controls:
                command = controls[key_pressed][0]
                command()

                # sets parameters and writes newly made value_string as sound wave
                noise_out.set_parameters(2, 2, 44100, 132300, 'NONE', 'not compressed')
                noise_out.write_file(values)

                print 'now play'
                del noise_out
                winsound.PlaySound('noise_with_class.wav', winsound.SND_FILENAME)
                # or with pygame
                # can't get this to work?
#                mmm_sound = pygame.mixer.Sound('noise_with_class.wav')
#                mmm_sound.play()
                noise_out = Sound()
                noise_out.set_parameters(2, 2, 44100, 132300, 'NONE', 'not compressed')
"""