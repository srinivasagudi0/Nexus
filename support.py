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
            {
                "role": "system",
                "content": (
                    "You are a senior code reviewer. Return analysis in exactly this order:\n"
                    "Summary:\n"
                    "- ...\n\n"
                    "Risks:\n"
                    "- ...\n\n"
                    "Suggestions:\n"
                    "- ...\n\n"
                    "Use short bullet points. If nothing is notable in a section, write '- None'. "
                    "Do not add extra headings."
                ),
            },
            {
                "role": "user",
                "content": f"Analyze the following code:\n\n{code}",
            },
        ],
    )
    return response.choices[0].message.content


# extract zip file and return the code in the zip file as a string
def extract_zip(file):
    import zipfile
    import io

    if hasattr(file, "read"):
        with zipfile.ZipFile(io.BytesIO(file.read())) as z:
            code = ""
            for filename in z.namelist():
                if filename.endswith((".py", ".txt")):
                    with z.open(filename) as f:
                        content = f.read()
                        if isinstance(content, bytes):
                            code += content.decode("utf-8", errors="ignore") + "\n"
                        else:
                            code += str(content) + "\n"
            return code
    else:
        with zipfile.ZipFile(file, "r") as z:
            code = ""
            for filename in z.namelist():
                if filename.endswith((".py", ".txt")):
                    with z.open(filename) as f:
                        content = f.read()
                        if isinstance(content, bytes):
                            code += content.decode("utf-8", errors="ignore") + "\n"
                        else:
                            code += str(content) + "\n"
            return code
