import sys
import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from src.audio_hack import Audio

def analyze(sample_file):
  x, sr = librosa.load(sample_file)
  o_env = librosa.onset.onset_strength(x, sr=sr)
  onset_frames = librosa.onset.onset_detect(onset_envelope=o_env, sr=sr)
  return len(onset_frames)

def main():
  if len(sys.argv) != 2:
    print(f'Usage: python3 {sys.argv[0]} <file>')
    sys.exit(-1)

  sample_file = sys.argv[1]
  count = analyze(sample_file)
  print(count)

if __name__ == '__main__':
  main()