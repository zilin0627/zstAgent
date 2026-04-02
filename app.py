import time
import streamlit as st
from agent.react_agent import ReactAgent

# 标题
st.title("智扫通机器人智能客服")
st.divider()

if "agent" not in st.session_state:
    st.session_state.agent = ReactAgent()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    st.chat_message(message["role"]).write(message["content"])

# 用户提示词
prompt = st.chat_input()

if prompt:
    st.chat_message("user").write(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})


    response_message = []
    with st.spinner("智能客服思考中..."):
        response_stream = st.session_state.agent.execute_stream(prompt)

        def capture_response(generator, cache_list):
            for chunk in generator:
                cache_list.append(chunk)

                for char in chunk:
                    time.sleep(0.01)
                    yield char
            
        st.chat_message("assistant").write_stream(capture_response(response_stream, response_message))
        st.session_state["messages"].append({"role": "assistant", "content": response_message[-1]})
        st.rerun()
            
           