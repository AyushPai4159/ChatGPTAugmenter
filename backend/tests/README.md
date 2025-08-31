# ChatGPT Augmenter Backend Tests

This directory contains comprehensive unit tests for the ChatGPT Augmenter backend services using pytest.

## Test Structure

- `test_extract.py` - Unit tests for the ExtractService class and functions
- `test_search.py` - Unit tests for the SearchService class and functions
- `conftest.py` - Pytest configuration and shared fixtures
- `requirements-test.txt` - Additional dependencies for testing

## Installation

Install testing dependencies:

```bash
cd /home/ayush/ChatGPTAugmenter/backend
pip install -r tests/requirements-test.txt
```

## Running Tests

### Run All Tests
```bash
# From the backend directory
python -m pytest tests/

# Or with verbose output
python -m pytest tests/ -v
```

### Run Specific Test Files
```bash
# Test only extract functionality
python -m pytest tests/test_extract.py -v

# Test only search functionality
python -m pytest tests/test_search.py -v
```

### Run Tests by Category
```bash
# Run only unit tests
python -m pytest tests/ -m "unit" -v

# Run only integration tests
python -m pytest tests/ -m "integration" -v

# Skip slow tests
python -m pytest tests/ -m "not slow" -v
```

### Run with Coverage
```bash
# Generate coverage report
python -m pytest tests/ --cov=routes --cov=database --cov-report=html

# View coverage in terminal
python -m pytest tests/ --cov=routes --cov=database --cov-report=term-missing
```

## Test Features

### ExtractService Tests (`test_extract.py`)

**Main Functions Tested:**
- `extract_service()` - Main extraction workflow
- `process_conversations()` - Conversation data processing
- `extract_conversation_tree()` - Conversation parsing
- `create_embeddings()` - Embedding generation
- `save_data()` - Database and file saving
- `convert_tensor_to_bytes()` - Tensor conversion utilities
- `convert_tensor_to_base64()` - Base64 encoding utilities

**Test Coverage:**
- ✅ Successful extraction workflows
- ✅ Error handling and exceptions
- ✅ Database save and file fallback
- ✅ Various conversation data formats
- ✅ Edge cases and invalid inputs
- ✅ Integration tests with mocked dependencies

### SearchService Tests (`test_search.py`)

**Main Functions Tested:**
- `search_documents_and_extract_results()` - Main search workflow
- `integrate_extraction()` - Data loading with fallbacks
- `integrate_database_extraction()` - Database data loading
- `integrate_file_extraction()` - File data loading
- `recreate_doc_embeddings_from_database()` - Database embedding reconstruction
- `recreate_doc_embeddings_from_file()` - File embedding reconstruction
- `query_doc_similarity_scores_UNCHANGED()` - Similarity scoring
- `create_results_from_scores_UNCHANGED()` - Result formatting

**Test Coverage:**
- ✅ Complete search pipelines
- ✅ Database and file data sources
- ✅ Embedding reconstruction from bytes and base64
- ✅ Similarity calculations and ranking
- ✅ Result formatting and error handling
- ✅ Fallback mechanisms
- ✅ Integration tests with real data flows

## Test Data and Fixtures

### Shared Fixtures (conftest.py)
- `mock_sentence_transformer` - Mock ML model
- `sample_embeddings` - Test embedding tensors
- `sample_conversation_data` - Mock ChatGPT conversations
- `sample_processed_data` - Processed conversation data
- `test_uuid` - Consistent test UUID
- `mock_database_connection` - Database connection mock

### Mocking Strategy
- **External Dependencies**: SentenceTransformer models, database connections
- **File System**: Temporary files for file I/O testing
- **Network Calls**: All external API calls are mocked
- **Database Operations**: PostgreSQL operations use mocked connections

## Example Test Runs

### Successful Test Output
```bash
$ python -m pytest tests/test_extract.py -v

tests/test_extract.py::TestExtractService::test_extract_service_success PASSED
tests/test_extract.py::TestExtractService::test_process_conversations_success PASSED
tests/test_extract.py::TestExtractService::test_create_embeddings_success PASSED
tests/test_extract.py::TestExtractService::test_save_data_to_database PASSED
...

================= 25 passed, 0 failed in 2.34s =================
```

### Coverage Report
```bash
$ python -m pytest tests/ --cov=routes --cov-report=term-missing

Name                     Stmts   Miss  Cover   Missing
------------------------------------------------------
routes/extract.py          150     10    93%   245-250, 280-285
routes/search.py           180     15    92%   320-325, 400-410
------------------------------------------------------
TOTAL                      330     25    92%
```

## Test Debugging

### Running Individual Tests
```bash
# Run a specific test method
python -m pytest tests/test_extract.py::TestExtractService::test_extract_service_success -v

# Run with print statements (disable capture)
python -m pytest tests/test_extract.py -s

# Run with pdb debugger on failures
python -m pytest tests/test_extract.py --pdb
```

### Common Issues

1. **Import Errors**: Make sure you're running from the backend directory
2. **Missing Dependencies**: Install test requirements with `pip install -r tests/requirements-test.txt`
3. **Mocking Issues**: Check that external dependencies are properly mocked
4. **Database Tests**: Database tests use mocks, no real database required

## Adding New Tests

### Test File Structure
```python
import pytest
from unittest.mock import Mock, patch
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.your_module import YourService

class TestYourService:
    def setup_method(self):
        """Set up test fixtures"""
        pass
    
    def test_your_function_success(self):
        """Test successful operation"""
        pass
    
    def test_your_function_failure(self):
        """Test error handling"""
        pass
```

### Best Practices
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies
- Use fixtures for common test data
- Add docstrings to test methods
- Group related tests in classes
- Test edge cases and boundary conditions

## Continuous Integration

These tests are designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    cd backend
    pip install -r requirements.txt
    pip install -r tests/requirements-test.txt
    python -m pytest tests/ --cov=routes --cov=database
```
