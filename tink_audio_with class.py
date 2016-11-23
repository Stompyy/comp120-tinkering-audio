import wave, struct, sys, math, winsound, pygame
from pygame.locals import *

pygame.init()
pygame.mixer.init()

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600

LENGTH_OF_TRACK = 1
SAMPLE_LENGTH = 44100 * LENGTH_OF_TRACK
FREQUENCY = float(1000)
SAMPLE_RATE = float(44100)
BIT_DEPTH = 32767           # 2 to the power (16 - 1 for sign) -1 for zero

volume = 0.5

values = []

window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
window.fill((255, 255, 255))
font = pygame.font.SysFont(None, 48)
levelText = font.render('m = mmmMMM', True, (0, 0, 0))
window.blit(levelText, (0, 0))
pygame.display.update()


class Sound:
    def __init__(self):
        """creates the file"""
        self.file = wave.open('noise_with_class2.wav', 'w')

    def set_parameters(self, nchannels, sampwidth, framerate, nframes, comptype, compname):
        """sets the parameters of the .wav file"""

        # probably unnecessary to have in a function. Just do after creating an instance
        self.file.setparams((nchannels, sampwidth, framerate, nframes, comptype, compname))

    def write_file(self, values_list):
        """takes the list of newly created values, joins, writes to the file, then closes the wave stream"""
        self.file.writeframes(''.join(values_list))
        self.file.close()


def mmmMMM():
    """doc string"""
    for i in xrange(0, SAMPLE_LENGTH):
        base_sound_wave_value = math.sin(2.0 * math.pi * FREQUENCY * (i / SAMPLE_RATE))

        # takes base value and brings up to correct BIT_DEPTH * volume
        # volume = i / SAMPLE_LENGTH increases volume over time. #leetfx
        value = base_sound_wave_value * BIT_DEPTH * i / SAMPLE_LENGTH

        packed_value = struct.pack('<h', value)
        values.append(packed_value)
        print packed_value


def noise():
    """doc string"""
    for i in xrange(0,SAMPLE_LENGTH):
        value_1 = math.sin(math.pi * FREQUENCY * (i / float(44100))) + math.sin(
            math.pi / float(1.01) * FREQUENCY * (i / float(44100)))
        value = (value_1 * (volume * BIT_DEPTH))
        packed_value = struct.pack('<h', value)
        values.append(packed_value)
        print packed_value


# create instance of Sound class

controls = {'m': (mmmMMM, "mmmMMM"),
            'n': (noise, "noise")}
for letters in controls:
    print letters + " makes a sound like " + controls[letters][1]

noise_out = Sound()


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

    pygame.display.update()








"""
def change_volume(current_amplitude, volume_level):
    new_amplitude = current_amplitude * volume_level
    return new_amplitude


for i in range(audio.getnframes()-1):
    frame = audio.readframes(1)
    #print 'hello'
    answer = struct.unpack("<h", frame)
    list.append(answer)

    if answer > max_amplitude:
        max_amplitude = answer
        peak_one = i

    if answer < min_amplitude:
        min_amplitude = answer
        trough_one = i
        #if peak_one != 10:
         #   wavelength = (peak_one - trough_one) * 2
          #  print wavelength

    #print answer

    #change_volume(answer, volume)

    #print max_amplitude, min_amplitude

while True:

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

#    for i in xrange(list.__len__()):
 #       print 'yo'
  #      window.fill((255, 255, 255))
   #    pygame.draw.rect(window, (100, 100, 100), (50, 50, int(list[i][0]), list[i][0]), 0)
    #   pygame.display.update()

"""
