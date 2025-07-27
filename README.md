# Multi-Agent Customer Support System

A LangGraph-based multi-agent system that simulates a customer support workflow. The system intelligently routes user queries to specialized agents based on issue type (Billing, Technical, or General), with a Supervisor agent ensuring response quality.

## System Architecture

```
User Query → Input Node → Router Agent → Specialized Agent → Supervisor Agent → Final Response
                              ↓
                    [Billing | Technical | General]
```
## Workflow Diagram

Below is a visual representation of the system architecture:

![Workflow Diagram](graph.png)
### Components

- **Input Node**: Processes initial user queries
- **Router Agent**: Classifies queries and routes to appropriate specialists
- **Specialized Agents**:
  - **Billing Agent**: Handles payment, invoice, and billing-related queries
  - **Technical Agent**: Manages technical issues, bugs, and feature requests
  - **General Agent**: Processes general inquiries and company information
- **Supervisor Agent**: Performs quality assurance and edits responses as needed
- **Final Response Node**: Returns the approved response to the user



## Project Structure

```
multi_agent_test/
├── main.py                 # Main application entry point
├── agents/
│   ├── __init__.py
│   ├── router.py          # Query classification logic
│   ├── specialized.py     # Billing, Technical, and General agents
│   └── supervisor.py      # Quality assurance and response editing
├── tests/                  # Comprehensive test suite
│   ├── __init__.py
│   ├── conftest.py        # Test fixtures and configuration
│   ├── test_router.py     # Router agent tests
│   ├── test_specialized.py # Specialized agents tests
│   ├── test_supervisor.py # Supervisor agent tests
│   └── test_integration.py # End-to-end workflow tests
├── .env.example           # Environment configuration template
├── .gitignore
├── README.md
├── pytest.ini             # Test configuration
├── requirements-test.txt  # Testing dependencies
├── graph.png              # Auto-generated workflow diagram (in development mode)
└── INITIAL.md            # Project requirements
```

## Features

- **Intelligent Query Routing**: Automatic classification of user queries
- **Specialized Response Handling**: Domain-specific agents for different query types
- **Quality Assurance**: Supervisor agent reviews and improves responses
- **Memory Functionality**: Agents maintain conversation history
- **Error Handling**: Comprehensive logging and error management
- **Graph Visualization**: Automatic generation of workflow diagram (graph.png) in development mode
- **Comprehensive Testing**: Full unit and integration test coverage with pytest
- **Extensible Architecture**: Easy to add new agent types or modify existing ones

## Setup Instructions

### Prerequisites

- Python 3.8+
- Virtual environment (already set up per requirements)

### Installation

1. **Clone and navigate to the project**:
   ```bash
   cd /path/to/multi_agent_test
   ```

2. **Activate the virtual environment**:
   ```bash
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies** (if not already installed):
   ```bash
   pip install langgraph langchain-core python-dotenv
   
   # Optional: For graph visualization
   pip install pygraphviz
   
   # For testing (optional)
   pip install -r requirements-test.txt
   ```

4. **Environment Configuration**:
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration if needed
   ```

### Configuration

#### Basic Setup (No External APIs Required)

The system works out-of-the-box with basic keyword-based classification and template responses. No external API keys are required for basic functionality.

#### Advanced Setup (Optional)

For enhanced functionality with LLM providers:

1. **OpenAI Integration**:
   ```bash
   # Add to .env
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. **Anthropic Integration**:
   ```bash
   # Add to .env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

3. **Gmail Configuration** (for notifications):
   ```bash
   # Add to .env
   GMAIL_USER=your_email@gmail.com
   GMAIL_PASSWORD=your_app_password_here
   ```

4. **Brave Search** (for web search capabilities):
   ```bash
   # Add to .env
   BRAVE_API_KEY=your_brave_search_api_key_here
   ```

## Usage

### Running the Demo

```bash
python main.py
```

This will run the system with three example queries demonstrating different agent types. In development mode (APP_ENV=development), this will also generate a `graph.png` file showing the workflow visualization.

![Output](output.png)

### Using the System Programmatically

```python
from main import run_customer_support_system

# Process a user query
response = run_customer_support_system("I need help with my billing")
print(response)
```

### Example Queries

- **Billing**: "I have a billing issue with my account", "Need a refund for my order"
- **Technical**: "The system is not working", "I found a bug in the application"
- **General**: "What are your company hours?", "How do I update my account?"

## System Workflow

1. **Input Processing**: User query is received and prepared
2. **Query Classification**: Router agent analyzes the query and determines the appropriate specialist
3. **Specialized Handling**: The selected agent (Billing, Technical, or General) processes the query
4. **Quality Assurance**: Supervisor agent evaluates the response for:
   - Completeness
   - Accuracy
   - Professional tone
   - Clarity
5. **Response Improvement**: If needed, the supervisor edits or enhances the response
6. **Final Output**: The approved response is returned to the user

## Memory System

Each specialized agent maintains conversation history:
- Stores previous queries and responses
- Provides context for follow-up questions
- Enables personalized interactions

## Logging

The system includes comprehensive logging:
- Agent routing decisions
- Processing status
- Error handling
- Quality assurance evaluations

## Extending the System

### Adding New Agent Types

1. Create a new agent class in `agents/specialized.py`
2. Add routing logic in `agents/router.py`
3. Update the workflow in `main.py`

### Customizing Response Templates

Modify the `response_template` in each agent class to match your organization's tone and style.

### Integrating External APIs

Add API calls in the agent's `generate_response` method for enhanced functionality.

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed and virtual environment is activated
2. **Classification Issues**: Check keyword lists in router agent
3. **Memory Issues**: Verify memory limits in configuration

### Debugging

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Testing

The project includes a comprehensive test suite covering all components:

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=agents --cov=main

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only

# Run tests for specific components
pytest tests/test_router.py
pytest tests/test_specialized.py
pytest tests/test_supervisor.py
pytest tests/test_integration.py

# Verbose output with details
pytest -v

# Run tests and generate HTML coverage report
pytest --cov=agents --cov=main --cov-report=html
```

### Test Structure

- **Unit Tests**: Test individual components in isolation
  - `test_router.py`: Router agent classification logic
  - `test_specialized.py`: All specialized agent functionality
  - `test_supervisor.py`: Supervisor quality assurance logic

- **Integration Tests**: Test complete workflows end-to-end
  - `test_integration.py`: Full system workflow testing

### Test Configuration

- `pytest.ini`: Test runner configuration
- `conftest.py`: Shared test fixtures and utilities
- `requirements-test.txt`: Testing dependencies

### Writing New Tests

When adding new features, include tests following the existing patterns:

```python
# Unit test example
def test_new_agent_functionality():
    agent = NewAgent()
    result = agent.process_query("test query")
    assert result is not None
    assert "expected_content" in result

# Integration test example  
def test_new_workflow_integration():
    response = run_customer_support_system("test query")
    assert response != ""
    assert "technical difficulties" not in response.lower()
```

## Development

### Adding New Features

1. **Implement the feature** in the appropriate module
2. **Add unit tests** to verify component functionality
3. **Add integration tests** to verify end-to-end behavior
4. **Update documentation** in README.md
5. **Run the full test suite** to ensure no regressions

### Testing New Queries

Add test queries to the main.py file or create separate test files:

```python
test_queries = [
    "Your test query here",
    # Add more test cases
]
```

### Contributing

1. Follow the existing code structure
2. Add appropriate logging
3. Update documentation for new features
4. Test with various query types

## License

This project is for educational and demonstration purposes.