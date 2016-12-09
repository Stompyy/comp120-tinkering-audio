import random, wave, struct, math, winsound

# Initialises sound variables
LENGTH_OF_TRACK = 1
SAMPLE_LENGTH = 44100 * LENGTH_OF_TRACK
FREQUENCY = float(1000)
SAMPLE_RATE = float(44100)
BIT_DEPTH = 32767  # 2 to the power (16 - 1 for sign) -1 for zero
volume = 0.5

notes = {'A': 440 * math.pow(2, 20 / 12.0),
         'Bb': 440 * math.pow(2, 21 / 12.0),
         'B': 440 * math.pow(2, 22.0 / 12.0),
         'C': 440 * math.pow(2, 23.0 / 12.0),
         'C#': 440 * math.pow(2, 24.0 / 12.0),
         'D': 440 * math.pow(2, 25.0 / 12.0),
         'D#': 440 * math.pow(2, 26.0 / 12.0),
         'E': 440 * math.pow(2, 27.0 / 12.0),
         'F': 440 * math.pow(2, 28.0 / 12.0),
         'F#': 440 * math.pow(2, 29.0 / 12.0),
         'G': 440 * math.pow(2, 30.0 / 12.0),
         'G#': 440 * math.pow(2, 11.0 / 12.0),

         'gunshot': 440 * math.pow(2, 5),
         'growl_1': 440 * math.pow(2, 3),
         'growl_2': 440 * math.pow(2, 1.5),
         'growl_3': 440 * math.pow(2, 0.5),
         'roar_1': 440 * math.pow(2, 11.0 / 12.0),
         'roar_2': 440 * math.pow(2, 10.0 / 12.0),
         'roar_3': 440 * math.pow(2, 19.0 / 20.0)}

# notes lists
custom = ['gunshot']
scale = ['A', 'Bb', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']

tense_list = ['G', 'F#', 'F', 'E',
              'G', 'F#', 'F', 'E',
              'G', 'F#', 'F', 'E',
              'G', 'F#', 'F', 'E', ]
walking_list = ['F', 'E',
                'F', 'E',
                'F', 'E',
                'F', 'E']
gunshot_list = ['G#']
growl_dead = ['growl_1', 'growl_1', 'growl_2', 'growl_2',
              'growl_2', 'growl_2', 'growl_3', 'growl_3', ]
growl_alive = ['growl_3', 'growl_3', 'growl_2', 'growl_2',
               'growl_2', 'growl_2', 'growl_1', 'growl_1', ]
roar = ['roar_1', 'roar_1', 'roar_2', 'roar_2',
        'roar_2', 'roar_2', 'growl_3', 'roar_3', ]
equip_list = ['B', 'E']

# attack, sustain, and release values
quickest = (0.02, 0.0, 0.02)
quick = (0.01, 0.3, 0.01)
medium = (0.05, 0.1, 0.2)
slow = (0.1, 0.2, 0.3)
gunshot_speed = (0.0, 0.01, 0.01)
equip_speed = (0.0, 0.1, 0.0)
growl = (0.01, 0.0, 0.01)
new_test = (0.0, 0.0, 0.01)


def custom_note(n):
    """to create a custom frequency key outside of the dictionary of standard notes"""
    return 440 * math.pow(2, n / 12.0)


def normalise(value_list):
    """normalises an entire list proportionately so that all values are within the correct parameters """
    multiplier = 0
    biggest_value = 0
    lowest_value = 0
    clamped_list = []
    for i in value_list:
        if i > biggest_value:
            biggest_value = i
        if i < lowest_value:
            lowest_value = i
    if biggest_value > -lowest_value:
        multiplier = BIT_DEPTH / biggest_value
    if -lowest_value > biggest_value:
        multiplier = BIT_DEPTH / -lowest_value
    for i in value_list:
        clamped_list.append(i * multiplier)
    return clamped_list


class LoadSound():
    """Loads a sound file of name 'name.wav' to add effects to with functions"""

    def __init__(self, name):
        """loads the file"""
        self.file = wave.open(name, "r")

    def read_file(self):
        """returns an unpacked list of values of the sound wave"""
        unpacked_list = []
        step = BIT_DEPTH / 200  # auto tune step

        for i in xrange(self.file.getnframes()):
            current_frame = self.file.readframes(1)
            unpacked_frame = struct.unpack("i", current_frame)
            unpacked_list.append(unpacked_frame[0])
        return unpacked_list


class CreateSound():
    """Creates a file with name 'name' """

    def __init__(self, name):
        """creates a new empty writable file"""
        self.file = wave.open(name, 'w')
        self.new_values_list = []
        self.name = name
        self.file.setparams((1, 2, 44100, 132300, 'NONE', 'not compressed'))
        self.temp_values_list = []

    def write_file(self, values_list):
        """writes a list of unpacked values packed into .file"""
        for value in values_list:
            packed_value = struct.pack("<h", value)
            self.file.writeframes(packed_value)
        self.file.close()

    def sound_envelope(self, frequency, attack_sustain_release):
        """crreates a basic sound envelope passing in a tuple for attack, sustain, and release"""
        self.new_values_list = []
        attack_frames = attack_sustain_release[0] * SAMPLE_RATE
        sustain_frames = attack_sustain_release[1] * SAMPLE_RATE
        release_frames = attack_sustain_release[2] * SAMPLE_RATE
        total_frames = attack_frames + sustain_frames + release_frames
        current_volume = 1

        for frame in xrange(int(total_frames)):
            if frame < attack_frames:
                current_volume += BIT_DEPTH / attack_frames  # BIT_DEPTH is max volume
            elif frame > attack_frames + sustain_frames:
                current_volume -= BIT_DEPTH / release_frames
            else:
                current_volume = BIT_DEPTH

            # written below, 2.0 * math.pi is to convert radians
            pure_tone_frame = math.sin(frame * frequency / SAMPLE_RATE) * current_volume * 2.0 * math.pi * volume
            self.temp_values_list.append(pure_tone_frame)

        self.temp_values_list = normalise(self.temp_values_list)
        for i in self.temp_values_list:
            packed_value = (struct.pack("<h", i))
            self.new_values_list.append(packed_value)

        self.file.writeframes(''.join(self.new_values_list))

    def play_song(self, notes_list, attack_sustain_release):
        """plays a list of notes using the dictionary above"""
        for note in notes_list:
            self.sound_envelope(notes[note], attack_sustain_release)
        winsound.PlaySound(self.name, winsound.SND_FILENAME)

    def teleport(self):
        """futuristic teleport sound effect for game contract"""
        value_list = []
        for i in xrange(SAMPLE_LENGTH):
            value_1 = math.sin(math.pi * FREQUENCY * 0.75 * (i / float(SAMPLE_RATE))) + math.sin(
                math.pi / float(1.01) * FREQUENCY * 0.75 * (i / float(SAMPLE_RATE)))
            value = (value_1 * (volume * BIT_DEPTH))
            value_list.append(value)
        return value_list

    def white_noise(self):
        """gratuitous white noise effect"""
        value_list = []
        for i in xrange(SAMPLE_LENGTH):
            value_1 = random.randrange(-BIT_DEPTH, BIT_DEPTH)
            value_list.append(value_1)
        return value_list

    def double(self, list):
        """skips every other value"""
        double_list = []
        for i in xrange(0, len(list), 2):
            double_list.append(list[i])
        return double_list

    def half(self, list):
        """duplicates every successive value"""
        half_list = []
        for i in xrange(len(list)):
            half_list.append(list[i - 1])
            half_list.append(list[i])
        return half_list

    def reverse(self, list):
        """reverses the sound wave, as an unpacked list argument"""
        reversed_list = []
        for i in xrange(len(list), 0, -1):
            reversed_list.append(list[i])
        return reversed_list

    def combine(self, list_one, list_two):
        """adds one wave onto the end of another"""
        for i in xrange(len(list_two)):
            list_one.append(list_two[i])
        return list_one

    def additive(self, list_one, list_two):
        """adds two waves together"""
        overlapped_list = []

        # gets the shortest list length so doesn't go list out of bounds error
        if len(list_one) < len(list_two):
            overlapped_list_length = len(list_one)
        else:
            overlapped_list_length = len(list_two)

        # adds them before normalising result
        for i in xrange(overlapped_list_length):
            overlapped_list.append(list_one[i] + list_two[i])
        return normalise(overlapped_list)

    def echo(self, list):
        """adds a reduced amplitude copy of the wave at a later point"""
        counter = 0
        new_list = []
        for i in list:
            counter += 1
            if counter < 10000:
                value = i
            else:
                value = i + (list[counter - 10000] * 0.4)
            new_list.append(value)
        return normalise(new_list)


def pre_made_sound_effects():
    """creates sound effects used in game"""
    gunshot = CreateSound('gunshot.wav')
    gunshot.play_song(custom, gunshot_speed)

    walking_instance = CreateSound('walking.wav')
    walking_instance.play_song(walking_list, medium)

    raptor_dead = CreateSound('rapgrowldead.wav')
    raptor_dead.play_song(growl_dead, growl)

    raptor_alive = CreateSound('rapalive.wav')
    raptor_alive.play_song(growl_alive, growl)

    equip = CreateSound('equip.wav')
    equip.play_song(equip_list, equip_speed)

    overloard_roar = CreateSound('overlordroar.wav')
    overloard_roar.play_song(roar, growl)

    # creates teleport noise and a 'double' version then adds the waves together for a new teleport noise
    teleport = CreateSound('teleport.wav')
    teleport.write_file(teleport.teleport())

    additive_teleport = CreateSound('additive_teleport.wav')
    additive_teleport.write_file(additive_teleport.additive(additive_teleport.teleport(),
                                                            additive_teleport.double(additive_teleport.teleport())))

# pre_made_sound_effects()