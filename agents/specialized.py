import logging
import os
from typing import Dict, Any, List, Optional
from langchain_core.messages import BaseMessage, AIMessage
from langchain_openai import ChatOpenAI
from utils.data_loader import customer_data_loader
from utils.user_identifier import user_identifier
from dotenv import load_dotenv

# Load environment variables at module import time
load_dotenv()

logger = logging.getLogger(__name__)

class BaseSpecializedAgent:
    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.memory: List[Dict[str, Any]] = []
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.7,
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        self.data_loader = customer_data_loader
        self.user_identifier = user_identifier
        self.current_customer = None
        self.identification_attempts = 0
        
    def identify_user_from_query(self, query: str) -> bool:
        """Try to identify user from query, return True if successful"""
        if not self.current_customer:
            identified_customer = self.user_identifier.extract_user_info_from_query(query)
            if identified_customer:
                self.current_customer = identified_customer
                logger.info(f"User identified: {self.current_customer.get('name')} ({self.current_customer.get('id')})")
                return True
        return self.current_customer is not None
        
    def get_customer_context(self) -> Optional[Dict[str, Any]]:
        """Get current customer context (None if not identified)"""
        return self.current_customer
        
    def reset_customer_context(self) -> None:
        """Reset customer context for new conversation"""
        self.current_customer = None
        self.identification_attempts = 0
        
    def request_user_identification(self, query: str) -> str:
        """Generate a response asking for user identification"""
        self.identification_attempts += 1
        
        # Check if query seems to be an identification attempt
        if self.user_identifier.is_identification_attempt(query):
            return "I couldn't find your account with the information provided. Please provide your account ID (e.g., USER123456) or email address so I can assist you better."
        
        # Different messages based on number of attempts
        if self.identification_attempts == 1:
            return "Hello! To provide you with personalized assistance, I'll need to identify your account first. Please provide your account ID (e.g., USER123456) or email address."
        elif self.identification_attempts == 2:
            return "I still need your account information to help you. You can provide:\n• Your account ID (format: USER123456)\n• Your email address\n• Or say something like 'My account is USER123456'"
        else:
            return "I'm having trouble identifying your account. Please double-check and provide your account ID or email address, or contact our support team for assistance."
        
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        return self.data_loader.get_system_status()
    
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
    
    def generate_response(self, query: str) -> str:
        # First try to identify the user if not already identified
        if not self.identify_user_from_query(query):
            return self.request_user_identification(query)
            
        memory_context = self.get_relevant_memory(query)
        customer_data = self.get_customer_context()
        billing_data = customer_data.get('billing_info', {})
        
        # Use OpenAI for more natural responses
        prompt = f"""
        You are a billing specialist for a customer support team. Use this context to provide helpful responses:
        
        Customer Info:
        - Account ID: {customer_data.get('id', 'N/A')}
        - Name: {customer_data.get('name', 'N/A')}
        - Email: {customer_data.get('email', 'N/A')}
        - Subscription: {customer_data.get('subscription', 'N/A')}
        - Join Date: {customer_data.get('join_date', 'N/A')}
        - Current Balance: ${billing_data.get('current_balance', 0)}
        - Last Payment: {billing_data.get('last_payment', 'N/A')}
        - Payment Method: {billing_data.get('payment_method', 'N/A')}
        - Next Billing: {billing_data.get('next_billing', 'N/A')}
        - Total Spent: ${billing_data.get('total_spent', 0)}
        - Payment Status: {billing_data.get('payment_status', 'N/A')}
        
        Customer Query: {query}
        
        Provide a helpful, professional response addressing their billing concern. Keep it concise but informative.
        If there are payment issues (overdue/failed), acknowledge them appropriately.
        """
        
        try:
            response = self.llm.invoke(prompt).content
            self.add_to_memory(query, response)
            return response
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            # Fallback to simple response
            return "I can help you with billing matters. Please let me know your specific concern and I'll assist you accordingly."

class TechnicalAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__("technical")
    
    def generate_response(self, query: str) -> str:
        # First try to identify the user if not already identified
        if not self.identify_user_from_query(query):
            return self.request_user_identification(query)
            
        memory_context = self.get_relevant_memory(query)
        customer_data = self.get_customer_context()
        tech_profile = customer_data.get('technical_profile', {})
        system_status = self.get_system_status()
        
        # Use OpenAI for more natural responses
        prompt = f"""
        You are a technical support specialist. Use this context to provide helpful responses:
        
        Customer Info:
        - Account ID: {customer_data.get('id', 'N/A')}
        - Name: {customer_data.get('name', 'N/A')}
        - Platform: {tech_profile.get('platform', 'N/A')}
        - Browser: {tech_profile.get('browser', 'N/A')}
        - Last Login: {customer_data.get('last_login', 'N/A')}
        - Previous Issues: {tech_profile.get('last_issue', 'None')}
        - Support Tickets: {tech_profile.get('support_tickets', 0)}
        
        System Status:
        - Overall Status: {system_status.get('overall_status', 'operational')}
        - Last Maintenance: {system_status.get('last_maintenance', 'N/A')}
        - Known Issues: {', '.join(system_status.get('known_issues', []))}
        - Recent Updates: {', '.join(system_status.get('recent_updates', []))}
        
        Customer Query: {query}
        
        Provide a helpful technical response. Include troubleshooting steps if relevant.
        If there are known system issues that might be related, mention them.
        """
        
        try:
            response = self.llm.invoke(prompt).content
            self.add_to_memory(query, response)
            return response
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            # Fallback to simple response
            return "I'm here to help with technical issues. Please describe the problem and I'll do my best to assist you."

class GeneralAgent(BaseSpecializedAgent):
    def __init__(self):
        super().__init__("general")
    
    def generate_response(self, query: str) -> str:
        # First try to identify the user if not already identified
        if not self.identify_user_from_query(query):
            return self.request_user_identification(query)
            
        memory_context = self.get_relevant_memory(query)
        customer_data = self.get_customer_context()
        billing_data = customer_data.get('billing_info', {})
        tech_profile = customer_data.get('technical_profile', {})
        
        # Use OpenAI for more natural responses
        prompt = f"""
        You are a general customer support representative. Use this context to provide helpful responses:
        
        Customer Info:
        - Account ID: {customer_data.get('id', 'N/A')}
        - Name: {customer_data.get('name', 'N/A')}
        - Email: {customer_data.get('email', 'N/A')}
        - Subscription: {customer_data.get('subscription', 'N/A')}
        - Join Date: {customer_data.get('join_date', 'N/A')}
        - Last Login: {customer_data.get('last_login', 'N/A')}
        - Payment Status: {billing_data.get('payment_status', 'N/A')}
        - Support History: {tech_profile.get('support_tickets', 0)} previous tickets
        
        Customer Query: {query}
        
        Provide a helpful, friendly response. If the query might be better handled by billing or technical support, mention that option.
        Reference their account information when relevant to personalize the response.
        """
        
        try:
            response = self.llm.invoke(prompt).content
            self.add_to_memory(query, response)
            return response
        except Exception as e:
            logger.error(f"Error generating OpenAI response: {e}")
            # Fallback to simple response
            return "Thank you for contacting us! I'm here to help with any questions you may have."

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