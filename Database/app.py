from langchain_community.utilities import SQLDatabase ##tools that allow LangChain to "read" and "understand" a database schema.
import streamlit as st 
from pathlib import Path 
from langchain_community.agent_toolkits import SQLDatabaseToolkit ,create_sql_agent## tools that allow LangChain to "read" and "understand" a database schema.
## the magic command that creates the "Chatbot" which knows how to write SQL.
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from sqlalchemy import create_engine
import psycopg2 ##  actual "cables" that plug into the PostgreSQL database.
import sqlite3 ## for connecting to local SQLite student.db
from langchain_groq import ChatGroq
from dotenv import load_dotenv
load_dotenv()

st.set_page_config(page_title="Langchain: Chat with PSQL DB")
st.title("Langchain: Chat with PSQL DB")

"""INJECTION_WARNING=
SQL agent can be vulnerable to prompt injection.
Use a DB role with limited"""

Local_db="USE_LOCALDB"
MYPSQL="USE_PSQL"
## create radio buttons

radio_opt=["Use PSQL 18- student.db","Connect to your PSQL database"]

selected_opt=st.sidebar.radio(label="Choose the db which you want to chat", 
options=radio_opt)

if radio_opt.index(selected_opt)==1:
    db_uri=MYPSQL
    mypsql_host=st.sidebar.text_input("Provide My PSQL Host")
    mypsql_user=st.sidebar.text_input("MYPSQL User")
    mypsql_password=st.sidebar.text_input("MYPSQL password",type="password")
    mypsql_db=st.sidebar.text_input("MyPSQL_database")
else:
    db_uri=Local_db

api_key=st.sidebar.text_input(label="Groq API key", type="password")

if not db_uri:
    st.info("Please enter the database information and uri")

if not api_key:
    st.info("Please enter groq api key")

## LLM Model

llm=ChatGroq(groq_api_key=api_key,
model_name="Llama-3.3-70b-versatile",
streaming=True)

@st.cache_resource(ttl="2h") 
#It tells the app: "Once you connect to the DB, 
#remember it for 2 hours so you don't have to reconnect every time I click a button."

def configure_db(db_uri,mypsql_host=None,mypsql_user=None,mypsql_password=None,mypsql_db=None):
    if db_uri==Local_db:
        dbfilepath=(Path(__file__).parent/"student.db").absolute()
        print(dbfilepath)
        creator = lambda: sqlite3.connect(f"file:{dbfilepath}?mode=ro", uri=True)
        return SQLDatabase(create_engine("sqlite:///", creator=creator))
    
    elif db_uri==MYPSQL:
        if not (mypsql_host and mypsql_user and mypsql_password and mypsql_db):
            st.error("please provide all MyPSQL connection details.")
            st.stop()
        return SQLDatabase(create_engine(f"postgresql+psycopg2://{mypsql_user}:{mypsql_password}@{mypsql_host}/{mypsql_db}"))

if db_uri==MYPSQL:
    db=configure_db(db_uri,mypsql_host,mypsql_user,mypsql_password,mypsql_db)
else:
    db=configure_db(db_uri)

toolkit=SQLDatabaseToolkit(db=db,llm=llm)

agent=create_sql_agent(
    llm=llm,
    toolkit=toolkit,
    verbose=True,
    handle_parsing_errors=True
)

if "messages" not in st.session_state or st.sidebar.button("clear message history"):
    st.session_state["messages"]=[{"role":"assistant","content":"How can i help you"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

user_query=st.chat_input(placeholder="Ask anything from the database")

if user_query:
    st.session_state.messages.append({"role":"user","content":user_query})
    st.chat_message("user").write(user_query)

    with st.chat_message("assistant"):
        streamlit_callback=StreamlitCallbackHandler(st.container())
        response=agent.run(user_query,
        callbacks=[streamlit_callback])
        st.session_state.messages.append({"role":"assistant","content":response})
        st.write(response)