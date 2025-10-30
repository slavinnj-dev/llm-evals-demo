import streamlit as st

from web_search import search
from langchain.agents import create_agent
from autoevals.llm import *

from braintrust import init_logger
from braintrust_langchain import BraintrustCallbackHandler, set_global_handler

# Show title and description.
st.title("🎤 SpotifyAI Playlist 🎵")

def select_model(option):
    if option:
        provider = ''
        model = ''
        key = ''
        if option == "Claude":
            provider = "anthropic"
            model = "claude-haiku-4-5"
            key = st.secrets["ANTHROPIC_API_KEY"]
        elif option == "Gemini":
            provider = "google_vertexai"
            model = "gemini-2.0-flash-lite"
            key = st.secrets["GEMINI_API_KEY"]
        elif option == "Mistral":
            provider = "mistralai"
            model = "mistral-small-latest"
            key = st.secrets["MISTRAL_API_KEY"]
        elif option == "Llama":
            provider = "groq"
            model = "llama-3.3-70b-versatile"
            key = st.secrets["GROQ_API_KEY"]
        elif option == "GPT-OSS":
            provider = "groq"
            model = "openai/gpt-oss-120b"
            key = st.secrets["GROQ_API_KEY"]
        elif option == "GPT 4o-mini":
            provider = "openai"
            model = "gpt-4o-mini"
            key = st.secrets["OPENAI_API_KEY"]
        elif option == "Deepseek r1 Distill":
            provider = "groq"
            model = "deepseek-r1-distill-qwen-32b"
            key = st.secrets["GROQ_API_KEY"]
        model_string = '{}:{}'.format(provider, model)
        st.write("Using model:", model_string)
        return model_string
    
def setup_model(model_string):
    system_prompt = ''
    try:
        with open("system_prompt.txt", "r") as f:
            content = f.read()
            system_prompt = content
    except FileNotFoundError:
        print("Error: System prompt not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    system_prompt = content

    tools = [search]

    bt_key = st.secrets["BRAINTRUST_API_KEY"]

    init_logger(project="Playlist Generation", api_key=bt_key)

    handler = BraintrustCallbackHandler()
    set_global_handler(handler)

    agent = create_agent(model=model_string, tools=tools, system_prompt=system_prompt)
    return agent

def stream_ai_messages(agent, inputs):
    for event in agent.stream(inputs):
        if "model" in event:
            for message in event["model"]["messages"]:
                if message.__class__.__name__ == 'AIMessage':
                    yield message.content
    

option = ''
option = st.selectbox(
    "Model",
    ("Claude", "Gemini (soon...)", "Mistral", "Llama", "GPT-OSS", "GPT 4o-mini", "Deepseek r1 Distill (soon...)"),
    index=None,
    placeholder="Select provider...",
)

if option:
    model_string = select_model(option)
    agent = setup_model(model_string)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    if prompt := st.chat_input("What are you listening to today?"):
        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        inputs = {"messages": [("user", prompt)]}


        with st.chat_message("assistant"):
            fmt_response = st.write_stream(stream_ai_messages(agent, inputs))
            st.session_state.messages.append({"role": "assistant", "content": fmt_response})