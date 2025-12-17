from typing import TypedDict, List, Annotated
import operator
from langchain_core.messages import AnyMessage, HumanMessage
from langgraph.graph import StateGraph, END
from src.database import execute_query
from src.llm_client import generate_sql_query, create_deepseek_client
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    messages: Annotated[List[AnyMessage], operator.add]
    user_question: str
    schema_info: dict
    sql_query: str
    query_results: any
    final_answer: str
    visualization: any
    conn: any

def get_llm():
    return create_deepseek_client(
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_API_BASE")
    )

def understand_question_node(state):
    return {"user_question": state["messages"][-1].content}

def generate_sql_node(state):
    llm = get_llm()
    sql = generate_sql_query(llm, state["user_question"], state["schema_info"])
    return {"sql_query": sql.replace("```sql", "").replace("```", "").strip()}

def execute_query_node(state):
    try:
        df = execute_query(state["conn"], state["sql_query"])
        return {"query_results": df}
    except Exception as e:
        return {"query_results": f"Error: {str(e)}"}

def format_response_node(state):
    llm = get_llm()
    results = state["query_results"]
    results_str = results.to_string() if isinstance(results, pd.DataFrame) else str(results)
    
    template = """Explain these query results for the user's question.
    
    Question: {user_question}
    Results: {results}
    
    Provide a direct answer and key stats.
    """
    
    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()
    response = chain.invoke({"user_question": state["user_question"], "results": results_str})
    return {"final_answer": response}

def visualize_data_node(state):
    df = state["query_results"]
    viz = None
    
    if isinstance(df, pd.DataFrame) and not df.empty:
        try:
            if len(df.columns) == 2:
                col1, col2 = df.columns
                if pd.api.types.is_numeric_dtype(df[col2]):
                    viz = px.bar(df, x=col1, y=col2)
                elif pd.api.types.is_numeric_dtype(df[col1]):
                    viz = px.bar(df, x=col2, y=col1)
            elif "created_date" in df.columns:
                 num_cols = df.select_dtypes(include=['number']).columns
                 if len(num_cols) > 0:
                     viz = px.line(df, x="created_date", y=num_cols[0])
        except:
            pass
            
    return {"visualization": viz}

def should_visualize(state):
    q = state["user_question"].lower()
    if any(x in q for x in ["plot", "chart", "graph", "visualize"]):
        return "visualize"
    if isinstance(state["query_results"], pd.DataFrame) and not state["query_results"].empty:
        if len(state["query_results"]) > 1:
            return "visualize"
    return "end"

graph = StateGraph(AgentState)
graph.add_node("understand_question", understand_question_node)
graph.add_node("generate_sql", generate_sql_node)
graph.add_node("execute_query", execute_query_node)
graph.add_node("format_response", format_response_node)
graph.add_node("visualize_data", visualize_data_node)

graph.set_entry_point("understand_question")
graph.add_edge("understand_question", "generate_sql")
graph.add_edge("generate_sql", "execute_query")
graph.add_edge("execute_query", "format_response")
graph.add_conditional_edges("format_response", should_visualize, {"visualize": "visualize_data", "end": END})
graph.add_edge("visualize_data", END)

agent_workflow = graph.compile()
