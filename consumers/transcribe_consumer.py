import json
import threading
import time

import pika

from config_constants import RabbitMQConfig
from utils.transcibe_utils import transcribe_gcs

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

# DMS_URL = 'http://localhost:8089'
DMS_URL = 'https://dms.timewise.space'


def register_transcribe_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(RabbitMQConfig.HOST, RabbitMQConfig.PORT, '/',
                                          pika.PlainCredentials(RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD)))
            channel = connection.channel()
            channel.queue_declare(queue='transcribe_queue')
            channel.basic_consume(queue='transcribe_queue', on_message_callback=process_message, auto_ack=False)
            print('[transcribe_queue] Waiting for messages')
            channel.start_consuming()
        except pika.exceptions.StreamLostError as e:
            print(f"[error] Stream connection lost: {e}")
        except Exception as e:
            print(f"[error] Unexpected error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)


def process_message(ch, method, properties, body):
    try:
        threading.Thread(target=threaded_process_message, args=(ch, method, properties, body)).start()
    except pika.exceptions.StreamLostError as e:
        print(f"[info] Message processed with StreamLostError")
        ch.basic_ack(delivery_tag=method.delivery_tag)


def threaded_process_message(ch, method, properties, body):
    for attempt in range(MAX_RETRIES):
        try:
            handle_transcribe_queue(ch, method, properties, body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"[info] Message processed successfully: {body}")
            return
        except Exception as e:
            print(f"[error] Error processing message: {e}. Attempt {attempt + 1} of {MAX_RETRIES}")
            time.sleep(RETRY_DELAY)
    print(f" [x] Failed to process message after {MAX_RETRIES} attempts: {body}")
    if ch.is_open:
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    else:
        print("[error] Channel is closed, cannot nack the message")


import requests


def update_transcript_to_db(schedule_id, generated_transcript):
    url = f'{DMS_URL}/dbms/v1/schedule/{schedule_id}/transcript'
    headers = {
        'accept': 'application/json',
        'x_api_key': '667qwsrUlyVa',
        'Content-Type': 'application/json'
    }
    data = {
        'video_transcript': {
            'raw_transcript': generated_transcript
        }
    }

    # print curl
    print(
        f"[info] curl -X PUT '{url}' -H 'accept: application/json' -H 'x_api_key: 667qwsrUlyVa' -H 'Content-Type: application/json' -d '{json.dumps(data)}'")
    response = requests.put(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"[info] Transcript updated successfully for schedule_id: {schedule_id}")
    else:
        print(
            f"[error] Failed to update transcript for schedule_id: {schedule_id}. Status code: {response.status_code}, Response: {response.text}")


def send_to_summarize_queue(schedule_id):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(RabbitMQConfig.HOST, RabbitMQConfig.PORT, '/',
                                  pika.PlainCredentials(RabbitMQConfig.USERNAME, RabbitMQConfig.PASSWORD)))
    channel = connection.channel()
    channel.queue_declare(queue='summarize_queue')
    message = {
        'schedule_id': schedule_id
    }
    channel.basic_publish(exchange='', routing_key='summarize_queue', body=json.dumps(message))
    print(f"[info] Sent to summarize queue: {message}")
    connection.close()


def handle_transcribe_queue(ch, method, properties, body):
    print(f"[info] Transcribe payload: {body}")

    message = json.loads(body)
    if 'filename' not in message or 'schedule_id' not in message:
        raise ValueError('filename or schedule_id are required')

    file_name = f"gs://tw-transcripts/{message['filename']}"

    generated_transcript = transcribe_gcs(file_name)
    if not generated_transcript:
        raise ValueError('Failed to generate transcript from GCS')

    # call dms to save in DB
    update_transcript_to_db(message['schedule_id'], generated_transcript)

    print(f"[info] Transcribe completed for schedule_id: {message['schedule_id']}")
    # send to summarize queue
    send_to_summarize_queue(message['schedule_id'])
