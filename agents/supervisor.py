import logging
from typing import Dict, Any
from langchain_core.messages import AIMessage

logger = logging.getLogger(__name__)

class SupervisorAgent:
    def __init__(self):
        self.qa_criteria = {
            "completeness": "Does the response fully address the user's query?",
            "accuracy": "Is the information provided accurate and helpful?", 
            "tone": "Is the tone professional and appropriate?",
            "clarity": "Is the response clear and easy to understand?"
        }
        
        self.improvement_prompt = """
        You are a quality assurance supervisor for customer support responses.
        
        Original Query: {query}
        Agent Response: {response}
        Query Type: {query_type}
        
        Evaluate this response based on:
        1. Completeness - Does it fully address the query?
        2. Accuracy - Is the information correct and helpful?
        3. Tone - Is it professional and appropriate?
        4. Clarity - Is it clear and easy to understand?
        
        If the response needs improvement, provide an edited version.
        If the response is satisfactory, return it as-is.
        
        Improved Response:
        """
    
    def evaluate_response(self, query: str, response: str, query_type: str) -> Dict[str, Any]:
        evaluation = {
            "needs_improvement": False,
            "issues": [],
            "score": 0
        }
        
        # Basic evaluation logic
        response_lower = response.lower()
        query_lower = query.lower()
        
        # Check completeness
        if len(response) < 50:
            evaluation["needs_improvement"] = True
            evaluation["issues"].append("Response too brief")
        
        # Check if key query terms are addressed
        query_keywords = query_lower.split()
        addressed_keywords = sum(1 for keyword in query_keywords if keyword in response_lower)
        if addressed_keywords < len(query_keywords) * 0.3:
            evaluation["needs_improvement"] = True
            evaluation["issues"].append("May not fully address query")
        
        # Check tone (look for appropriate language)
        if "sorry" not in response_lower and "apologize" not in response_lower and "unfortunately" not in response_lower:
            if query_type == "BILLING" or "problem" in query_lower or "issue" in query_lower:
                evaluation["needs_improvement"] = True
                evaluation["issues"].append("May need more empathetic tone")
        
        # Calculate score
        evaluation["score"] = max(0, 100 - len(evaluation["issues"]) * 20)
        
        return evaluation
    
    def improve_response(self, query: str, response: str, query_type: str, issues: list) -> str:
        try:
            # Simple improvement logic based on identified issues
            improved_response = response
            
            if "Response too brief" in issues:
                improved_response += "\n\nI'm here to provide additional assistance if you need more detailed information."
            
            if "May not fully address query" in issues:
                improved_response = f"Thank you for your inquiry. {improved_response}\n\nPlease let me know if this doesn't fully address your question or if you need clarification on any point."
            
            if "May need more empathetic tone" in issues:
                if query_type == "BILLING":
                    improved_response = f"I understand billing concerns can be frustrating. {improved_response}"
                elif query_type == "TECHNICAL":
                    improved_response = f"I apologize for any technical difficulties you're experiencing. {improved_response}"
                else:
                    improved_response = f"I appreciate you reaching out to us. {improved_response}"
            
            return improved_response
            
        except Exception as e:
            logger.error(f"Error improving response: {e}")
            return response

supervisor_instance = SupervisorAgent()

def supervisor_agent(state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        if state["messages"] and len(state["messages"]) >= 2:
            original_query = state["messages"][0].content
            agent_response = state["messages"][-1].content
            query_type = state.get("query_type", "GENERAL")
            
            # Evaluate the response
            evaluation = supervisor_instance.evaluate_response(
                original_query, agent_response, query_type
            )
            
            logger.info(f"Supervisor evaluation - Score: {evaluation['score']}, Issues: {evaluation['issues']}")
            
            # Improve response if needed
            if evaluation["needs_improvement"]:
                improved_response = supervisor_instance.improve_response(
                    original_query, agent_response, query_type, evaluation["issues"]
                )
                
                # Replace the last message with improved version
                state["messages"][-1] = AIMessage(content=improved_response)
                state["final_response"] = improved_response
                
                logger.info("Supervisor improved the response")
            else:
                state["final_response"] = agent_response
                logger.info("Supervisor approved the response as-is")
                
    except Exception as e:
        logger.error(f"Error in supervisor agent: {e}")
        # Fallback - use the last response as-is
        if state["messages"]:
            state["final_response"] = state["messages"][-1].content
    
    return state