from google.cloud import speech
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    './timewise-6969-372d2275d0bd.json')


def transcribe_gcs(gcs_uri: str) -> str:
    client = speech.SpeechClient(credentials=credentials)

    audio = speech.RecognitionAudio(uri=gcs_uri)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=44100,
        language_code="vi-VN",
    )

    operation = client.long_running_recognize(config=config, audio=audio)

    print("[info] Waiting for operation to complete...")
    response = operation.result(timeout=90)
    print(f'[info] Speech2Text Response: {response}')

    raw_transcript = ""
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        raw_transcript = result.alternatives[0].transcript


    print(f"[info] Raw Transcript: {raw_transcript}")
    return raw_transcript
