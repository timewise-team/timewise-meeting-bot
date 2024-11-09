import json
import threading
import time

import pika

from bots.meeting_bot_factory import start_meeting_bot

MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds


def register_meeting_bot_consumer():
    while True:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters('34.87.175.71', 5672, '/', pika.PlainCredentials('admin', 'admin')))
            channel = connection.channel()
            channel.queue_declare(queue='start_meeting_queue')
            channel.basic_consume(queue='start_meeting_queue', on_message_callback=process_message, auto_ack=False)
            print('[start_meeting_queue] Waiting for messages')
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
            handle_start_meeting_queue(ch, method, properties, body)
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


def handle_start_meeting_queue(ch, method, properties, body):
    print(f"[info] Start meeting: {body}")
    message = json.loads(body)
    if 'meet_link' not in message or 'schedule_id' not in message:
        raise ValueError('meet_link or schedule_id are required')
    start_meeting_bot(message)
