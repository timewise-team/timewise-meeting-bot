import google.generativeai as genai

GEMINI_API_KEY = 'AIzaSyDho0bRbLOqDEqkBHOliuGWKdfSHOaeTWc'

genai.configure(api_key=GEMINI_API_KEY)


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini.

    See https://ai.google.dev/gemini-api/docs/prompting_with_media
    """
    file = genai.upload_file(path, mime_type=mime_type)
    print(f"Uploaded file '{file.display_name}' as: {file.uri}")
    return file


# Create the model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# TODO Make these files available on the local file system
# You may need to update the file paths
files = [
    upload_to_gemini("./record_20241109_yw808q.wav", mime_type="audio/wav"),
]

chat_session = model.start_chat(
    history=[
        {
            "role": "user",
            "parts": [
                files[0],
            ],
        }
    ]
)

response = chat_session.send_message(
    "Hãy tạo một bản tóm tắt âm thanh, bao gồm bản ghi âm và thông tin người nói cho mỗi bản ghi âm, từ cuộc phỏng vấn này. Sắp xếp bản ghi âm theo thời gian chúng xảy ra.")

print(response.text)
