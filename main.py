from src.reac import  run_agent, validate_email_dict, extract_email_message
from src.nodes import execute_tools, run_agent_reasoning_engine
from src.state import AgentState

from langchain_core.agents import AgentFinish
from langgraph.graph import END, StateGraph



from dotenv import load_dotenv
load_dotenv()

AGENT_REASON = 'agent_reason'
ACT = 'act'

################### Agent Workflow
def should_continue(state: AgentState) -> str:
    if isinstance(state['agent_outcome'], AgentFinish):
        return END
    else:
        return ACT


################### Graph Workflow
def create_flow():
    try:
        flow = StateGraph(AgentState)
        flow.add_node(AGENT_REASON, run_agent_reasoning_engine)
        flow.add_node(ACT, execute_tools)
        
        flow.set_entry_point(AGENT_REASON)
        flow.add_conditional_edges(AGENT_REASON, should_continue)
        flow.add_edge(ACT, AGENT_REASON)
        return flow.compile()
    except Exception as e:
        print(f"Error creando flujo: {str(e)}")
        return None
    
app = create_flow()

test_email_01 = {
        "id":"002",
        "from":"curious.shopper@example.com",
        "subject":"Question about product specifications",
        "body":"Hi, I'm interested in buying your premium package but I couldn't find information about whether it's compatible with Mac OS. Could you please clarify this? Thanks!",
        "timestamp":"2024-03-15T11:45:00Z"
    }

test_email_02 = {
        "id":"001",
        "from":"angry.customer@example.com",
        "subject":"Broken product received",
        "body":"I received my order #12345 yesterday but it arrived completely damaged. This is unacceptable and I demand a refund immediately. This is the worst customer service I've experienced.",
        "timestamp":"2024-03-15T10:30:00Z"
    }

test_email_03 = {
        "id":"005",
        "from":"business.client@example.com",
        "subject":"Partnership opportunity",
        "body":"Our company is interested in exploring potential partnership opportunities with your organization. Would it be possible to schedule a call next week to discuss this further?",
        "timestamp":"2024-03-15T15:00:00Z"
    }

test_email_04 = {
    "id": "006",
    "from": "newsletter@example.com",
    "subject": "Upcoming Maintenance Notice",
    "body": "Please be advised that our website will be undergoing scheduled maintenance on Saturday, March 23rd, from 2:00 AM to 6:00 AM PST. During this time, the site may be temporarily unavailable. We apologize for any inconvenience.",
    "timestamp": "2024-03-16T09:00:00Z"
}

data = test_email_04

data_validation_result = validate_email_dict(data)

if data_validation_result['valid']:
    email_input = extract_email_message(data)
    print("Valid input:", email_input)
else:
    print("Validation Errors:", data_validation_result['errors'])


run_agent(email_input)

if __name__ == '__main__':    
    print('!!!! Hello reAct agent !!!!')