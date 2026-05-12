from langchain_community.tools import DuckDuckGoSearchRun
import streamlit as st
from langchain_groq import ChatGroq
from langchain_community.tools import ArxivQueryRun, WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper,ArxivAPIWrapper
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
import os
from dotenv import load_dotenv

load_dotenv()

arxiv_wrapper=ArxivAPIWrapper(top_k_results=1,
doc_content_chars_max=250)

arxiv=ArxivQueryRun(api_wrapper=arxiv_wrapper)

wiki_wrapper=WikipediaAPIWrapper(top_k_results=1,
doc_content_chars_max=250)

wiki=WikipediaQueryRun(api_wrapper=wiki_wrapper)

search=DuckDuckGoSearchRun(name="search")

if "messages" not in st.session_state:
    st.session_state["messages"]=[
        {"role":"assistant","content":
        """Hi, i am a chatbot who can search the web.
        How can i help you today?"""}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg['content'])

if prompt:=st.chat_input(placeholder="What is machine learning"):
    st.session_state.messages.append({
        "role":"user",
        "content":prompt
    })
    st.chat_message("user").write(prompt)
    
    llm=ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"),
             model_name="qwen/qwen3-32b",
             streaming=True)
    tools=[search,arxiv,wiki]

    search_agent=create_agent(
        model=llm,
        tools=tools,
        system_prompt="You are a helpful assistant who can search the web using Arxiv, Wikipedia, and DuckDuckGo."
    )

    with st.chat_message("assistant"):
        st_cb=StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        response=search_agent.invoke({"messages":[{"role":"user","content":prompt}]}, config={"callbacks":[st_cb]})
        
        # Extract the response from the message list
        final_response = response["messages"][-1].content
        st.session_state.messages.append({"role":"assistant", "content":final_response})
        st.write(final_response)





