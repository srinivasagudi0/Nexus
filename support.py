from openai import OpenAI
import os

# extract the code from the file
def extract_code(file):
    # Streamlit uploader returns an UploadedFile-like object with a .read() method.
    if hasattr(file, "read"):
        content = file.read()
        if isinstance(content, bytes):
            return content.decode("utf-8", errors="ignore")
        return str(content)

    # Fallback: allow passing a regular file path.
    with open(file, "r", encoding="utf-8") as f:
        return f.read()

def analyze_file_code(code):
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that analyzes code."},
            {"role": "user", "content": f"Analyze the following code:\n\n{code}"}
        ]
    )
    return response.choices[0].message.content
