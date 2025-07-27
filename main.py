import os
import logging
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

from agents.router import router_agent
from agents.specialized import billing_agent, technical_agent, general_agent
from agents.supervisor import supervisor_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're in development mode
APP_ENV = os.getenv("APP_ENV", "development")

class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], "The messages in the conversation"]
    next_agent: str
    query_type: str
    final_response: str

def create_multi_agent_system():
    workflow = StateGraph(AgentState)
    
    # Add nodes
    workflow.add_node("input", input_node)
    workflow.add_node("router", router_agent)
    workflow.add_node("billing_agent", billing_agent)
    workflow.add_node("technical_agent", technical_agent)
    workflow.add_node("general_agent", general_agent)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("output", output_node)
    
    # Add edges
    workflow.set_entry_point("input")
    workflow.add_edge("input", "router")
    workflow.add_conditional_edges(
        "router",
        lambda x: x["next_agent"],
        {
            "billing_agent": "billing_agent",
            "technical_agent": "technical_agent", 
            "general_agent": "general_agent"
        }
    )
    workflow.add_edge("billing_agent", "supervisor")
    workflow.add_edge("technical_agent", "supervisor")
    workflow.add_edge("general_agent", "supervisor")
    workflow.add_edge("supervisor", "output")
    workflow.add_edge("output", END)
    
    app = workflow.compile()
    
    # Generate graph visualization in development mode
    if APP_ENV == "development":
        try:
            # Generate the graph visualization
            graph_image = app.get_graph().draw_mermaid_png()
            
            # Save to graph.png
            with open("graph.png", "wb") as f:
                f.write(graph_image)
            
            logger.info("Graph visualization saved to graph.png")
            
        except Exception as e:
            logger.warning(f"Could not generate graph visualization: {e}")
            logger.info("To enable graph visualization, install: pip install pygraphviz")
    
    return app

def input_node(state: AgentState):
    logger.info("Processing input")
    return state

def output_node(state: AgentState):
    logger.info("Generating final output")
    return state

def run_customer_support_system(user_query: str):
    app = create_multi_agent_system()
    
    initial_state = {
        "messages": [HumanMessage(content=user_query)],
        "next_agent": "",
        "query_type": "",
        "final_response": ""
    }
    
    try:
        result = app.invoke(initial_state)
        return result['final_response']
    except Exception as e:
        logger.error(f"Error in customer support system: {e}")
        return "I apologize, but I'm experiencing technical difficulties. Please try again later."

if __name__ == "__main__":
    # Example usage
    test_queries = [
        "I have a billing issue with my account",
        "The system is not working properly", 
        "What are your company hours?"
    ]
    
    print("=== Multi-Agent Customer Support System Demo ===\n")
    
    for query in test_queries:
        print(f"User Query: {query}")
        print("-" * 50)
        response = run_customer_support_system(query)
        print(f"System Response: {response}")
        print("=" * 80 + "\n")