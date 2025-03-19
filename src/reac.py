from langchain.agents import AgentExecutor
from langchain.agents import create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from datetime import datetime
import re
import os

from src.tools import (    
    classify_email_content,
    handle_complaint,
    handle_inquiry,
    handle_support_request,
    handle_feedback,
    handle_other
)

from dotenv import load_dotenv

load_dotenv()
GOOGLE_APY_KEY= os.getenv("GOOGLE_API_KEY")

################################ reAct agent prompt
react_prompt = PromptTemplate(
    template='''
    Classify incoming emails and automate responses based on the classification.. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: A response to the the received email.

Begin!

Question: {input}
Thought:{agent_scratchpad}
'''
)

######################## Tools
def get_tools():
    return [
        classify_email_content,
        handle_complaint,
        handle_inquiry,
        handle_support_request,
        handle_feedback,
        handle_other
        ]

######################## llm model
def get_llm():
    try:
        return ChatGoogleGenerativeAI(model='gemini-1.5-flash-latest', temperature=0, google_api_key= GOOGLE_APY_KEY)
    except Exception as e:
        print(f"Error starting LLM: {str(e)}")
        return None

######################## Agent functions
def get_agent_runnable():
    llm = get_llm()
    if llm is None:
        return None
    
    tools = get_tools()
    
    try:
        return create_react_agent(llm, tools, react_prompt) # Agent runnable
    except Exception as e:
        print(f"Error creando agente: {str(e)}")
        return None
    
def get_agent_executor():
    agent = get_agent_runnable()
    if agent is None:
        return None
    
    tools = get_tools()
    
    try:
        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True
        )
    except Exception as e:
        print(f"Executor Error: {str(e)}")
        return None

    
def run_agent(query:dict)->str:
    agent_executor = get_agent_executor()
    if agent_executor is None:
        return "Error: Can't runb agent"
    
    try:
        response = agent_executor.invoke({"input": query})
        return response['output']
    except Exception as e:
        print(f"Error ejecutando agente: {str(e)}")
        return f"Error: {str(e)}"
    
######################## Data Validation functions

def extract_email_message(email_dict: dict) -> str:
    """
    Extracts and combines the subject and body of a single email into a single string.    
    :params email_dict: A dictionary containing 'subject' and 'body' keys 
    :email_dict: dict   
    :returns:a string containing the subject and body of the email
    :rtype: str
    """
    subject = email_dict.get('subject', '')
    body = email_dict.get('body', '')
    
    # Combine subject and body with a space between them
    combined_text = f"{subject} {body}"
    
    return combined_text


def validate_email_dict(email_dict: dict) -> dict:
    """
    Validates that the email message meets the expected format.
    
    :param email_dict: Dictionary representing an email message.
    :type email_dict: dict
    :return: Dictionary with two keys: 'valid' (boolean) and 'errors' (list of errors).
    :rtype: dict    
    """
    
    result = {
        'valid': True,
        'errors': []
    }
    
    # Check that all required keys exist
    required_keys = ['id', 'from', 'subject', 'body', 'timestamp']
    for key in required_keys:
        if key not in email_dict:
            result['valid'] = False
            result['errors'].append(f"Missing key '{key}'")
    
    # If keys are missing, return early
    if not all(key in email_dict for key in required_keys):
        return result
    
    # Validate ID format
    if not re.match(r'^\d{3}$', email_dict['id']):
        result['valid'] = False
        result['errors'].append(f"ID '{email_dict['id']}' doesn't have the correct format (should be 3 digits)")
    
    # Validate email format
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email_dict['from']):        
        result['valid'] = False
        result['errors'].append(f"Invalid email address '{email_dict['from']}'")
    # Validate that subject is not empty
    if not email_dict['subject'].strip():
        result['valid'] = False
        result['errors'].append(f"Subject is empty")
    
    # Validate that body is not empty
    if not email_dict['body'].strip():
        result['valid'] = False
        result['errors'].append(f"Message body is empty")
    
    # Validate timestamp format
    try:
        # Usamos strptime en lugar de fromisoformat
        datetime.strptime(email_dict['timestamp'], '%Y-%m-%dT%H:%M:%SZ')
    except ValueError:
        result['valid'] = False
        result['errors'].append(f"Invalid timestamp format '{email_dict['timestamp']}'")
    
    return result