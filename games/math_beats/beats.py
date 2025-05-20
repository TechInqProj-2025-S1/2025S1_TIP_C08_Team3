import aubio
import numpy as np
import os

class BeatDetector:
    def __init__(self, filepath):
        self.filepath = filepath
        self.samplerate = 44100
        self.hop_size = 512
        self.beats = []
        self.bpm = 0

    def analyze(self):
        if not os.path.exists(self.filepath):
            raise FileNotFoundError(f"File not found: {self.filepath}")
        s = aubio.source(self.filepath, self.samplerate, self.hop_size)
        o = aubio.tempo("default", 1024, self.hop_size, self.samplerate)
        beats = []
        total_frames = 0
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                timestamp = o.get_last_s()
                beats.append(timestamp)
            total_frames += read
            if read < self.hop_size:
                break
        self.beats = [int(b * 1000) for b in beats]  # ms
        self.bpm = o.get_bpm()
        return self.beats, self.bpm
