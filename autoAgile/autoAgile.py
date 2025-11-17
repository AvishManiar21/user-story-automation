"""Main module."""
import json
import sys
from utils.prompts import *

from save_output import *



api_key = os.environ['auth_key']

DOC = sys.argv[1]
temp = 0.3
Model = ""
prod = "prod"
debug = "debug"
mode = prod
try:
    Model = sys.argv[2] 
except:
    Model = "gpt-4-turbo" 

print(f"model is {Model}")

if __name__ == "__main__":
    chat = ChatOpenAI(model=Model, temperature=temp, openai_api_key=api_key)
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


    
