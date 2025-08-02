import os
import logging
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI

from agents.router import router_agent
from agents.specialized import billing_agent, technical_agent, general_agent
from agents.supervisor import supervisor_agent

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check if we're in development mode
APP_ENV = os.getenv("APP_ENV", "development")

# Initialize OpenAI model (GPT-4 mini)
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.7,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

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

def interactive_chatbot():
    """Interactive chatbot with user identification workflow"""
    print("🤖 Multi-Agent Customer Support Chatbot")
    print("Type 'q' or 'exit' to quit the chat.")
    print("Type 'reset' to start a new conversation.")
    print("=" * 50)
    
    # Import here to avoid circular imports
    from agents.specialized import billing_agent_instance, technical_agent_instance, general_agent_instance
    from utils.data_loader import customer_data_loader
    
    print(f"\n📈 Total Customers in System: {customer_data_loader.get_total_customers()}")
    print("\n💬 Hello! I'm your customer support assistant. Please tell me how I can help you today.")
    print("💡 Tip: Include your account ID (e.g., USER123456) or email for faster service.")
    
    session_count = 0
    
    while True:
        try:
            # Get user input
            user_input = input("\n👤 You: ").strip()
            
            # Check for quit commands
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("\n🤖 Assistant: Thank you for using our support system. Have a great day!")
                break
            
            # Check for reset command
            if user_input.lower() == 'reset':
                billing_agent_instance.reset_customer_context()
                technical_agent_instance.reset_customer_context()
                general_agent_instance.reset_customer_context()
                
                print(f"\n🔄 Conversation reset. How can I help you today?")
                print("💡 Tip: Include your account ID (e.g., USER123456) or email for faster service.")
                session_count = 0
                continue
            
            if not user_input:
                print("Please enter a message, 'reset' to start over, or 'q' to quit.")
                continue
            
            session_count += 1
            print(f"\n🔄 Processing your request... (Session #{session_count})")
            
            # Process the query through the multi-agent system
            response = run_customer_support_system(user_input)
            
            print(f"\n🤖 Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🤖 Assistant: Chat interrupted. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Error in chatbot: {e}")
            print("\n🤖 Assistant: I apologize, but I encountered an error. Please try again.")

if __name__ == "__main__":
    interactive_chatbot()