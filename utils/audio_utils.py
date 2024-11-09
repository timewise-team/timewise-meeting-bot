import datetime
import os
import random
import string
import wave

import numpy as np

def generate_audio_path():
    current_date = datetime.datetime.now().strftime("%Y%m%d")
    random_string = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    audio_path = f"record_{current_date}_{random_string}.wav"
    return audio_path


def save_audio_to_wav(filename, audio_frames, samplerate):
    audio_data = np.concatenate(audio_frames, axis=0)
    audio_data = np.int16(audio_data * 32767)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)  # Mono
        wf.setsampwidth(2)  # 2 bytes per sample
        wf.setframerate(samplerate)
        wf.writeframes(audio_data.tobytes())
    print(f"Audio saved to {filename}")

def delete_local_file(filename):
    os.remove(filename)
    print(f"Deleted local file: {filename}")
