from transformers import pipeline

# Initialize the summarization and text correction pipelines
summarizer = pipeline("summarization", model="VietAI/vit5-large-vietnews-summarization", device="mps")
corrector = pipeline("text2text-generation", model="bmd1905/vietnamese-correction-v2", device="mps")

def generate_summary(raw_transcript):
    """
    Generates a detailed summary for a given raw transcript text.

    Parameters:
    - raw_transcript (str): The raw text of the meeting or document transcript.

    Returns:
    - str: The generated summary text.
    """
    # Normalize the text using the correction model
    normalized_text = corrector(raw_transcript, max_length=len(raw_transcript))[0]['generated_text']
    print("Normalized Text:", normalized_text)

    # Generate the summary with adjusted parameters for detail and variety
    summary_output = summarizer(
        normalized_text,
        max_length=int(len(normalized_text) / 2),
        min_length=min(int(len(normalized_text) / 3), 150),
        do_sample=True,
        temperature=0.4,
        num_return_sequences=1
    )
    summary_text = summary_output[0]['summary_text']

    # Correct any grammatical or typographical errors in the generated summary
    normalized_summary_text = corrector(summary_text, max_length=len(summary_text))[0]['generated_text']

    # # Write output to file (optional)
    # with open("meeting_summary.txt", "w") as file:
    #     file.write("Raw Transcript:\n")
    #     file.write(raw_transcript + "\n\n")
    #     file.write("-----------------------------\n\n")
    #     file.write("Meeting Summary:\n")
    #     file.write(normalized_summary_text + "\n\n")
    #
    # print("Summary and key highlights saved to 'meeting_summary.txt'")

    return normalized_summary_text
