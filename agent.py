from dotenv import load_dotenv

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase

from langchain_openai import ChatOpenAI
import os

load_dotenv()

# Make sure this path points to your existing SQLite DB file
sqlite_db_path = "sqlite:///./employees.db"

system_prompt = """
You are a helpful assistant that answers questions about employee data using SQL.

Always try to generate a SQL query, even if you're unsure. Never respond with "I don't know".
"""

# Setup LangChain LLM
llm = ChatOpenAI(model="gpt-4o-mini") 

# Setup LangChain SQL Database wrapper
db = SQLDatabase.from_uri(sqlite_db_path)

# Create agent with SQL toolkit
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
    handle_parsing_errors=True,  # Add this argument
    prefix=system_prompt
)