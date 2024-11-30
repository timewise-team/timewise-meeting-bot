import os
import tempfile
from abc import ABC, abstractmethod

from utils.audio_utils import generate_audio_path


class MeetBot(ABC):
    @abstractmethod
    def go_to_meeting(self, meet_link):
        pass

    @abstractmethod
    def turn_off_mic_cam(self):
        pass

    @abstractmethod
    def join_meeting(self, audio_path, max_duration):
        pass


class MeetBotFactory:
    @staticmethod
    def create_meet_bot(meet_link):
        if 'google' in meet_link:
            from bots.google_meeting_bot import GoogleMeetBot
            return GoogleMeetBot()
        # elif bot_type == 'zoom':
        #     return ZoomMeetBot()
        else:
            raise ValueError(f"Unknown bot type for meeting link: {meet_link}")


def start_meeting_bot(msg):
    audio_path = generate_audio_path()

    # Duration for bot to record audio
    meeting_bot = MeetBotFactory.create_meet_bot(msg['meet_link'])
    meeting_bot.go_to_meeting(msg['meet_link'])
    # meeting_bot.turn_off_mic_cam()
    meeting_bot.join_meeting(audio_path, msg['schedule_id'])

    # SpeechToText().transcribe(audio_path)
