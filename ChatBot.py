import os
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env', encoding='utf-16')
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY=os.getenv("TAVILY_API_KEY")

#####CREATE LLM ###########
from langchain_groq import ChatGroq
llm=ChatGroq(model_name="llama3-8b-8192", api_key=GROQ_API_KEY)

##### Creating State Graph   ######

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
from typing import Annotated
from langgraph.prebuilt import ToolNode, tools_condition

class State(TypedDict):
  messages : Annotated[list, add_messages]

graph_builder= StateGraph(State)
tool=TavilySearchResults(api_key=TAVILY_API_KEY, max_results=2)
tools=[tool]

llm_with_tools= llm.bind_tools(tools)

def chatBot(state : State):
    return {"messages":[llm_with_tools.invoke(state["messages"])]}

graph_builder.add_node("chatBot", chatBot)

tool_node = ToolNode(tools=[tool])
graph_builder.add_node("tools", tool_node)

# tools condition will determine whether to stay in chatBot node or go to Tools node
graph_builder.add_conditional_edges("chatBot",tools_condition)

# Any time a tool is called, we return to the chatbot to decide the next step
graph_builder.add_edge("tools", "chatBot")
graph_builder.set_entry_point("chatBot")


## Add memory to chatBot
from langgraph.checkpoint.memory import MemorySaver
memory=MemorySaver()

## compile graph with memory
graph=graph_builder.compile(checkpointer=memory)


####### UI Part- using streamlit #######
import streamlit as st
st.title("Manika's ChatBot")


if "messages" not in st.session_state:
 st.session_state.messages=[]

def stream_user_input(userInput):
    st.session_state.messages.append(("user",userInput))
    assistantResponse=""
     ### st.chat_message () feature in Streamlit is used to create chat-like message interfaces within Streamlit apps. 
    ####It provides a conversational-style UI, where you can display user and assistant messages dynamically. 
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        for event in graph.stream({"messages":[{"role":"user", "content":userInput}]}, {"configurable":{"thread_id":1}}):
            for value in event.values():
                newText=value["messages"][-1].content
                assistantResponse+=newText
                message_placeholder.markdown(assistantResponse)

    st.session_state.messages.append(("assistant", assistantResponse))

### display chat history
for role, message in st.session_state.messages:
    with st.chat_message(role):
        st.markdown(message)

if prompt := st.chat_input("What is your question?"):

    with st.chat_message("user"):
        st.markdown(prompt)

    response=stream_user_input(prompt)




