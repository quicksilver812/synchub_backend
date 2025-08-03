from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate
import json
import ast

llm = ChatOllama(model = "llama3.2")

prompt_template = PromptTemplate.from_template("""
Given a list of keys from a data source called "{source_name}", map them to a standard unified schema for employee data.

The standard fields are: employee_id, name, salary, email, department, location.

Here are the fields: {fields}

Respond with a JSON dictionary where each source field maps to a unified field.
Only map what's available. Don't guess extra fields.

Example:
{{ "emp_id": "employee_id", "emp_name": "name" }}

Now give only the JSON mapping.
""")

def get_dynamic_field_mapping(source_name: str, fields: list[str]) -> dict:
    prompt = prompt_template.format(source_name=source_name, fields=fields)
    res = llm.invoke(prompt)
    try:
        return json.loads(res.content)
    except Exception as e:
        print("Failed to parse mapping:", res.content)
        raise e