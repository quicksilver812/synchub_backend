from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json
import re

load_dotenv()

llm = ChatOpenAI(model = "gpt-4o-mini")

prompt_template = PromptTemplate.from_template("""
Given a list of keys from a data source called "{source_name}", map them to a standard unified schema for employee data.

The standard fields are: employee_id, name, salary, email, department, location.

Here are the fields: {fields}

Respond with a JSON dictionary where each source field maps to a unified field.
Only map what's available. Don't guess extra fields. Dont output any extra text, just output the json dictionary.

Example:
{{ "emp_id": "employee_id", "emp_name": "name" }}

Now give only the JSON mapping.
""")

def get_dynamic_field_mapping(source_name: str, fields: list[str]) -> dict:
    prompt = prompt_template.format(source_name=source_name, fields=fields)
    res = llm.invoke(prompt)
    raw_output = res.content.strip()

    # Extract only the JSON using a regex (robust af)
    match = re.search(r"\{.*\}", raw_output, re.DOTALL)
    if match:
        json_str = match.group(0)
        try:
            return json.loads(json_str)
        except Exception as e:
            print("Failed to parse cleaned JSON:", json_str)
            raise e
    else:
        print("Couldn’t find JSON in LLM response:", raw_output)
        raise ValueError("No valid JSON object found in response")