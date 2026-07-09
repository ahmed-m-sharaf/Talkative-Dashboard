import streamlit as st

from engine import dashboard_engine
from frontend.components import render_response



st.set_page_config(
    page_title="Talkative Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Talkative Dashboard")

st.caption(
    "AI-powered Recruitment Analytics Dashboard"
)

st.divider()


if "messages" not in st.session_state:
    st.session_state.messages = []



with st.sidebar:

    st.header("Examples")

    st.markdown(
        """
- Average age of Software Engineers

- Average age of Software Engineers in Cairo

- Top skills for AI Engineer

- Rejected applications from LinkedIn

- Average salary expectation for AI Engineer

- Count accepted applications
"""
    )

    st.divider()

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()



for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        if message["role"] == "user":

            st.write(message["content"])

        else:

            render_response(message["content"])



prompt = st.chat_input(
    "Ask your recruitment analytics question..."
)



if prompt:


    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    with st.chat_message("user"):

        st.write(prompt)


    with st.spinner("Thinking..."):

        response = dashboard_engine.run(prompt)


    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

 
    with st.chat_message("assistant"):
        render_response(response)