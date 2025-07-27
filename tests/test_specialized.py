import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import HumanMessage, AIMessage

from agents.specialized import (
    BaseSpecializedAgent, BillingAgent, TechnicalAgent, GeneralAgent,
    billing_agent, technical_agent, general_agent,
    billing_agent_instance, technical_agent_instance, general_agent_instance
)


class TestBaseSpecializedAgent:
    """Test cases for the BaseSpecializedAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BaseSpecializedAgent("test")
    
    def test_initialization(self):
        """Test BaseSpecializedAgent initializes correctly"""
        assert self.agent.agent_type == "test"
        assert self.agent.memory == []
    
    def test_add_to_memory(self):
        """Test adding items to memory"""
        query = "Test query"
        response = "Test response"
        
        self.agent.add_to_memory(query, response)
        
        assert len(self.agent.memory) == 1
        assert self.agent.memory[0]["query"] == query
        assert self.agent.memory[0]["response"] == response
        assert "timestamp" in self.agent.memory[0]
    
    def test_get_relevant_memory_empty(self):
        """Test get_relevant_memory with empty memory"""
        result = self.agent.get_relevant_memory("test query")
        assert result == "No previous interactions"
    
    def test_get_relevant_memory_with_data(self):
        """Test get_relevant_memory with existing memory"""
        self.agent.add_to_memory("query1", "response1")
        self.agent.add_to_memory("query2", "response2")
        
        result = self.agent.get_relevant_memory("test query")
        assert "Previous interactions: 2 records" in result


class TestBillingAgent:
    """Test cases for the BillingAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = BillingAgent()
    
    def test_initialization(self):
        """Test BillingAgent initializes correctly"""
        assert self.agent.agent_type == "billing"
        assert self.agent.response_template is not None
        assert "billing specialist" in self.agent.response_template
    
    def test_generate_response_refund_query(self):
        """Test response generation for refund queries"""
        query = "I need a refund for my order"
        response = self.agent.generate_response(query)
        
        assert "refund" in response.lower()
        assert "order number" in response.lower()
        assert query in response
        assert len(self.agent.memory) == 1
    
    def test_generate_response_invoice_query(self):
        """Test response generation for invoice queries"""
        query = "Question about my invoice"
        response = self.agent.generate_response(query)
        
        assert "invoice" in response.lower()
        assert "dashboard" in response.lower()
        assert query in response
    
    def test_generate_response_payment_query(self):
        """Test response generation for payment queries"""
        query = "Payment method not working"
        response = self.agent.generate_response(query)
        
        assert "payment" in response.lower()
        assert "verify" in response.lower()
        assert query in response
    
    def test_generate_response_general_billing(self):
        """Test response generation for general billing queries"""
        query = "General billing question"
        response = self.agent.generate_response(query)
        # print("Billing Agent response:", response)
        assert "billing-related concerns" in response.lower()
        assert query in response


class TestTechnicalAgent:
    """Test cases for the TechnicalAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = TechnicalAgent()
    
    def test_initialization(self):
        """Test TechnicalAgent initializes correctly"""
        assert self.agent.agent_type == "technical"
        assert self.agent.response_template is not None
        assert "technical support specialist" in self.agent.response_template
    
    def test_generate_response_bug_query(self):
        """Test response generation for bug queries"""
        query = "Found a bug in the system"
        response = self.agent.generate_response(query)
        print("Technical Agent response:", response)
        assert "troubleshoot" in response.lower()
        assert "error messages" in response.lower()
        assert query in response
    
    def test_generate_response_feature_query(self):
        """Test response generation for feature queries"""
        query = "Feature request for new functionality"
        response = self.agent.generate_response(query)
        
        assert "feature suggestion" in response.lower()
        assert "development team" in response.lower()
        assert query in response
    
    def test_generate_response_not_working_query(self):
        """Test response generation for 'not working' queries"""
        query = "System is not working"
        response = self.agent.generate_response(query)
        
        assert "diagnose" in response.lower()
        assert "cache" in response.lower()
        assert query in response


class TestGeneralAgent:
    """Test cases for the GeneralAgent class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.agent = GeneralAgent()
    
    def test_initialization(self):
        """Test GeneralAgent initializes correctly"""
        assert self.agent.agent_type == "general"
        assert self.agent.response_template is not None
        assert "general inquiries" in self.agent.response_template
    
    def test_generate_response_account_query(self):
        """Test response generation for account queries"""
        query = "Account settings question"
        response = self.agent.generate_response(query)
        
        assert "account-related" in response.lower()
        assert "dashboard" in response.lower()
        assert query in response
    
    def test_generate_response_company_query(self):
        """Test response generation for company queries"""
        query = "About your company"
        response = self.agent.generate_response(query)
        
        assert "company" in response.lower()
        assert "website" in response.lower()
        assert query in response
    
    def test_generate_response_help_query(self):
        """Test response generation for help queries"""
        query = "I need help"
        response = self.agent.generate_response(query)
        
        assert "here to help" in response.lower()
        assert query in response


class TestAgentFunctions:
    """Test cases for the agent wrapper functions"""
    
    @patch('agents.specialized.logger')
    def test_billing_agent_function_success(self, mock_logger, billing_query_state):
        """Test billing_agent function processes query successfully"""
        initial_message_count = len(billing_query_state["messages"])
        
        result = billing_agent(billing_query_state)
        
        # Should add an AI response message
        assert len(result["messages"]) == initial_message_count + 1
        assert isinstance(result["messages"][-1], AIMessage)
        
        # Should log the processing
        mock_logger.info.assert_called()
    
    @patch('agents.specialized.logger')
    def test_technical_agent_function_success(self, mock_logger, technical_query_state):
        """Test technical_agent function processes query successfully"""
        initial_message_count = len(technical_query_state["messages"])
        
        result = technical_agent(technical_query_state)
        
        # Should add an AI response message
        assert len(result["messages"]) == initial_message_count + 1
        assert isinstance(result["messages"][-1], AIMessage)
        
        # Should log the processing
        mock_logger.info.assert_called()
    
    @patch('agents.specialized.logger')
    def test_general_agent_function_success(self, mock_logger, general_query_state):
        """Test general_agent function processes query successfully"""
        initial_message_count = len(general_query_state["messages"])
        
        result = general_agent(general_query_state)
        
        # Should add an AI response message
        assert len(result["messages"]) == initial_message_count + 1
        assert isinstance(result["messages"][-1], AIMessage)
        
        # Should log the processing
        mock_logger.info.assert_called()
    
    def test_agent_function_empty_messages(self):
        """Test agent functions with empty messages"""
        state = {
            "messages": [],
            "next_agent": "",
            "query_type": "",
            "final_response": ""
        }
        
        # All agents should handle empty messages gracefully
        for agent_func in [billing_agent, technical_agent, general_agent]:
            result = agent_func(state.copy())
            assert "messages" in result
    
    @patch('agents.specialized.billing_agent_instance.generate_response', side_effect=Exception("Test error"))
    @patch('agents.specialized.logger')
    def test_billing_agent_error_handling(self, mock_logger, mock_generate, billing_query_state):
        """Test billing_agent function error handling"""
        result = billing_agent(billing_query_state)
        
        # Should add error message
        assert len(result["messages"]) == 2
        assert "technical difficulties" in result["messages"][-1].content
        
        # Should log the error
        mock_logger.error.assert_called()
    
    @patch('agents.specialized.technical_agent_instance.generate_response', side_effect=Exception("Test error"))
    @patch('agents.specialized.logger')
    def test_technical_agent_error_handling(self, mock_logger, mock_generate, technical_query_state):
        """Test technical_agent function error handling"""
        result = technical_agent(technical_query_state)
        print("Technical Agent error handling result:", result)
        # Should add error message
        assert len(result["messages"]) == 2
        assert "technical difficulties" in result["messages"][-1].content
        
        # Should log the error
        mock_logger.error.assert_called()
    
    @patch('agents.specialized.general_agent_instance.generate_response', side_effect=Exception("Test error"))
    @patch('agents.specialized.logger')
    def test_general_agent_error_handling(self, mock_logger, mock_generate, general_query_state):
        """Test general_agent function error handling"""
        result = general_agent(general_query_state)
        
        # Should add error message
        assert len(result["messages"]) == 2
        assert "technical difficulties" in result["messages"][-1].content
        
        # Should log the error
        mock_logger.error.assert_called()


class TestAgentInstances:
    """Test cases for the global agent instances"""
    
    def test_agent_instances_exist(self):
        """Test that global agent instances exist and are correct types"""
        assert isinstance(billing_agent_instance, BillingAgent)
        assert isinstance(technical_agent_instance, TechnicalAgent)
        assert isinstance(general_agent_instance, GeneralAgent)
    
    def test_agent_instances_memory_isolation(self):
        """Test that agent instances have isolated memory"""
        # Clear any existing memory
        billing_agent_instance.memory.clear()
        technical_agent_instance.memory.clear()
        general_agent_instance.memory.clear()
        
        # Add memory to each agent
        billing_agent_instance.add_to_memory("billing query", "billing response")
        technical_agent_instance.add_to_memory("tech query", "tech response")
        general_agent_instance.add_to_memory("general query", "general response")
        
        # Verify memory isolation
        assert len(billing_agent_instance.memory) == 1
        assert len(technical_agent_instance.memory) == 1
        assert len(general_agent_instance.memory) == 1
        
        assert billing_agent_instance.memory[0]["query"] == "billing query"
        assert technical_agent_instance.memory[0]["query"] == "tech query"
        assert general_agent_instance.memory[0]["query"] == "general query"