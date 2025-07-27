import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage

from agents.router import RouterAgent, router_agent


class TestRouterAgent:
    """Test cases for the RouterAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.router = RouterAgent()
    
    def test_router_agent_initialization(self):
        """Test RouterAgent initializes correctly"""
        assert self.router.classification_prompt is not None
        assert "BILLING" in self.router.classification_prompt
        assert "TECHNICAL" in self.router.classification_prompt
        assert "GENERAL" in self.router.classification_prompt
    
    def test_classify_billing_queries(self):
        """Test classification of billing-related queries"""
        billing_queries = [
            "I have a billing issue",
            "Need help with my payment",
            "Refund request for my order",
            "Invoice question about charges",
            "Payment method not working"
        ]
        
        for query in billing_queries:
            result = self.router.classify_query(query)
            assert result == "billing_agent", f"Query '{query}' should be classified as billing"
    
    def test_classify_technical_queries(self):
        """Test classification of technical-related queries"""
        technical_queries = [
            "System is not working",
            "Found a bug in the application",
            "Technical error occurred",
            "Feature request for new functionality",
            "Application is broken"
        ]
        
        for query in technical_queries:
            result = self.router.classify_query(query)
            assert result == "technical_agent", f"Query '{query}' should be classified as technical"
    
    def test_classify_general_queries(self):
        """Test classification of general queries"""
        general_queries = [
            "What are your company hours?",
            "How do I contact support?",
            "General information about services",
            "Account settings question",
            "Random inquiry"
        ]
        
        for query in general_queries:
            result = self.router.classify_query(query)
            assert result == "general_agent", f"Query '{query}' should be classified as general"
    
    def test_classify_query_empty_string(self):
        """Test classification with empty string"""
        result = self.router.classify_query("")
        assert result == "general_agent"
    
    def test_classify_query_mixed_keywords(self):
        """Test classification with mixed keywords (should prioritize billing over technical)"""
        query = "billing system is not working"
        result = self.router.classify_query(query)
        assert result == "billing_agent"
    
    @patch('agents.router.logger')
    def test_classify_query_exception_handling(self, mock_logger):
        """Test error handling in classify_query"""
        # Mock an exception during classification
        with patch.object(self.router, 'classify_query', side_effect=Exception("Test error")):
            router = RouterAgent()
            # Create a new instance to avoid the mocked method
            with patch('builtins.any', side_effect=Exception("Test error")):
                result = router.classify_query("test query")
                assert result == "general_agent"


class TestRouterAgentFunction:
    """Test cases for the router_agent function"""
    
    def test_router_agent_with_billing_query(self, billing_query_state):
        """Test router_agent function with billing query"""
        result = router_agent(billing_query_state)
        
        assert result["next_agent"] == "billing_agent"
        assert result["query_type"] == "BILLING"
        assert "messages" in result
    
    def test_router_agent_with_technical_query(self, technical_query_state):
        """Test router_agent function with technical query"""
        result = router_agent(technical_query_state)
        
        assert result["next_agent"] == "technical_agent"
        assert result["query_type"] == "TECHNICAL"
        assert "messages" in result
    
    def test_router_agent_with_general_query(self, general_query_state):
        """Test router_agent function with general query"""
        result = router_agent(general_query_state)
        
        assert result["next_agent"] == "general_agent"
        assert result["query_type"] == "GENERAL"
        assert "messages" in result
    
    def test_router_agent_empty_messages(self):
        """Test router_agent function with empty messages"""
        state = {
            "messages": [],
            "next_agent": "",
            "query_type": "",
            "final_response": ""
        }
        
        result = router_agent(state)
        
        # Should not modify state if no messages
        assert result["next_agent"] == ""
        assert result["query_type"] == ""
    
    @patch('agents.router.logger')
    def test_router_agent_logging(self, mock_logger, billing_query_state):
        """Test that router_agent logs classification results"""
        router_agent(billing_query_state)
        
        # Verify that logger.info was called
        mock_logger.info.assert_called()
        call_args = mock_logger.info.call_args[0][0]
        assert "Classified query as:" in call_args
        assert "routing to:" in call_args
    
    def test_agent_to_type_mapping(self):
        """Test the agent to query type mapping is correct"""
        from agents.router import router_agent
        
        test_cases = [
            ("billing_agent", "BILLING"),
            ("technical_agent", "TECHNICAL"), 
            ("general_agent", "GENERAL")
        ]
        
        for agent_name, expected_type in test_cases:
            # Create a mock state that would result in the specific agent
            state = {
                "messages": [HumanMessage(content="test")],
                "next_agent": "",
                "query_type": "",
                "final_response": ""
            }
            
            # Mock the classify_query to return the specific agent
            with patch('agents.router.RouterAgent.classify_query', return_value=agent_name):
                result = router_agent(state)
                assert result["query_type"] == expected_type