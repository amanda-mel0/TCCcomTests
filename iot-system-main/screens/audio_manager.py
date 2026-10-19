import math
from array import array

import pygame


_SOUNDS = {}


def _ensure_mixer():
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        return True
    except pygame.error:
        return False


def _make_tone(freq, duration_ms, volume=0.45, sample_rate=44100, channels=2):
    sample_count = int(sample_rate * duration_ms / 1000)
    samples = array("h")
    fade_count = max(1, int(sample_rate * 0.015))

    for i in range(sample_count):
        t = i / sample_rate
        fade_in = min(1.0, i / fade_count)
        fade_out = min(1.0, (sample_count - i) / fade_count)
        envelope = min(fade_in, fade_out)
        value = int(32767 * volume * envelope * math.sin(2 * math.pi * freq * t))
        for _ in range(channels):
            samples.append(value)

    return samples


def _make_sequence(notes, volume=0.45):
    if not _ensure_mixer():
        return None

    init = pygame.mixer.get_init()
    sample_rate = init[0] if init else 44100
    channels = init[2] if init else 2
    samples = array("h")

    for freq, duration_ms in notes:
        if freq <= 0:
            silence_count = int(sample_rate * duration_ms / 1000)
            for _ in range(silence_count * channels):
                samples.append(0)
        else:
            samples.extend(_make_tone(freq, duration_ms, volume, sample_rate, channels))

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except pygame.error:
        return None


def _play(name, notes, volume=0.45):
    sound = _SOUNDS.get(name)
    if sound is None:
        sound = _make_sequence(notes, volume)
        _SOUNDS[name] = sound

    if sound:
        try:
            sound.play()
        except pygame.error:
            pass


def play_success():
    _play("success", [(660, 90), (0, 25), (880, 130)], volume=0.36)


def play_error():
    _play("error", [(260, 140), (0, 30), (180, 170)], volume=0.34)


def play_phase_complete():
    _play("phase_complete", [(0, 260), (523, 110), (659, 110), (784, 130), (1046, 220)], volume=0.38)


def play_game_complete():
    _play("game_complete", [(523, 120), (659, 120), (784, 120), (1046, 180), (0, 40), (988, 280)], volume=0.4)
