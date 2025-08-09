#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
import os

import numpy as np
import shlex
import subprocess
import wave
import json

from deepspeech import Model

from pipes import quote


def convert_samplerate(audio_path, desired_sample_rate):
    sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate {} --encoding signed-integer --endian little --compression 0.0 --no-dither - '.format(quote(audio_path), desired_sample_rate)
    try:
        output = subprocess.check_output(shlex.split(sox_cmd), stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        raise RuntimeError('SoX returned non-zero status: {}'.format(e.stderr))
    except OSError as e:
        raise OSError(e.errno, 'SoX not found, use {}hz files or install it: {}'.format(desired_sample_rate, e.strerror))

    return desired_sample_rate, np.frombuffer(output, np.int16)


def words_from_candidate_transcript(metadata):
    word = ""
    word_list = []
    word_start_time = 0
    # Loop through each character
    for i, token in enumerate(metadata.tokens):
        # Append character to word if it's not a space
        if token.text != " ":
            if len(word) == 0:
                # Log the start time of the new word
                word_start_time = token.start_time

            word = word + token.text
        # Word boundary is either a space or the last character in the array
        if token.text == " " or i == len(metadata.tokens) - 1:
            word_duration = token.start_time - word_start_time

            if word_duration < 0:
                word_duration = 0

            each_word = dict()
            each_word["word"] = word
            each_word["start_time"] = round(word_start_time, 4)
            each_word["duration"] = round(word_duration, 4)

            word_list.append(each_word)
            # Reset
            word = ""
            word_start_time = 0

    return word_list

class Transcripter:
    def __init__(self, model = None):
        if not model:
            model = os.path.join(
                os.path.dirname(__file__),
                "deepspeech-0.9.3-models.pbmm"
            )

        self.ds = Model(model)
        self.desired_sample_rate =self.ds.sampleRate()

    def get_transcript(self, audio_path):
        with wave.open(audio_path, 'rb') as fin:
            fs_orig = fin.getframerate()
            if fs_orig != self.desired_sample_rate:
                _, audio = convert_samplerate(audio_path, self.desired_sample_rate)
            else:
                audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)


        transcript = self.ds.sttWithMetadata(audio, 1).transcripts[0]
        return words_from_candidate_transcript(transcript)



def main():
    audio = r"generated.wav"

    t = Transcripter()
    transcript = t.get_transcript(audio)
    with open('out.json', 'w') as f:
        json.dump(transcript, f, indent=2)

if __name__ == '__main__':
    main()
