import json
import threading
import time

import pika

from utils.transcibe_utils import transcribe_gcs

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

DMS_URL = 'http://localhost:8089'
# DMS_URL = 'https://dms.timewise.space'


def register_transcribe_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('localhost', 5672, '/', pika.PlainCredentials('admin', 'admin')))
            channel = connection.channel()
            channel.queue_declare(queue='transcribe_queue')
            channel.basic_consume(queue='transcribe_queue', on_message_callback=process_message, auto_ack=False)
            print(' [*] Waiting for messages. To exit press CTRL+C')
            channel.start_consuming()
        except pika.exceptions.StreamLostError as e:
            print(f" [error] Stream connection lost: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        except Exception as e:
            print(f" [error] Unexpected error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)


def process_message(ch, method, properties, body):
    threading.Thread(target=threaded_process_message, args=(ch, method, properties, body)).start()


def threaded_process_message(ch, method, properties, body):
    for attempt in range(MAX_RETRIES):
        try:
            handle_transcribe_queue(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f" [info] Message processed successfully: {body}")
            return
        except Exception as e:
            print(f" [error] Error processing message: {e}. Attempt {attempt + 1} of {MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    print(f" [x] Failed to process message after {MAX_RETRIES} attempts: {body}")
    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


import requests


def update_transcript_to_db(schedule_id, generated_transcript):
    url = f'{DMS_URL}/dbms/v1/schedule/{schedule_id}'
    headers = {
        'accept': 'application/json',
        'x_api_key': '667qwsrUlyVa',
        'Content-Type': 'application/json'
    }
    data = {
        'video_transcript': generated_transcript
    }

    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f" [info] Transcript updated successfully for schedule_id: {schedule_id}")
    else:
        print(
            f" [error] Failed to update transcript for schedule_id: {schedule_id}. Status code: {response.status_code}, Response: {response.text}")


def handle_transcribe_queue(ch, method, properties, body):
    print(f" [info] Transcribe payload: {body}")

    message = json.loads(body)
    if 'filename' not in message or 'schedule_id' not in message:
        raise ValueError('filename or schedule_id are required')

    file_name = f"gs://tw-transcripts/{message['filename']}"

    generated_transcript = transcribe_gcs(file_name)

    # call dms to save in DB
    update_transcript_to_db(message['schedule_id'], generated_transcript)
