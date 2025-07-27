import pytest
import sys
import os
from unittest.mock import MagicMock

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

@pytest.fixture
def sample_state():
    """Base state fixture for testing"""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="Test message")],
        "next_agent": "",
        "query_type": "",
        "final_response": ""
    }

@pytest.fixture
def billing_query_state():
    """State with billing-related query"""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="I have a billing issue with my account")],
        "next_agent": "",
        "query_type": "",
        "final_response": ""
    }

@pytest.fixture
def technical_query_state():
    """State with technical-related query"""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="The system is not working properly")],
        "next_agent": "",
        "query_type": "",
        "final_response": ""
    }

@pytest.fixture
def general_query_state():
    """State with general inquiry"""
    from langchain_core.messages import HumanMessage
    return {
        "messages": [HumanMessage(content="What are your company hours?")],
        "next_agent": "",
        "query_type": "",
        "final_response": ""
    }

@pytest.fixture
def mock_logger():
    """Mock logger to prevent logging during tests"""
    return MagicMock()