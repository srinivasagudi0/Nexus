import io
import json
import os
import zipfile
from datetime import date, datetime, timedelta

from openai import APIError, APITimeoutError, OpenAI, OpenAIError, RateLimitError


OK_TYPES = [".py", ".txt", ".zip"]


def validate_upload(file):
    # checking the file type here
    if file is None:
        return False, "Please upload a file first."

    name = getattr(file, "name", "")
    name = str(name).lower()

    good = False
    for x in OK_TYPES:
        if name.endswith(x):
            good = True

    if good:
        return True, ""
    return False, "Only .py, .txt, and .zip files can be uploaded."


def extract_code(file):
    if hasattr(file, "read"):
        data = file.read()
        if isinstance(data, bytes):
            return data.decode("utf-8", errors="ignore")
        return str(data)

    f = open(file, "r", encoding="utf-8")
    data = f.read()
    f.close()
    return data


def extract_zip(file):
    text = ""

    if hasattr(file, "read"):
        temp = io.BytesIO(file.read())
        z = zipfile.ZipFile(temp)
    else:
        z = zipfile.ZipFile(file, "r")

    with z:
        names = z.namelist()
        for name in names:
            low = name.lower()
            if low.endswith(".py") or low.endswith(".txt"):
                f = z.open(name)
                data = f.read()
                f.close()
                data = data.decode("utf-8", errors="ignore")
                text = text + "\n\n# file: " + name + "\n"
                text = text + data

    return text.strip()


def get_code_from_upload(file):
    ok, msg = validate_upload(file)
    if not ok:
        return "", msg

    name = str(getattr(file, "name", "")).lower()
    try:
        if name.endswith(".zip"):
            code = extract_zip(file)
        else:
            code = extract_code(file)
    except zipfile.BadZipFile:
        return "", "That ZIP file could not be opened."
    except Exception as e:
        return "", "I could not read that file: " + str(e)

    if code.strip() == "":
        return "", "I did not find any .py or .txt code to analyze."
    return code, ""


def has_api_key():
    if os.environ.get("OPENAI_API_KEY"):
        return True
    return False


def analyze_file_code(code):
    try:
        bot = OpenAI(timeout=30)
        answer = bot.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Look at the code and answer with exactly these sections:\n"
                        "Summary:\n- ...\n\n"
                        "Risks:\n- ...\n\n"
                        "Suggestions:\n- ..."
                    ),
                },
                {"role": "user", "content": "Here is the code:\n\n" + code},
            ],
        )
        return answer.choices[0].message.content, None
    except RateLimitError:
        return None, "OpenAI rate limit hit. Please wait a bit and try again."
    except APITimeoutError:
        return None, "OpenAI took too long to answer. Please try again."
    except APIError as e:
        return None, "OpenAI had an API problem: " + str(e)
    except OpenAIError as e:
        return None, "OpenAI could not finish the request: " + str(e)
    except Exception as e:
        return None, "Something went wrong during analysis: " + str(e)


def make_tasks_from_goal(goal):
    try:
        bot = OpenAI(timeout=30)
        answer = bot.chat.completions.create(
            model="gpt-4o",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Make tasks from this goal. Send JSON only. "
                        "Use this shape: "
                        '{"tasks":[{"title":"name","details":"what to do","due_date":"YYYY-MM-DD or empty"}]}. '
                        "Make about 4 to 7 tasks."
                    ),
                },
                {"role": "user", "content": goal},
            ],
        )

        raw = answer.choices[0].message.content
        data = json.loads(raw)
        tasks = data.get("tasks", [])
        new_tasks = []

        for x in tasks:
            title = str(x.get("title", "")).strip()
            details = str(x.get("details", "")).strip()
            due = str(x.get("due_date", "")).strip()
            if title != "":
                new_tasks.append({"title": title, "details": details, "due_date": due})

        return new_tasks, None
    except json.JSONDecodeError:
        return None, "The AI answered, but it did not send valid JSON."
    except RateLimitError:
        return None, "OpenAI rate limit hit. Please wait a bit and try again."
    except APITimeoutError:
        return None, "OpenAI took too long to answer. Please try again."
    except APIError as e:
        return None, "OpenAI had an API problem: " + str(e)
    except OpenAIError as e:
        return None, "OpenAI could not finish the request: " + str(e)
    except Exception as e:
        return None, "Something went wrong making tasks: " + str(e)


def read_date(text):
    if not text:
        return None
    try:
        return datetime.strptime(text, "%Y-%m-%d").date()
    except ValueError:
        return None


def find_risks(tasks, today=None):
    if today is None:
        today = date.today()

    risks = []
    close_day = today + timedelta(days=3)

    for task in tasks:
        status = task.get("status", "pending")
        due = read_date(task.get("due_date"))

        if due is not None and status != "completed":
            name = task.get("title", "Untitled task")
            if due < today:
                risks.append({
                    "level": "High",
                    "task": name,
                    "message": name + " is past due and is still " + status + ".",
                })
            elif due <= close_day:
                risks.append({
                    "level": "Medium",
                    "task": name,
                    "message": name + " is due soon and is still " + status + ".",
                })

    return risks
