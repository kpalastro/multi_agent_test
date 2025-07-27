import logging
from typing import Dict, Any, List
from langchain_core.messages import BaseMessage, AIMessage

logger = logging.getLogger(__name__)

class BaseSpecializedAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.memory: List[Dict[str, Any]] = []
    
    def add_to_memory(self, query: str, response: str):
        self.memory.append({
            "query": query,
            "response": response,
            "timestamp": "now"  # In real implementation, use datetime
        })
    
    def get_relevant_memory(self, query: str) -> str:
        # Simple memory retrieval - in practice, use embeddings/similarity
        if self.memory:
            return f"Previous interactions: {len(self.memory)} records"
        return "No previous interactions"

class BillingAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__("billing")
        self.response_template = """
        I'm your billing specialist. I can help you with:
        - Payment issues and billing inquiries
        - Invoice questions and billing cycles
        - Refund requests and charge disputes
        - Account balance and payment methods
        
        For your query: "{query}"
        
        Based on our records and policies, here's my response:
        {response_content}
        
        If you need further assistance with billing matters, please don't hesitate to ask.
        """
    
    def generate_response(self, query: str) -> str:
        memory_context = self.get_relevant_memory(query)
        
        # Simple response generation based on keywords
        query_lower = query.lower()
        
        if "refund" in query_lower:
            response_content = "I can help you process a refund. Please provide your order number and reason for the refund request."
        elif "invoice" in query_lower : #or "bill" in query_lower:
            response_content = "I can assist with invoice-related questions. Your latest invoice details can be found in your account dashboard."
        elif "payment" in query_lower:
            response_content = "For payment issues, please verify your payment method is up to date and has sufficient funds."
        else:
            response_content = "I'm here to help with any billing-related concerns you may have."
        
        response = self.response_template.format(
            query=query,
            response_content=response_content
        )
        
        self.add_to_memory(query, response)
        return response

class TechnicalAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__("technical")
        self.response_template = """
        I'm your technical support specialist. I can assist with:
        - System bugs and error troubleshooting
        - Feature requests and functionality questions
        - Performance issues and optimizations
        - Integration and API support
        
        For your technical query: "{query}"
        
        Technical analysis and solution:
        {response_content}
        
        If this doesn't resolve your issue, please provide more details about your setup and error messages.
        """
    
    def generate_response(self, query: str) -> str:
        memory_context = self.get_relevant_memory(query)
        
        query_lower = query.lower()
        
        if "bug" in query_lower or "error" in query_lower:
            response_content = "I can help troubleshoot this issue. Please provide error messages, steps to reproduce, and your system configuration."
        elif "feature" in query_lower:
            response_content = "Thank you for your feature suggestion. I'll document this request and forward it to our development team."
        elif "not working" in query_lower or "broken" in query_lower:
            response_content = "Let's diagnose this issue. Please try clearing your cache, updating your browser, and check if the problem persists."
        else:
            response_content = "I'm here to help resolve any technical issues you're experiencing."
        
        response = self.response_template.format(
            query=query,
            response_content=response_content
        )
        
        self.add_to_memory(query, response)
        return response

class GeneralAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__("general")
        self.response_template = """
        Hello! I'm here to help with general inquiries. I can assist with:
        - Account information and settings
        - Company policies and procedures  
        - General product information
        - Directing you to the right specialist
        
        Regarding your inquiry: "{query}"
        
        Here's the information I can provide:
        {response_content}
        
        Is there anything else I can help you with today?
        """
    
    def generate_response(self, query: str) -> str:
        memory_context = self.get_relevant_memory(query)
        
        query_lower = query.lower()
        
        if "account" in query_lower:
            response_content = "For account-related questions, you can manage your settings in the user dashboard or contact our support team."
        elif "company" in query_lower or "about" in query_lower:
            response_content = "Our company is committed to providing excellent service. You can find more information on our website's About page."
        elif "help" in query_lower:
            response_content = "I'm here to help! Please let me know what specific information you're looking for."
        else:
            response_content = "Thank you for contacting us. I'm here to assist with any general questions you may have."
        
        response = self.response_template.format(
            query=query,
            response_content=response_content
        )
        
        self.add_to_memory(query, response)
        return response

# Agent instances
billing_agent_instance = BillingAgent()
technical_agent_instance = TechnicalAgent()
general_agent_instance = GeneralAgent()

def billing_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if state["messages"]:
            query = state["messages"][-1].content
            response = billing_agent_instance.generate_response(query)
            
            state["messages"].append(AIMessage(content=response))
            logger.info(f"Billing agent processed query: {query[:50]}...")
            
    except Exception as e:
        logger.error(f"Error in billing agent: {e}")
        state["messages"].append(AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later."))
    
    return state

def technical_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if state["messages"]:
            query = state["messages"][-1].content
            response = technical_agent_instance.generate_response(query)
            
            state["messages"].append(AIMessage(content=response))
            logger.info(f"Technical agent processed query: {query[:50]}...")
            
    except Exception as e:
        logger.error(f"Error in technical agent: {e}")
        state["messages"].append(AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later."))
    
    return state

def general_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if state["messages"]:
            query = state["messages"][-1].content
            response = general_agent_instance.generate_response(query)
            
            state["messages"].append(AIMessage(content=response))
            logger.info(f"General agent processed query: {query[:50]}...")
            
    except Exception as e:
        logger.error(f"Error in general agent: {e}")
        state["messages"].append(AIMessage(content="I apologize, but I'm experiencing technical difficulties. Please try again later."))
    
    return state