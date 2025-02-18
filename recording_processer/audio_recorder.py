import json
import threading
import time

import pika
import sounddevice as sd

from config_constants import RabbitMQConfig
from utils.audio_utils import save_audio_to_wav
from utils.storage_utils import upload_blob


def publish_msg_to_transcribe(filename, schedule_id):
    # Establish connection to RabbitMQ
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RabbitMQConfig.HOST, RabbitMQConfig.PORT, '/',
                                  pika.PlainCredentials(RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD)))
    channel = connection.channel()

    # Declare the queue
    channel.queue_declare(queue='transcribe_queue')

    # Publish the message
    message = {'filename': filename, 'schedule_id': schedule_id}
    channel.basic_publish(exchange='', routing_key='transcribe_queue', body=json.dumps(message))

    # Close the connection
    connection.close()
    print(f"[info] Sent to transcribe queue: {message}")


class AudioRecorder:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate

    @staticmethod
    def start_audio_recording(meeting_bot, filename, schedule_id):
        def callback(indata, frames, time, status):
            if status:
                print(status)
            audio_frames.append(indata.copy())

        def stop_recording_when_meeting_ends():
            while not meeting_bot.check_if_meeting_ended():
                time.sleep(2)
            print("Stopping recording...")
            return True
            # stop_event.set()

        # # Create a threading event to signal stopping the recording
        # stop_event = threading.Event()
        # monitoring_thread = threading.Thread(target=stop_recording_when_meeting_ends)
        # monitoring_thread.start()

        audio_frames = []
        samplerate = 44100
        channels = 1

        # Open audio stream
        with sd.InputStream(samplerate=samplerate, channels=channels, callback=callback, device=0):
            print("Recording started...")
            while not stop_recording_when_meeting_ends():
                time.sleep(1)

        save_audio_to_wav(filename, audio_frames, samplerate)
        upload_blob('tw_transcripts', filename, filename)
        # delete_local_file(filename)

        publish_msg_to_transcribe(filename, schedule_id)
