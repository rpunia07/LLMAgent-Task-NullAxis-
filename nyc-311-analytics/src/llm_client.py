from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

def create_deepseek_client(api_key, base_url):
    return ChatOpenAI(
        model="deepseek-chat",
        openai_api_key=api_key,
        openai_api_base=base_url,
        temperature=0
    )

def generate_sql_query(llm, user_question, schema_info):
    template = """Generate a DuckDB SQL query for this question.
    
    Schema: {schema_info}
    Question: {user_question}
    
    Rules:
    - Table name is `data`
    - Use DuckDB syntax
    - Return ONLY the SQL
    - LIMIT 100 unless asked otherwise
    """
    
    chain = ChatPromptTemplate.from_template(template) | llm | StrOutputParser()
    return chain.invoke({"schema_info": str(schema_info), "user_question": user_question})
