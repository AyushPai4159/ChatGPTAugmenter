"""
Pytest configuration file for ChatGPT Augmenter backend tests
"""

import pytest
import sys
import os
from unittest.mock import Mock
import torch
import numpy as np

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


@pytest.fixture(scope="session")
def mock_sentence_transformer():
    """Session-wide mock SentenceTransformer model"""
    model = Mock()
    model.encode.return_value = torch.tensor([0.1, 0.2, 0.3])
    return model


@pytest.fixture(scope="session")
def sample_embeddings():
    """Session-wide sample embeddings tensor"""
    return torch.tensor([
        [0.1, 0.2, 0.3],
        [0.4, 0.5, 0.6],
        [0.7, 0.8, 0.9],
        [0.2, 0.3, 0.4]
    ])


@pytest.fixture(scope="session")
def sample_conversation_data():
    """Session-wide sample conversation data"""
    return [
        {
            "mapping": {
                "msg1": {
                    "message": {
                        "content": {"parts": ["How do I learn Python?"]},
                        "author": {"role": "user"}
                    }
                },
                "msg2": {
                    "message": {
                        "content": {"parts": ["Start with the basics like variables and loops."]},
                        "author": {"role": "assistant"}
                    }
                }
            }
        },
        {
            "mapping": {
                "msg3": {
                    "message": {
                        "content": {"parts": ["What about machine learning?"]},
                        "author": {"role": "user"}
                    }
                },
                "msg4": {
                    "message": {
                        "content": {"parts": ["ML requires understanding of statistics and programming."]},
                        "author": {"role": "assistant"}
                    }
                }
            }
        }
    ]


@pytest.fixture(scope="session")
def sample_processed_data():
    """Session-wide sample processed data"""
    return {
        "How do I learn Python?": "Start with the basics like variables and loops.",
        "What about machine learning?": "ML requires understanding of statistics and programming.",
        "Explain neural networks": "Neural networks are computational models.",
        "What is deep learning?": "Deep learning is a subset of machine learning."
    }


@pytest.fixture
def test_uuid():
    """Test UUID for consistent testing"""
    return "test-uuid-12345"


@pytest.fixture
def temp_test_file(tmp_path):
    """Create a temporary test file"""
    def _create_file(content, filename="test.json"):
        file_path = tmp_path / filename
        file_path.write_text(content)
        return str(file_path)
    return _create_file


# Configure pytest to show more detailed output
def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", 
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", 
        "unit: marks tests as unit tests"
    )


# Custom pytest collection rules
def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        # Mark integration tests
        if "integration" in item.name.lower() or "Integration" in str(item.cls):
            item.add_marker(pytest.mark.integration)
        # Mark unit tests
        elif "Test" in str(item.cls) and "Integration" not in str(item.cls):
            item.add_marker(pytest.mark.unit)


# Test database connection mock
@pytest.fixture
def mock_database_connection():
    """Mock database connection for testing"""
    connection = Mock()
    cursor = Mock()
    connection.cursor.return_value = cursor
    return connection, cursor


# Error simulation fixtures
@pytest.fixture
def database_error():
    """Database error for testing error handling"""
    from database.postgres import DatabaseServiceException
    return DatabaseServiceException("Test database error")


@pytest.fixture
def search_error():
    """Search error for testing error handling"""
    from routes.search import SearchServiceException
    return SearchServiceException("Test search error")


@pytest.fixture
def extract_error():
    """Extract error for testing error handling"""
    from routes.extract import ExtractServiceException
    return ExtractServiceException("Test extract error")
