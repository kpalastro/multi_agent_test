import pytest
from unittest.mock import patch, MagicMock
import os
import tempfile
from langchain_core.messages import HumanMessage

from main import (
    create_multi_agent_system, run_customer_support_system,
    input_node, output_node, AgentState
)


class TestWorkflowIntegration:
    """Integration tests for the complete multi-agent workflow"""
    
    def test_create_multi_agent_system(self):
        """Test that the multi-agent system is created correctly"""
        # Mock environment to prevent graph generation during tests
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            app = create_multi_agent_system()
            
            # Verify the app was created
            assert app is not None
            
            # Verify the graph structure
            graph = app.get_graph()
            
            # Check that all expected nodes exist
            expected_nodes = {
                "input", "router", "billing_agent", "technical_agent", 
                "general_agent", "supervisor", "output"
            }
            actual_nodes = set(graph.nodes.keys())
            assert expected_nodes.issubset(actual_nodes)
    
    @patch.dict(os.environ, {'APP_ENV': 'development'})
    @patch('main.logger')
    def test_create_multi_agent_system_with_graph_generation(self, mock_logger):
        """Test graph generation in development mode"""
        with patch('builtins.open', create=True) as mock_open:
            with patch.object(type(create_multi_agent_system()), 'get_graph') as mock_get_graph:
                mock_graph = MagicMock()
                mock_graph.draw_mermaid_png.return_value = b'fake_png_data'
                mock_get_graph.return_value = mock_graph
                
                app = create_multi_agent_system()
                
                # Verify that graph generation was attempted
                mock_logger.info.assert_called()
                log_calls = [call[0][0] for call in mock_logger.info.call_args_list]
                # Should have some logging about graph generation
                assert any("Graph" in call for call in log_calls)
    
    def test_billing_workflow_end_to_end(self):
        """Test complete workflow for billing queries"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            query = "I have a billing issue with my account"
            response = run_customer_support_system(query)
            
            # Verify response is generated
            assert response is not None
            assert len(response) > 0
            assert "billing" in response.lower()
            
            # Should not be an error message
            assert "technical difficulties" not in response.lower()
    
    def test_technical_workflow_end_to_end(self):
        """Test complete workflow for technical queries"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            query = "The system is not working properly"
            response = run_customer_support_system(query)
            
            # Verify response is generated
            assert response is not None
            assert len(response) > 0
            
            # Should contain technical-related content
            technical_keywords = ["technical", "system", "troubleshoot", "error"]
            assert any(keyword in response.lower() for keyword in technical_keywords)
            
            # Should not be an error message
            assert "technical difficulties" not in response.lower()
    
    def test_general_workflow_end_to_end(self):
        """Test complete workflow for general queries"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            query = "What are your company hours?"
            response = run_customer_support_system(query)
            
            # Verify response is generated
            assert response is not None
            assert len(response) > 0
            
            # Should contain general/company-related content
            general_keywords = ["help", "assist", "company", "information"]
            assert any(keyword in response.lower() for keyword in general_keywords)
            
            # Should not be an error message
            assert "technical difficulties" not in response.lower()
    
    def test_workflow_state_transitions(self):
        """Test that state transitions work correctly through the workflow"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            app = create_multi_agent_system()
            
            initial_state = {
                "messages": [HumanMessage(content="I need a refund for my order")],
                "next_agent": "",
                "query_type": "",
                "final_response": ""
            }
            
            result = app.invoke(initial_state)
            
            # Verify state was processed correctly
            assert result["next_agent"] == "billing_agent"
            assert result["query_type"] == "BILLING"
            assert result["final_response"] != ""
            assert len(result["messages"]) > 1  # Should have added AI response
    
    def test_supervisor_improves_responses(self):
        """Test that supervisor actually improves poor responses"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            # Create a scenario where we know the response will be brief
            with patch('agents.specialized.BillingAgent.generate_response', return_value="OK"):
                query = "I have a billing problem"
                response = run_customer_support_system(query)
                
                # Supervisor should have improved the brief "OK" response
                assert response != "OK"
                assert len(response) > 10
    
    def test_memory_persistence_across_agents(self):
        """Test that agent memory persists across calls"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            from agents.specialized import billing_agent_instance
            
            # Clear existing memory
            billing_agent_instance.memory.clear()
            
            # First query
            query1 = "I have a billing issue"
            run_customer_support_system(query1)
            
            # Check memory was updated
            assert len(billing_agent_instance.memory) == 1
            assert billing_agent_instance.memory[0]["query"] == query1
            
            # Second query
            query2 = "Another billing question"
            run_customer_support_system(query2)
            
            # Memory should now have two entries
            assert len(billing_agent_instance.memory) == 2
    
    @patch('main.logger')
    def test_error_handling_in_workflow(self, mock_logger):
        """Test error handling throughout the workflow"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            # Mock an error in the workflow
            with patch('agents.router.router_agent', side_effect=Exception("Test error")):
                query = "Test query"
                response = run_customer_support_system(query)
                # print("Error handling in workflow response:", response)
                # Should return error message
                assert "technical difficulties" in response.lower()
                
                # Should log the error
                mock_logger.error.assert_called()
    
    def test_multiple_query_types_in_sequence(self):
        """Test handling multiple different query types in sequence"""
        with patch.dict(os.environ, {'APP_ENV': 'test'}):
            queries = [
                ("I need a refund", "billing"),
                ("System bug found", "technical"),
                ("Company information", "general")
            ]
            
            for query, expected_type in queries:
                response = run_customer_support_system(query)
                
                # Each should get appropriate response
                assert response is not None
                assert len(response) > 0
                assert "technical difficulties" not in response.lower()


class TestNodeFunctions:
    """Test individual node functions"""
    
    def test_input_node(self):
        """Test input_node function"""
        state = {
            "messages": [HumanMessage(content="Test message")],
            "next_agent": "",
            "query_type": "",
            "final_response": ""
        }
        
        result = input_node(state)
        
        # Should return state unchanged
        assert result == state
    
    def test_output_node(self):
        """Test output_node function"""
        state = {
            "messages": [HumanMessage(content="Test message")],
            "next_agent": "billing_agent",
            "query_type": "BILLING",
            "final_response": "Test response"
        }
        
        result = output_node(state)
        
        # Should return state unchanged
        assert result == state
    
    @patch('main.logger')
    def test_node_logging(self, mock_logger):
        """Test that nodes log their actions"""
        state = {"messages": [], "next_agent": "", "query_type": "", "final_response": ""}
        
        input_node(state)
        output_node(state)
        
        # Should have logged processing
        assert mock_logger.info.call_count >= 2


class TestAgentStateStructure:
    """Test the AgentState TypedDict structure"""
    
    def test_agent_state_structure(self):
        """Test that AgentState has the expected structure"""
        from typing import get_type_hints
        
        hints = get_type_hints(AgentState)
        
        # Check required fields exist
        assert 'messages' in hints
        assert 'next_agent' in hints
        assert 'query_type' in hints
        assert 'final_response' in hints
    
    def test_agent_state_creation(self):
        """Test creating an AgentState-compatible dict"""
        state = {
            "messages": [HumanMessage(content="Test")],
            "next_agent": "billing_agent",
            "query_type": "BILLING",
            "final_response": "Test response"
        }
        
        # Should be compatible with AgentState
        assert isinstance(state["messages"], list)
        assert isinstance(state["next_agent"], str)
        assert isinstance(state["query_type"], str)
        assert isinstance(state["final_response"], str)


class TestSystemConfiguration:
    """Test system configuration and environment handling"""
    
    def test_app_env_detection(self):
        """Test APP_ENV environment variable detection"""
        # Test default value
        with patch.dict(os.environ, {}, clear=True):
            from importlib import reload
            import main
            reload(main)
            assert main.APP_ENV == "development"
        
        # Test custom value
        with patch.dict(os.environ, {'APP_ENV': 'production'}):
            from importlib import reload
            import main
            reload(main)
            assert main.APP_ENV == "production"
    
    def test_logging_configuration(self):
        """Test that logging is configured correctly"""
        import logging
        
        # Verify logger exists and is configured
        logger = logging.getLogger('main')
        assert logger is not None
        
        # Should have at least one handler (from basicConfig)
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0