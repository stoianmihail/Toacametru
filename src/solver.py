import numpy as np
import librosa

class Solver:
  def __init__(self):
    pass

  def compute_statistics(self, dist, onset_frames):
    statistics = {
      'max_beats' : 0,
      'avg_beats' : 0,
      'total' : 0
    }

    def time_dist(i, j):
      return (onset_frames[j] - onset_frames[i]) * dist
    
    def report(i, j):
      num_beats = j - i + 1
      if num_beats > statistics['max_beats']:
        statistics['max_beats'] = num_beats

    # Average number of beats.
    if len(onset_frames) > 1:
      statistics['avg_beats'] = len(onset_frames) / time_dist(0, len(onset_frames) - 1)

    # Total number of beats.
    statistics['total'] = len(onset_frames)

    # Fix the first window.
    l, r = 0, 0
    while r != len(onset_frames) and time_dist(l, r) <= 1.0:
      r += 1

    # Report the first window.
    if r:
      report(l, r - 1)

    # Get the next ones.
    while r != len(onset_frames):
      # Get rid of previous frames.
      while l != r and time_dist(l, r) > 1.0:
        l += 1

      # Report statistics in this window.
      report(l, r)
      
      # Increase the right pointer.
      r += 1
    return statistics

  def analyze(self, sample_file):
    x, sr = librosa.load(sample_file)
    o_env = librosa.onset.onset_strength(x, sr=sr)
    times = librosa.frames_to_time(np.arange(len(o_env)), sr=sr)
    onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)
    return self.compute_statistics(times[1], onset_frames)
