import google.generativeai as genai

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

    # response = chat_session.send_message(
    #     f"Bạn là một trợ lý AI chuyên nghiệp, được thiết kế để tóm tắt các đoạn hội thoại dài từ nhiều người. "
    #     f"Đây là một đoạn hội thoại đã được chuyển từ âm thanh sang văn bản. "
    #     f"Đoạn văn bản có thể chứa các từ không chính xác hoặc nhiễu do âm thanh môi trường hoặc nhiều người cùng nói một lúc. "
    #     f"Hãy tóm tắt nội dung chính, đảm bảo: Loại bỏ các từ ngữ nhiễu hoặc không liên quan. "
    #     f"Giữ lại các ý chính, thông tin quan trọng và kết luận (nếu có). "
    #     f"Quan trọng: Đảm bảo tóm tắt bằng ngôn ngữ giống với ngôn ngữ của đoạn văn bản đầu vào dưới đây (tiếng Anh hoặc tiếng Việt). "
    #     f"Nếu đoạn hội thoại dưới đây là tiếng Việt, hãy trả kết quả tóm tắt bằng tiếng Việt. "
    #     f"Nếu đoạn hội thoại dưới đây là tiếng Anh, hãy trả kết quả tóm tắt bằng tiếng Anh. "
    #     f"Đoạn hội thoại: {raw_transcript} "
    #     f"Yêu cầu đầu ra: Chỉ trả về đoạn text tóm tắt nội dung, không có lời dẫn dắt hay chú thích thêm. "
    # )
    response = chat_session.send_message(
        f"Bạn là một trợ lý AI chuyên nghiệp, được thiết kế để tóm tắt các đoạn hội thoại dài từ nhiều người. "
        f"Đây là một đoạn hội thoại đã được chuyển từ âm thanh sang văn bản. "
        f"Đoạn văn bản có thể chứa các từ không chính xác hoặc nhiễu do âm thanh môi trường hoặc nhiều người cùng nói một lúc. "
        f"Hãy tóm tắt nội dung chính, đảm bảo: "
        f"- Loại bỏ các từ ngữ nhiễu hoặc không liên quan. "
        f"- Giữ lại các ý chính, thông tin quan trọng và kết luận (nếu có). "
        f"- Đảm bảo rằng đầu ra dưới dạng các ý chính được liệt kê theo gạch đầu dòng. "
        f"- Đảm bảo tóm tắt bằng ngôn ngữ giống với ngôn ngữ của đoạn văn bản đầu vào dưới đây (tiếng Anh hoặc tiếng Việt). "
        f"- Nếu đoạn hội thoại dưới đây là tiếng Việt, hãy trả kết quả tóm tắt bằng tiếng Việt. "
        f"- Nếu đoạn hội thoại dưới đây là tiếng Anh, hãy trả kết quả tóm tắt bằng tiếng Anh. "
        f"Đoạn hội thoại: {raw_transcript} "
        f"Yêu cầu đầu ra: Chỉ trả về các ý chính dưới dạng gạch đầu dòng, không có lời dẫn dắt hay chú thích thêm. "
    )
    print(response.text)

    return response.text


if __name__ == "__main__":
    raw_transcript = (
        f"Alright, let's start our retrospective. What went well in this sprint, Đức Anh? "
        f"Well, I think the implementation of the new email synchronisation feature went smoothly. The unit tests were comprehensive, and we caught a few bugs early on. "
        f"Also, the team collaboration on the frontend design was really effective. "
        f"That's great to hear! I agree. The design team did a fantastic job. What about any challenges or roadblocks? "
        f"We did run into some issues with the API integration. The endpoint for fetching user data was inconsistent, which caused some delays. "
        f"Also, the deployment process could be streamlined. It took longer than expected to deploy the latest build. "
        f"Good point. We definitely need to improve the API integration process and streamline the deployment pipeline. Any other thoughts? "
        f"I think we could improve our communication around task prioritization. Sometimes, it's unclear which tasks are the highest priority, "
        f"leading to some confusion and delays. "
        f"That's a valid point. We'll address that in our next sprint planning meeting. Let's summarize our action items: "
        f"Improve API integration process: Investigate the root cause of the inconsistency and work with the backend team to improve the endpoint reliability. "
        f"Streamline deployment pipeline: Automate the deployment process as much as possible to reduce manual intervention and potential errors. "
        f"Enhance task prioritization communication: Hold regular stand-up meetings to discuss priorities and any roadblocks. "
        f"Sounds good. Let's work on these and make the next sprint even more productive. "
        f"Great. Thanks, Đức Anh. Let's wrap up this retrospective."
    )
    # raw_transcript = "Hello, how are you?"
    summary = generate_summary__gemini(raw_transcript)
