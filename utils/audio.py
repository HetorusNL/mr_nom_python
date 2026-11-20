from pygame import mixer


class Audio(object):
    def __init__(self, has_audio):
        self.has_audio = has_audio
        self.music_on = False
        self.sound_on = False

        if self.has_audio:
            self._load_assets()

    def set_music(self, on):
        if not self.has_audio:
            return

        if on and not self.music_on:
            mixer.music.play(-1)
            self.music_on = True
        elif not on and self.music_on:
            mixer.music.stop()
            self.music_on = False

    def set_sound(self, on):
        if not self.has_audio:
            return

        self.sound_on = on

    def play_sound(self, sound):
        if not self.has_audio:
            return

        if not self.sound_on:
            return

        if self.sounds.get(sound):
            self.sounds[sound].play()
        else:
            print(sound, "not found!")

    def _load_assets(self):
        mixer.music.load("assets/music.ogg")
        self.sounds = {
            "bitten": mixer.Sound("assets/bitten.ogg"),
            "click": mixer.Sound("assets/click.ogg"),
            "eat": mixer.Sound("assets/eat.ogg"),
        }
