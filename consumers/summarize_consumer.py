import json
import threading
import time

import pika
import requests

from consumers.transcribe_consumer import DMS_URL, update_transcript_to_db
from utils.summarize_utils import generate_summary

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def register_summarize_consumer():
    while True:
        try:
            # Establish connection to RabbitMQ
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('34.87.175.71', 5672, '/', pika.PlainCredentials('admin', 'admin')))
            channel = connection.channel()
            channel.queue_declare(queue='summarize_queue')  # Queue name
            channel.basic_consume(queue='summarize_queue', on_message_callback=process_message, auto_ack=False)
            print('[summarize_queue] Waiting for messages')
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
            handle_summarize_queue(ch, method, properties, body)
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


def handle_summarize_queue(ch, method, properties, body):
    print(f"[info] Start summarization: {body}")
    message = json.loads(body)
    if 'schedule_id' not in message:
        raise ValueError('schedule_id is required')

    # Query the database with schedule_id
    transcript = get_transcript_by_schedule_id(message['schedule_id'])
    if transcript is None:
        raise ValueError(f'No transcript found for schedule_id: {message["schedule_id"]}')

    print('[info] Retrieved transcript:', transcript)
    transcript = json.loads(transcript)
    raw_transcript = transcript.get('raw_transcript', None)
    if raw_transcript is None:
        raise ValueError(f'No raw_transcript found for schedule_id: {message["schedule_id"]}')

    # Run the summarization function on the retrieved transcript
    summarized_text = generate_summary(raw_transcript)
    if summarized_text is None:
        raise ValueError(f'Failed to generate summary for schedule_id: {message["schedule_id"]}')

    updated_transcript = {
        **transcript,
        'summary': summarized_text
    }

    # Optionally, store the summary in the database or process further
    update_transcript_to_db(message['schedule_id'], updated_transcript)


def get_transcript_by_schedule_id(schedule_id):
    url = f'{DMS_URL}/dbms/v1/schedule/{schedule_id}'
    headers = {
        'accept': 'application/json',
        'x_api_key': '667qwsrUlyVa',
    }

    # print curl
    print(f"curl -X GET \"{url}\" -H \"accept: application/json\" -H \"x_api_key: 667qwsrUlyVa\"")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        resp_data = response.json()
        return resp_data.get('video_transcript')
    else:
        print(
            f"[error] Failed to fetch transcript for schedule_id: {schedule_id}. Status code: {response.status_code}, Response: {response.text}")
        return None


# Start the consumer to listen for messages
if __name__ == "__main__":
    register_summarize_consumer()
