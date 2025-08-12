import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the Python path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from routes.search import SearchService, SearchServiceException
from database.postgres import DatabaseServiceException


class TestSearchService:
    """Test suite for SearchService class"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        self.mock_model = Mock()
        self.mock_model.encode.return_value = torch.tensor([0.1, 0.2, 0.3, 0.4])
        
        self.test_uuid = "test-uuid-123"
        self.test_query = "How do I learn Python?"
        self.test_top_k = 3
        
        # Mock embeddings and data
        self.mock_doc_embeddings = torch.tensor([
            [0.1, 0.2, 0.3, 0.4],
            [0.5, 0.6, 0.7, 0.8],
            [0.9, 1.0, 1.1, 1.2]
        ])
        
        self.mock_processed_data = {
            "How do I learn Python?": "Start with basics",
            "What is machine learning?": "AI subset",
            "How to use TensorFlow?": "Deep learning framework"
        }
        
        self.mock_keys = list(self.mock_processed_data.keys())
        
        self.mock_similarity_scores = {
            'cos_scores': torch.tensor([0.9, 0.8, 0.7]),
            'top_indices': torch.tensor([[0, 1, 2]])
        }
        
        self.mock_database_extraction = {
            "doc_embeddings": self.mock_doc_embeddings,
            "data": self.mock_processed_data,
            "keys": self.mock_keys
        }

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR SEARCH_DOCUMENTS_AND_EXTRACT_RESULTS() ROOT FUNCTION"""

    @patch('routes.search.SearchService.create_results_from_scores_UNCHANGED')
    @patch('routes.search.SearchService.query_doc_similarity_scores_UNCHANGED')
    @patch('routes.search.SearchService.integrate_extraction')
    def test_integration_search_documents_and_extract_results_success(self, mock_integrate, mock_similarity, mock_create_results):
        """Test successful search_documents_and_extract_results execution"""
        # Setup mocks
        mock_integrate.return_value = self.mock_database_extraction
        mock_similarity.return_value = {
            'cos_scores': torch.tensor([0.9, 0.8, 0.7]),
            'top_indices': torch.tensor([[0, 1, 2]])
        }
        mock_create_results.return_value = [
            {"question": "How do I learn Python?", "answer": "Start with basics", "score": 0.9}
        ]
        
        # Execute
        result = SearchService.search_documents_and_extract_results(
            self.test_uuid, self.test_query, self.test_top_k, self.mock_model
        )
        
        # Verify
        assert result["query"] == self.test_query
        assert result["total_results"] == 1
        assert "results" in result
        
        # Verify method calls
        mock_integrate.assert_called_once_with(self.test_uuid)
        mock_similarity.assert_called_once()
        mock_create_results.assert_called_once()

    def test_unit_search_documents_and_extract_results_no_model(self):
        """Test search_documents_and_extract_results with missing model"""
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                self.test_uuid, self.test_query, self.test_top_k, None
            )
        assert "Model, query, or uuid not provided" in str(exc_info.value)

    def test_unit_search_documents_and_extract_results_no_query(self):
        """Test search_documents_and_extract_results with missing query"""
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                self.test_uuid, None, self.test_top_k, self.mock_model
            )
        assert "Model, query, or uuid not provided" in str(exc_info.value)

    def test_unit_search_documents_and_extract_results_no_uuid(self):
        """Test search_documents_and_extract_results with missing uuid"""
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                None, self.test_query, self.test_top_k, self.mock_model
            )
        assert "Model, query, or uuid not provided" in str(exc_info.value)

    @patch('routes.search.SearchService.integrate_extraction')
    def test_unit_search_documents_and_extract_results_integrate_extraction_failure(self, mock_integrate):
        """Test search_documents_and_extract_results when integrate_extraction fails"""
        mock_integrate.side_effect = SearchServiceException("Database extraction failed")
        
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                self.test_uuid, self.test_query, self.test_top_k, self.mock_model
            )
        assert "Database extraction failed" in str(exc_info.value)

    @patch('routes.search.SearchService.query_doc_similarity_scores_UNCHANGED')
    @patch('routes.search.SearchService.integrate_extraction')
    def test_unit_search_documents_and_extract_results_similarity_failure(self, mock_integrate, mock_similarity):
        """Test search_documents_and_extract_results when similarity calculation fails"""
        mock_integrate.return_value = self.mock_database_extraction
        mock_similarity.side_effect = SearchServiceException("Similarity calculation failed")
        
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                self.test_uuid, self.test_query, self.test_top_k, self.mock_model
            )
        assert "Similarity calculation failed" in str(exc_info.value)

    @patch('routes.search.SearchService.create_results_from_scores_UNCHANGED')
    @patch('routes.search.SearchService.query_doc_similarity_scores_UNCHANGED')
    @patch('routes.search.SearchService.integrate_extraction')
    def test_unit_search_documents_and_extract_results_formatting_failure(self, mock_integrate, mock_similarity, mock_format):
        """Test search_documents_and_extract_results when similarity calculation fails"""
        mock_integrate.return_value = self.mock_database_extraction
        mock_similarity.return_value = self.mock_similarity_scores
        mock_format.side_effect = SearchServiceException("Results formatting failed")
        
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.search_documents_and_extract_results(
                self.test_uuid, self.test_query, self.test_top_k, self.mock_model
            )
        assert "Results formatting failed" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR INTEGRATE_EXTRACTION() AND CHILD FUNCTIONS"""

    @patch('routes.search.SearchService.integrate_database_extraction')
    def test_integration_integrate_extraction_success(self, mock_db_extract):
        """Test successful integrate_extraction execution"""
        mock_db_extract.return_value = self.mock_database_extraction
        
        result = SearchService.integrate_extraction(self.test_uuid)
        
        assert result == self.mock_database_extraction
        mock_db_extract.assert_called_once_with(self.test_uuid)

    @patch('routes.search.SearchService.integrate_file_extraction')
    @patch('routes.search.SearchService.integrate_database_extraction')
    def test_integration_integrate_extraction_fallback_to_file(self, mock_db_extract, mock_file_extract):
        """Test integrate_extraction fallback from database to file"""
        mock_db_extract.side_effect = SearchServiceException("Database connection failed")
        mock_file_extract.return_value = self.mock_database_extraction
        
        result = SearchService.integrate_extraction(self.test_uuid)
        
        assert result == self.mock_database_extraction
        mock_db_extract.assert_called_once_with(self.test_uuid)
        mock_file_extract.assert_called_once_with(self.test_uuid)

    @patch('routes.search.SearchService.integrate_file_extraction')
    @patch('routes.search.SearchService.integrate_database_extraction')
    def test_unit_integrate_extraction_both_methods_fail(self, mock_db_extract, mock_file_extract):
        """Test integrate_extraction when both database and file methods fail"""
        mock_db_extract.side_effect = SearchServiceException("Database error")
        mock_file_extract.side_effect = SearchServiceException("File error")
        
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.integrate_extraction(self.test_uuid)
        assert "Database extraction failed" in str(exc_info.value)

    
    @patch('routes.search.SearchService.recreate_doc_embeddings_from_database')
    @patch('routes.search.DatabaseService.load_user_data_from_database')
    def test_unit_integrate_database_extraction_success(self, mock_load_data, mock_recreate_embeddings):
        """Test successful integrate_database_extraction execution"""
        mock_user_data = {
            'processed_data': self.mock_processed_data,
            'key_order': self.mock_keys,
            'embeddings': b'mock_embeddings_bytes',
            'embedding_shape': (3, 4)
        }
        mock_load_data.return_value = mock_user_data
        mock_recreate_embeddings.return_value = self.mock_doc_embeddings
        
        result = SearchService.integrate_database_extraction(self.test_uuid)
        
        assert result["data"] == self.mock_processed_data
        assert result["keys"] == self.mock_keys
        assert torch.equal(result["doc_embeddings"], self.mock_doc_embeddings)
        mock_load_data.assert_called_once_with(self.test_uuid)
        mock_recreate_embeddings.assert_called_once_with(b'mock_embeddings_bytes', (3, 4))

    def test_unit_recreate_doc_embeddings_from_database_success(self):
        """Test successful recreate_doc_embeddings_from_database execution"""
        original_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        embeddings_bytes = original_embeddings.tobytes()
        embedding_shape = (2, 2)
        
        result = SearchService.recreate_doc_embeddings_from_database(embeddings_bytes, embedding_shape)
        
        assert isinstance(result, torch.Tensor)
        assert result.shape == torch.Size([2, 2])
        assert torch.allclose(result, torch.from_numpy(original_embeddings))

    
    def test_unit_recreate_doc_embeddings_from_database_failure(self):
        """Test successful recreate_doc_embeddings_from_database execution"""
        original_embeddings = np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32)
        embeddings_bytes = None
        embedding_shape = None
        with pytest.raises(SearchServiceException):
            result = SearchService.recreate_doc_embeddings_from_database(embeddings_bytes, embedding_shape)
        


    @patch('routes.search.SearchService.recreate_doc_embeddings_from_file')
    @patch('routes.search.SearchService.load_user_data_from_file')
    def test_unit_integrate_file_extraction_success(self, mock_load_file, mock_recreate_file_embeddings):
        """Test successful integrate_file_extraction execution"""
        mock_user_data = {
            "processed_data": self.mock_processed_data,
            "embeddings": "base64_encoded_embeddings",
            "keys": list(self.mock_processed_data.keys())
        }
        mock_load_file.return_value = mock_user_data
        mock_recreate_file_embeddings.return_value = self.mock_doc_embeddings
        
        result = SearchService.integrate_file_extraction(self.test_uuid)
        
        assert result["data"] == self.mock_processed_data
        assert result["keys"] == self.mock_keys
        assert torch.equal(result["doc_embeddings"], self.mock_doc_embeddings)

    @patch('routes.search.os.path.exists')
    def test_unit_load_user_data_from_file_not_found(self, mock_exists):
        """Test load_user_data_from_file when file not found"""
        mock_exists.return_value = False
        
        with pytest.raises(SearchServiceException) as exc_info:
            SearchService.load_user_data_from_file(self.test_uuid)
        assert "conversations.json not found" in str(exc_info.value)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR QUERY_DOC_SIMILARITY_SCORES_UNCHANGED() AND CHILD FUNCTIONS"""

    @patch('routes.search.SearchService.get_top_k_results')
    @patch('routes.search.SearchService.calculate_cosine_similarities')
    @patch('routes.search.SearchService.encode_query_to_embedding')
    def test_integration_query_doc_similarity_scores_success(self, mock_encode, mock_calculate, mock_get_top_k):
        """Test successful query_doc_similarity_scores_UNCHANGED execution"""
        mock_query_embedding = torch.tensor([0.1, 0.2, 0.3, 0.4])
        mock_cos_scores = torch.tensor([[0.9, 0.8, 0.7]])
        mock_top_k_result = {
            'cos_scores': torch.tensor([0.9, 0.8, 0.7]),
            'top_indices': torch.tensor([[2, 0, 1]])
        }
        
        mock_encode.return_value = mock_query_embedding
        mock_calculate.return_value = mock_cos_scores
        mock_get_top_k.return_value = mock_top_k_result
        
        result = SearchService.query_doc_similarity_scores_UNCHANGED(
            self.test_query, self.test_top_k, self.mock_model, self.mock_doc_embeddings, self.mock_keys
        )
        
        assert torch.equal(result["cos_scores"], torch.tensor([0.9, 0.8, 0.7]))
        assert torch.equal(result["top_indices"], torch.tensor([[2, 0, 1]]))
        mock_encode.assert_called_once_with(self.test_query, self.mock_model)
        mock_calculate.assert_called_once_with(mock_query_embedding, self.mock_doc_embeddings)
        mock_get_top_k.assert_called_once_with(mock_cos_scores, self.test_top_k, self.mock_keys)

    
    def test_unit_encode_query_to_embedding_success(self):
        """Test successful encode_query_to_embedding execution"""
        result = SearchService.encode_query_to_embedding(self.test_query, self.mock_model)
        
        assert torch.equal(result, torch.tensor([0.1, 0.2, 0.3, 0.4]))
        self.mock_model.encode.assert_called_once_with(self.test_query, convert_to_tensor=True)

    @patch('sentence_transformers.util.pytorch_cos_sim')
    def test_unit_calculate_cosine_similarities_success(self, mock_cos_sim):
        """Test successful calculate_cosine_similarities execution"""
        query_embedding = torch.tensor([0.1, 0.2, 0.3, 0.4])
        doc_embeddings = torch.tensor([[0.1, 0.2, 0.3, 0.4], [0.5, 0.6, 0.7, 0.8]])
        
        mock_cos_sim.return_value = torch.tensor([[0.9, 0.8]])
        
        result = SearchService.calculate_cosine_similarities(query_embedding, doc_embeddings)
        
        assert isinstance(result, torch.Tensor)
        assert torch.equal(result, torch.tensor([[0.9, 0.8]]))
        mock_cos_sim.assert_called_once_with(query_embedding, doc_embeddings)

    def test_unit_get_top_k_results_success(self):
        """Test successful get_top_k_results execution"""
        cos_scores = torch.tensor([[0.9, 0.7, 0.8]])
        top_k = 2
        keys = ["key1", "key2", "key3"]
        
        result = SearchService.get_top_k_results(cos_scores, top_k, keys)
        
        assert isinstance(result, dict)
        assert 'cos_scores' in result
        assert 'top_indices' in result
        assert isinstance(result['cos_scores'], torch.Tensor)
        assert isinstance(result['top_indices'], torch.Tensor)

    """----------------------------------------------------------------------------------------------------------------------------"""
    """TESTS FOR CREATE_RESULTS_FROM_SCORES_UNCHANGED() AND CHILD FUNCTIONS"""

    @patch('routes.search.SearchService.format_single_result')
    def test_integration_create_results_from_scores_success(self, mock_format):
        """Test successful create_results_from_scores_UNCHANGED execution"""
        cos_scores = torch.tensor([0.9, 0.8])
        top_indices = torch.tensor([[0, 1]])
        
        mock_format.side_effect = [
            {"key": "Question 1", "content": "Answer 1", "similarity": 0.9},
            {"key": "Question 2", "content": "Answer 2", "similarity": 0.8}
        ]
        
        result = SearchService.create_results_from_scores_UNCHANGED(
            cos_scores, top_indices, self.mock_processed_data, self.mock_keys
        )
        
        assert len(result) == 2
        assert result[0]["similarity"] == 0.9
        assert result[1]["similarity"] == 0.8
        assert mock_format.call_count == 2

    
    def test_unit_format_single_result_success(self):
        """Test successful format_single_result execution"""
        idx = 0
        cos_scores = torch.tensor([0.9, 0.8])
        keys = ["How do I learn Python?", "What is machine learning?"]
        data = {
            "How do I learn Python?": "Start with basics",
            "What is machine learning?": "AI subset"
        }
        
        result = SearchService.format_single_result(idx, cos_scores, keys, data)
        
        assert result["key"] == "How do I learn Python?"
        assert result["content"] == "Start with basics"
        assert round(result["similarity"], 1) == 0.9


    def test_unit_format_single_result_index_failure(self):
        idx = 6
        cos_scores = torch.tensor([0.9, 0.8])
        keys = ["How do I learn Python?", "What is machine learning?"]
        data = {
            "How do I learn Python?": "Start with basics",
            "What is machine learning?": "AI subset"
        }
        
        with pytest.raises(SearchServiceException) as exc_info:
            result = SearchService.format_single_result(idx, cos_scores, keys, data)

        assert "idx is out of bounds for keys array given" in str(exc_info)
        
        

    """----------------------------------------------------------------------------------------------------------------------------"""

    

    

    


# ===== PYTEST FIXTURES =====

@pytest.fixture
def mock_sentence_transformer():
    """Fixture for mock SentenceTransformer model"""
    model = Mock()
    model.encode.return_value = torch.tensor([0.1, 0.2, 0.3, 0.4])
    return model

@pytest.fixture
def sample_search_data():
    """Fixture for sample search data"""
    return {
        "embeddings": torch.tensor([[0.1, 0.2], [0.3, 0.4]]),
        "processed_data": {
            "How to learn Python?": "Start with basics",
            "What is AI?": "Artificial Intelligence"
        },
        "keys": ["How to learn Python?", "What is AI?"]
    }
