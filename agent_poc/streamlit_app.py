import streamlit as st
from main_graph import process_query_graph as process_query
from memory import MemoryManager
from langchain_core.messages import HumanMessage, AIMessage


st.set_page_config(
    page_title="AI Agent POC",
    page_icon="🤖",
    layout="centered"
)

if "memory" not in st.session_state:
    st.session_state.memory = MemoryManager()

st.title("🤖 Role-Based AI Agent")
st.markdown("*A proof-of-concept demonstrating routing, tool usage, and evaluation*")

if st.sidebar.button("Reset Memory"):
    st.session_state.memory.clear()
    st.rerun()

st.divider()

# Display chat history from memory
for message in st.session_state.memory.get_messages():
    if isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.markdown(message.content)
    elif isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)

# Chat input
if user_query := st.chat_input("Enter your question..."):
    # Display user message immediately
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.spinner("Processing..."):
        try:
            # Process result
            result = process_query(user_query, st.session_state.memory)
            
            # Display assistant response
            with st.chat_message("assistant"):
                if result["passed_evaluation"]:
                    st.markdown(result["answer"])
                else:
                    st.warning(f"Note: This answer did not pass the automated evaluation.\n\n{result['answer']}")
                
                with st.expander("View Intermediate Steps"):
                    for step in result["steps"]:
                        step_name = step.get("step", "Unknown")
                        st.markdown(f"**{step_name}**")
                        
                        for key, value in step.items():
                            if key != "step":
                                st.text(f"  {key}: {value}")
                        
                        st.divider()
                        
        except Exception as e:
            st.error(f"Error: {str(e)}")
            st.info("Make sure GROQ_API_KEY environment variable is set.")
            if "memory" in st.session_state:
                # Still show history even on error if possible
                pass
