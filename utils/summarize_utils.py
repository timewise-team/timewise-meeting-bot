import google.generativeai as genai
from transformers import pipeline

# Initialize the summarization and text correction pipelines
# summarizer = pipeline("summarization", model="VietAI/vit5-large-vietnews-summarization", device="mps")
# corrector = pipeline("text2text-generation", model="bmd1905/vietnamese-correction-v2", device="mps")


# def generate_summary(raw_transcript):
#     """
#     Generates a detailed summary for a given raw transcript text.
#
#     Parameters:
#     - raw_transcript (str): The raw text of the meeting or document transcript.
#
#     Returns:
#     - str: The generated summary text.
#     """
#     # Normalize the text using the correction model
#     normalized_text = corrector(raw_transcript, max_length=len(raw_transcript))[0]['generated_text']
#     print("Normalized Text:", normalized_text)
#
#     # Generate the summary with adjusted parameters for detail and variety
#     summary_output = summarizer(
#         normalized_text,
#         max_length=int(len(normalized_text) / 2),
#         min_length=min(int(len(normalized_text) / 3), 150),
#         do_sample=True,
#         temperature=0.4,
#         num_return_sequences=1
#     )
#     summary_text = summary_output[0]['summary_text']
#
#     # Correct any grammatical or typographical errors in the generated summary
#     normalized_summary_text = corrector(summary_text, max_length=len(summary_text))[0]['generated_text']
#
#     # # Write output to file (optional)
#     # with open("meeting_summary.txt", "w") as file:
#     #     file.write("Raw Transcript:\n")
#     #     file.write(raw_transcript + "\n\n")
#     #     file.write("-----------------------------\n\n")
#     #     file.write("Meeting Summary:\n")
#     #     file.write(normalized_summary_text + "\n\n")
#     #
#     # print("Summary and key highlights saved to 'meeting_summary.txt'")
#
#     return normalized_summary_text


GEMINI_API_KEY = 'AIzaSyA0M39VosZ1OWtQ62ggMqRh-m3cC08fyyA'

genai.configure(api_key=GEMINI_API_KEY)


def generate_summary__gemini(raw_transcript):
    # Normalize the text using the correction model
    # normalized_text = corrector(raw_transcript, max_length=len(raw_transcript))[0]['generated_text']
    # print("Normalized Text:", normalized_text)

    print("Raw Transcript:", raw_transcript)

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

    chat_session = model.start_chat()

    response = chat_session.send_message(
        f"no yapping, "
        f"đây là cuộc họp giữa nhiều người, "
        f"tóm tắt nội dung cuộc họp bên dưới, chi tiết nhất có thể, nêu rõ các điểm chính được đề cập trong cuộc họp, "
        f"chỉ trả về một đoạn text tóm tắt có thể lưu vào database luôn, không trả thêm gì khác, không trả câu hỏi thêm, "
        f"không trả lời mở đầu, chỉ trả về kết quả tóm tắt: {raw_transcript}")

    print(response.text)

    return response.text
