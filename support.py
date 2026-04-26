from openai import OpenAI
import os

# extract the code from the file
def extract_code(file):
    with open(file, 'r') as f:
        code = f.read()
    return code

