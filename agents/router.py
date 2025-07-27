import logging
from langchain_core.messages import BaseMessage
from typing import Dict, Any

logger = logging.getLogger(__name__)

class RouterAgent:
    def __init__(self):
        self.classification_prompt = """
        You are a customer support query classifier. Analyze the user's message and classify it into one of these categories:
        
        1. BILLING - Issues related to payments, invoices, charges, refunds, billing cycles
        2. TECHNICAL - Technical problems, bugs, feature requests, system issues
        3. GENERAL - General inquiries, account information, company information
        
        Respond with only the category name: BILLING, TECHNICAL, or GENERAL
        
        User message: {message}
        
        Classification:
        """
    
    def classify_query(self, message: str) -> str:
        try:
            # Simple keyword-based classification for demo
            message_lower = message.lower()
            
            billing_keywords = ['billing', 'payment', 'charge', 'invoice', 'refund', 'money', 'cost', 'price']
            technical_keywords = ['bug', 'error', 'technical', 'feature', 'system', 'not working', 'broken']
            
            if any(keyword in message_lower for keyword in billing_keywords):
                return "billing_agent"
            elif any(keyword in message_lower for keyword in technical_keywords):
                return "technical_agent"
            else:
                return "general_agent"
                
        except Exception as e:
            logger.error(f"Error in query classification: {e}")
            return "general_agent"

def router_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    router = RouterAgent()
    
    if state["messages"]:
        latest_message = state["messages"][-1].content
        next_agent = router.classify_query(latest_message)
        
        # Map to query type for tracking
        agent_to_type = {
            "billing_agent": "BILLING",
            "technical_agent": "TECHNICAL", 
            "general_agent": "GENERAL"
        }
        
        state["next_agent"] = next_agent
        state["query_type"] = agent_to_type[next_agent]
        
        logger.info(f"Classified query as: {state['query_type']}, routing to: {next_agent}")
    
    return state