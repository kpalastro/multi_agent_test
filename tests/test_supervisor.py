import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from agents.supervisor import SupervisorAgent, supervisor_agent, supervisor_instance


class TestSupervisorAgent:
    """Test cases for the SupervisorAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.supervisor = SupervisorAgent()
    
    def test_initialization(self):
        """Test SupervisorAgent initializes correctly"""
        assert self.supervisor.qa_criteria is not None
        assert "completeness" in self.supervisor.qa_criteria
        assert "accuracy" in self.supervisor.qa_criteria
        assert "tone" in self.supervisor.qa_criteria
        assert "clarity" in self.supervisor.qa_criteria
        assert self.supervisor.improvement_prompt is not None
    
    def test_evaluate_response_good_response(self):
        """Test evaluation of a good response"""
        query = "I have a billing issue with my account"
        response = "I understand your billing concern and I'm here to help. I can assist you with payment issues, invoice questions, and account balance inquiries. Please provide more details about your specific billing issue so I can give you the most accurate assistance."
        query_type = "BILLING"
        
        evaluation = self.supervisor.evaluate_response(query, response, query_type)
        
        assert isinstance(evaluation["needs_improvement"], bool)
        assert isinstance(evaluation["issues"], list)
        assert isinstance(evaluation["score"], int)
        assert evaluation["score"] >= 0
        assert evaluation["score"] <= 100
    
    def test_evaluate_response_brief_response(self):
        """Test evaluation of a brief response that needs improvement"""
        query = "I have a billing issue"
        response = "OK"
        query_type = "BILLING"
        
        evaluation = self.supervisor.evaluate_response(query, response, query_type)
        
        assert evaluation["needs_improvement"] is True
        assert "Response too brief" in evaluation["issues"]
        assert evaluation["score"] < 100
    
    def test_evaluate_response_missing_keywords(self):
        """Test evaluation when response doesn't address query keywords"""
        query = "billing refund payment invoice"
        response = "Thank you for contacting us. We appreciate your business."
        query_type = "BILLING"
        
        evaluation = self.supervisor.evaluate_response(query, response, query_type)
        
        assert evaluation["needs_improvement"] is True
        assert "May not fully address query" in evaluation["issues"]
    
    def test_evaluate_response_tone_issues(self):
        """Test evaluation of tone issues"""
        query = "I have a problem with my billing"
        response = "Here's your billing information. Check your account dashboard."
        query_type = "BILLING"
        
        evaluation = self.supervisor.evaluate_response(query, response, query_type)
        
        # Should flag tone issue for billing problems without empathy
        assert evaluation["needs_improvement"] is True
        assert "May need more empathetic tone" in evaluation["issues"]
    
    def test_improve_response_brief_issue(self):
        """Test improvement of brief responses"""
        query = "Help with billing"
        response = "Check your account."
        query_type = "BILLING"
        issues = ["Response too brief"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        assert len(improved) > len(response)
        assert "additional assistance" in improved.lower()
    
    def test_improve_response_missing_query_address(self):
        """Test improvement when query isn't fully addressed"""
        query = "Billing question"
        response = "Thank you for contacting us."
        query_type = "BILLING"
        issues = ["May not fully address query"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        assert "doesn't fully address" in improved.lower()
        assert "clarification" in improved.lower()
    
    def test_improve_response_tone_billing(self):
        """Test improvement of tone for billing issues"""
        query = "Billing problem"
        response = "Here's the information."
        query_type = "BILLING"
        issues = ["May need more empathetic tone"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        assert "understand" in improved.lower() and "frustrating" in improved.lower()
    
    def test_improve_response_tone_technical(self):
        """Test improvement of tone for technical issues"""
        query = "System error"
        response = "Fix it yourself."
        query_type = "TECHNICAL"
        issues = ["May need more empathetic tone"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        assert "apologize" in improved.lower() and "difficulties" in improved.lower()
    
    def test_improve_response_tone_general(self):
        """Test improvement of tone for general issues"""
        query = "General question"
        response = "Here's the answer."
        query_type = "GENERAL"
        issues = ["May need more empathetic tone"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        assert "appreciate" in improved.lower() and "reaching out" in improved.lower()
    
    def test_improve_response_multiple_issues(self):
        """Test improvement with multiple issues"""
        query = "Billing problem"
        response = "OK"
        query_type = "BILLING"
        issues = ["Response too brief", "May need more empathetic tone"]
        
        improved = self.supervisor.improve_response(query, response, query_type, issues)
        
        # Should address both issues
        assert "understand" in improved.lower()
        assert "additional assistance" in improved.lower()
    
    @patch('agents.supervisor.logger')
    def test_improve_response_exception_handling(self, mock_logger):
        """Test error handling in improve_response"""
        query = "Test query"
        response = "Test response"
        query_type = "BILLING"
        issues = ["Test issue"]
        
        # Mock an exception
        with patch.object(self.supervisor, 'improve_response', side_effect=Exception("Test error")):
            supervisor = SupervisorAgent()
            result = supervisor.improve_response(query, response, query_type, issues)
            # Should return original response on error
            assert result == response


class TestSupervisorAgentFunction:
    """Test cases for the supervisor_agent function"""
    
    def test_supervisor_agent_no_improvement_needed(self):
        """Test supervisor_agent when response is already good"""
        state = {
            "messages": [
                HumanMessage(content="What are your company hours?"),
                AIMessage(content="Our company hours are Monday through Friday, 9 AM to 5 PM EST. We're here to assist you with any questions during these hours. If you need help outside of business hours, please feel free to leave a message and we'll get back to you as soon as possible.")
            ],
            "next_agent": "general_agent",
            "query_type": "GENERAL",
            "final_response": ""
        }
        
        result = supervisor_agent(state)
        
        assert "final_response" in result
        assert result["final_response"] != ""
        assert len(result["messages"]) == 2  # Should not add new messages
    
    def test_supervisor_agent_improvement_needed(self):
        """Test supervisor_agent when response needs improvement"""
        state = {
            "messages": [
                HumanMessage(content="I have a billing problem with my account"),
                AIMessage(content="OK")
            ],
            "next_agent": "billing_agent",
            "query_type": "BILLING",
            "final_response": ""
        }
        
        result = supervisor_agent(state)
        
        assert "final_response" in result
        assert result["final_response"] != "OK"
        assert len(result["final_response"]) > 10  # Should be improved
        # Last message should be updated
        assert result["messages"][-1].content != "OK"
    
    def test_supervisor_agent_insufficient_messages(self):
        """Test supervisor_agent with insufficient messages"""
        state = {
            "messages": [HumanMessage(content="Test query")],
            "next_agent": "general_agent",
            "query_type": "GENERAL",
            "final_response": ""
        }
        
        result = supervisor_agent(state)
        
        # Should handle gracefully
        assert "final_response" in result
    
    def test_supervisor_agent_empty_messages(self):
        """Test supervisor_agent with empty messages"""
        state = {
            "messages": [],
            "next_agent": "general_agent",
            "query_type": "GENERAL",
            "final_response": ""
        }
        
        result = supervisor_agent(state)
        
        # Should handle gracefully
        assert "final_response" in result
    
    def test_supervisor_agent_missing_query_type(self):
        """Test supervisor_agent with missing query_type"""
        state = {
            "messages": [
                HumanMessage(content="Test query"),
                AIMessage(content="Test response")
            ],
            "next_agent": "general_agent",
            "final_response": ""
        }
        
        result = supervisor_agent(state)
        
        # Should default to GENERAL and process normally
        assert "final_response" in result
    
    @patch('agents.supervisor.logger')
    def test_supervisor_agent_logging_improvement(self, mock_logger):
        """Test that supervisor_agent logs when improving responses"""
        state = {
            "messages": [
                HumanMessage(content="I have a billing problem"),
                AIMessage(content="OK")  # Brief response that needs improvement
            ],
            "next_agent": "billing_agent",
            "query_type": "BILLING",
            "final_response": ""
        }
        
        supervisor_agent(state)
        
        # Should log improvement
        mock_logger.info.assert_called()
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("improved the response" in call for call in log_calls)
    
    @patch('agents.supervisor.logger')
    def test_supervisor_agent_logging_approval(self, mock_logger):
        """Test that supervisor_agent logs when approving responses"""
        state = {
            "messages": [
                HumanMessage(content="What are your hours?"),
                AIMessage(content="Our company hours are Monday through Friday, 9 AM to 5 PM EST. We're here to assist you with any questions during these hours and appreciate your business.")
            ],
            "next_agent": "general_agent",
            "query_type": "GENERAL",
            "final_response": ""
        }
        
        supervisor_agent(state)
        
        # Should log approval
        mock_logger.info.assert_called()
        log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
        assert any("approved the response" in call for call in log_calls)
    
    @patch('agents.supervisor.logger')
    def test_supervisor_agent_exception_handling(self, mock_logger):
        """Test supervisor_agent error handling"""
        state = {
            "messages": [
                HumanMessage(content="Test query"),
                AIMessage(content="Test response")
            ],
            "next_agent": "general_agent",
            "query_type": "GENERAL",
            "final_response": ""
        }
        
        # Mock an exception in evaluation
        with patch.object(supervisor_instance, 'evaluate_response', side_effect=Exception("Test error")):
            result = supervisor_agent(state)
            
            # Should handle error gracefully and use fallback
            assert result["final_response"] == "Test response"
            mock_logger.error.assert_called()


class TestSupervisorInstance:
    """Test cases for the global supervisor instance"""
    
    def test_supervisor_instance_exists(self):
        """Test that global supervisor instance exists"""
        assert isinstance(supervisor_instance, SupervisorAgent)
    
    def test_supervisor_instance_functionality(self):
        """Test that supervisor instance works correctly"""
        query = "Test query"
        response = "Test response with sufficient length to pass basic checks"
        query_type = "GENERAL"
        
        evaluation = supervisor_instance.evaluate_response(query, response, query_type)
        
        assert isinstance(evaluation, dict)
        assert "needs_improvement" in evaluation
        assert "issues" in evaluation
        assert "score" in evaluation