"""Main module."""
import json
import sys
import os
from utils.prompts import *
from langchain_ollama import ChatOllama

from save_output import *


# Ollama configuration (no API key needed)
OLLAMA_BASE_URL = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3.2')

DOC = sys.argv[1]
temp = 0.3
Model = ""
prod = "prod"
debug = "debug"
mode = prod
try:
    Model = sys.argv[2] 
except:
    Model = OLLAMA_MODEL  # Use Ollama model by default

print(f"model is {Model}")
print(f"Using Ollama at: {OLLAMA_BASE_URL}")

if __name__ == "__main__":
    # Use Ollama instead of OpenAI (no API key needed)
    chat = ChatOllama(
        model=Model,
        temperature=temp,
        base_url=OLLAMA_BASE_URL
    )
    # Replace 'your_file.docx' with the path to your DOCX file
    docx_path = DOC
    extracted_text = ""
    try:
        extracted_text = extract_text_from_docx(docx_path)
        if mode == debug:
            print("Text extracted successfully:\n")
            print("=============================\n")
            print(extracted_text)
            print("=============================\n")
    except Exception as e:
        print("Error extracting text:", str(e))
    requirements = rat(refine_doc, extract_functionarity, extracted_text, chat, mode)
    print(requirements)
    deliverables = rat(refine_requirements, extract_epics, requirements, chat, mode)
    if mode == debug:
        print(deliverables)
    epics = get_epics(deliverables, chat)
    test_cases = rat(refine_requirements, generate_test_cases, requirements, chat,mode)
    #test_cases is in json text already
    print(epics)
    print(test_cases)

    # save the output into a file
    save_json_output(requirements, epics, test_cases,docx_path)


    
