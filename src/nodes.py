from langgraph.prebuilt import ToolNode
from langchain_core.agents import AgentAction, AgentFinish

from dotenv import load_dotenv

load_dotenv()

def run_agent_reasoning_engine(state):    # Agent node
    """
    Runs the agent's reasoning engine.
    Args:
    state (AgentState): The agent's current state
    Returns:
    dict: A dictionary with the key 'agent_outcome' containing the agent's outcome
    """
    from src.reac import get_agent_runnable
    
    try:
        # Get the agent runnable
        agent_runnable = get_agent_runnable()
        
        if agent_runnable is None:
            return {'agent_outcome': AgentFinish(return_values={"output": "Error: No se pudo inicializar el agente"}, log="")}
        
        # Agent invoke
        agent_outcome = agent_runnable.invoke(state)
        return {'agent_outcome': agent_outcome}
    except Exception as e:
        print(f"Error en el razonamiento del agente: {str(e)}")
        return {'agent_outcome': AgentFinish(return_values={"output": f"Error: {str(e)}"}, log="")}
    
def get_tool_executor():
    """
    Gets the tool executor.
    Returns:
    ToolExecutor: The tool executor
    """
    from src.reac import get_tools #Prevents circular reference 
    
    tools = get_tools()  
    return ToolNode(tools)

def cached_tool_executor():
    """
    Gets a cached instance of the tool executor.
    Returns:
    ToolExecutor: The cached instance of the tool executor.
    """
    global _tool_executor
    
    if _tool_executor is None:
        _tool_executor = get_tool_executor()
    
    return _tool_executor

def execute_tools(state):
    """
    Executes tools based on the agent's action.
    Args:
    state (dict): The current state with the agent's action
    Returns:
    dict: A dictionary containing the intermediate steps of the execution
    """
    
    tool_executor = cached_tool_executor()          # Get the tool executor    
    
    agent_outcome = state["agent_outcome"]          # Get the nex agent outcome    
    
    if not isinstance(agent_outcome, AgentAction):
        return {"intermediate_steps": []}
    
    try:                                            # Execute the tool          
        output = tool_executor.invoke(agent_outcome)
        return {"intermediate_steps": [(agent_outcome, str(output))]}
    except Exception as e:
        print(f"Error exevuting the tool: {str(e)}")
        return {"intermediate_steps": [(agent_outcome, f"Error: {str(e)}")]}