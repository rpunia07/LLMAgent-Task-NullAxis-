import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from src.database import init_database, get_schema_info
from src.agent import agent_workflow
from langchain_core.messages import HumanMessage

load_dotenv()

st.set_page_config(page_title="NYC 311 Analytics", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []

@st.cache_resource
def get_db():
    if not os.path.exists("data/nyc_311_data.csv"):
        st.error("Missing data/nyc_311_data.csv")
        return None
    return init_database("data/nyc_311_data.csv")

def main():
    st.title("NYC 311 Analytics Agent")
    
    with st.sidebar:
        conn = get_db()
        if conn:
            st.success("Database Ready")
            with st.expander("Schema"):
                info = get_schema_info(conn)
                if "error" in info:
                    st.error(info["error"])
                else:
                    st.json(info.get("columns", []))
        
        st.subheader("Examples")
        examples = [
            "Top 10 complaint types?",
            "Which zip code has most complaints?",
            "Complaints over time?",
            "Distribution by borough?"
        ]
        
        for ex in examples:
            if st.button(ex):
                st.session_state.current_input = ex
        
        if st.button("Clear History"):
            st.session_state.messages = []

    # Chat Interface
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("visualization"):
                st.plotly_chart(msg["visualization"], use_container_width=True)

    user_input = st.chat_input("Ask about NYC 311 data...")
    if "current_input" in st.session_state and st.session_state.current_input:
        user_input = st.session_state.current_input
        st.session_state.current_input = None
        
    if user_input and conn:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)
            
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    result = agent_workflow.invoke({
                        "messages": [HumanMessage(content=user_input)],
                        "schema_info": get_schema_info(conn),
                        "conn": conn
                    })
                    
                    response = result["final_answer"]
                    viz = result.get("visualization")
                    
                    st.markdown(response)
                    if viz:
                        st.plotly_chart(viz, use_container_width=True)
                        
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response,
                        "visualization": viz
                    })
                except Exception as e:
                    st.error(f"Error: {e}")

if __name__ == "__main__":
    main()
