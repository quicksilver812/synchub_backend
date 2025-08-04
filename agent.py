from dotenv import load_dotenv

from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.utilities.sql_database import SQLDatabase

from langchain_openai import ChatOpenAI
import os

load_dotenv()

# Make sure this path points to your existing SQLite DB file
sqlite_db_path = "sqlite:///./employees.db"

# Setup LangChain LLM
llm = ChatOpenAI(model="gpt-4o-mini") 

# Setup LangChain SQL Database wrapper
db = SQLDatabase.from_uri(sqlite_db_path)

# Create agent with SQL toolkit
sql_agent = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
)