import os
import sys
import threading

from consumers.meeting_bot_consumer import register_meeting_bot_consumer
from consumers.summarize_consumer import register_summarize_consumer
from consumers.transcribe_consumer import register_transcribe_consumer


def main():
    try:
        # Create threads for each consumer
        meeting_bot_thread = threading.Thread(target=register_meeting_bot_consumer)
        transcribe_thread = threading.Thread(target=register_transcribe_consumer)
        summarize_thread = threading.Thread(target=register_summarize_consumer)

        # Start the threads
        meeting_bot_thread.start()
        transcribe_thread.start()
        summarize_thread.start()

        # Wait for both threads to complete
        meeting_bot_thread.join()
        transcribe_thread.join()
        summarize_thread.join()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    main()
