"""
Pytest tests for the Writesonic SEO Analyzer API.
Run with: pytest test_main.py -v
"""

import pytest
from fastapi.testclient import TestClient
from main import app, clean_text, get_stopwords, calculate_keyword_stats, calc_readability, mock_plagiarism, compute_final_score

# Create test client
client = TestClient(app)


class TestHelperFunctions:
    """Test suite for helper functions"""
    
    def test_clean_text(self):
        """Test text cleaning function"""
        text = "Hello, World! This is A TEST."
        cleaned = clean_text(text)
        assert cleaned == "hello world this is a test"
        assert "," not in cleaned
        assert "!" not in cleaned
    
    def test_get_stopwords(self):
        """Test stopwords loading"""
        stopwords = get_stopwords()
        assert isinstance(stopwords, set)
        assert len(stopwords) > 0
        assert "the" in stopwords
        assert "and" in stopwords
    
    def test_calculate_keyword_stats(self):
        """Test keyword statistics calculation"""
        text = "Python programming is great. Python is powerful. Programming with Python is fun."
        top_keywords, keyword_density = calculate_keyword_stats(text, top_n=5)
        
        assert isinstance(top_keywords, list)
        assert isinstance(keyword_density, dict)
        assert len(top_keywords) > 0
        
        # Check that 'python' is a top keyword
        keywords_list = [kw[0] for kw in top_keywords]
        assert "python" in keywords_list
    
    def test_calc_readability(self):
        """Test readability calculation"""
        simple_text = "The cat sat on the mat. It was a nice day."
        score = calc_readability(simple_text)
        
        assert isinstance(score, float)
        assert 0 <= score <= 100
    
    def test_mock_plagiarism(self):
        """Test plagiarism detection"""
        # Original text should have low plagiarism
        original = "This is completely unique content about quantum computing and blockchain."
        score = mock_plagiarism(original)
        assert isinstance(score, float)
        assert 0 <= score <= 100
        
        # Empty text should return 0
        empty_score = mock_plagiarism("")
        assert empty_score == 0.0
    
    def test_compute_final_score(self):
        """Test final score computation"""
        top_keywords = [("test", 5), ("example", 3)]
        keyword_density = {"test": 10.0, "example": 6.0}
        keyword_stats = (top_keywords, keyword_density)
        
        final_score = compute_final_score(60.0, 10.0, keyword_stats)
        
        assert isinstance(final_score, float)
        assert 0 <= final_score <= 100


class TestAPI:
    """Test suite for API endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "status" in data
        assert data["status"] == "active"
    
    def test_analyze_valid_text(self):
        """Test analyze endpoint with valid text"""
        sample_text = """
        Search engine optimization is crucial for online visibility. Quality content
        that engages readers and provides value is essential for SEO success. Keywords
        should be used naturally throughout the text.
        """
        
        response = client.post("/analyze", json={"text": sample_text})
        assert response.status_code == 200
        
        data = response.json()
        assert "readability" in data
        assert "top_keywords" in data
        assert "keyword_density" in data
        assert "plagiarism_score" in data
        assert "final_score" in data
        
        # Validate data types
        assert isinstance(data["readability"], (int, float))
        assert isinstance(data["top_keywords"], list)
        assert isinstance(data["keyword_density"], dict)
        assert isinstance(data["plagiarism_score"], (int, float))
        assert isinstance(data["final_score"], (int, float))
        
        # Validate ranges
        assert 0 <= data["readability"] <= 100
        assert 0 <= data["plagiarism_score"] <= 100
        assert 0 <= data["final_score"] <= 100
    
    def test_analyze_short_text(self):
        """Test analyze endpoint with too short text"""
        response = client.post("/analyze", json={"text": "Short"})
        assert response.status_code == 400
        assert "at least 10 characters" in response.json()["detail"]
    
    def test_analyze_empty_text(self):
        """Test analyze endpoint with empty text"""
        response = client.post("/analyze", json={"text": ""})
        assert response.status_code == 400
    
    def test_analyze_keyword_extraction(self):
        """Test that keywords are properly extracted"""
        text = """
        Digital marketing strategies are essential for business growth. Marketing
        automation helps streamline digital marketing efforts. Social media marketing
        is a key component of modern marketing strategies.
        """
        
        response = client.post("/analyze", json={"text": text})
        assert response.status_code == 200
        
        data = response.json()
        keywords_list = [kw[0] for kw in data["top_keywords"]]
        
        # 'marketing' should be a top keyword since it appears frequently
        assert "marketing" in keywords_list
    
    def test_analyze_plagiarism_detection(self):
        """Test plagiarism detection with similar content"""
        # Use text very similar to one of the SAMPLE_TEXTS
        similar_text = """
        Search engine optimization is crucial for online visibility. Quality content
        that engages readers and provides value is essential for SEO success.
        """
        
        response = client.post("/analyze", json={"text": similar_text})
        assert response.status_code == 200
        
        data = response.json()
        # Should detect some similarity
        assert data["plagiarism_score"] > 0


class TestIntegration:
    """Integration tests"""
    
    def test_complete_analysis_workflow(self):
        """Test complete analysis workflow with real-world text"""
        article = """
        Artificial Intelligence is transforming the way we work and live. Machine learning
        algorithms can analyze vast amounts of data to identify patterns and make predictions.
        Natural language processing enables computers to understand and generate human language.
        Deep learning neural networks have achieved remarkable results in image recognition,
        speech synthesis, and game playing. AI applications are being deployed across industries
        including healthcare, finance, transportation, and entertainment. As AI technology
        continues to advance, it raises important questions about ethics, privacy, and the
        future of work. Responsible AI development requires careful consideration of these
        societal impacts.
        """
        
        response = client.post("/analyze", json={"text": article})
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify all required fields are present and valid
        assert data["readability"] > 0
        assert len(data["top_keywords"]) > 0
        assert len(data["keyword_density"]) > 0
        assert data["final_score"] > 0
        
        # Print results for manual inspection
        print("\n" + "="*60)
        print("Integration Test Results")
        print("="*60)
        print(f"Readability: {data['readability']:.2f}")
        print(f"Plagiarism: {data['plagiarism_score']:.2f}%")
        print(f"Final Score: {data['final_score']:.2f}/100")
        print(f"Top 5 Keywords:")
        for word, count in data['top_keywords'][:5]:
            print(f"  - {word}: {count} ({data['keyword_density'][word]}%)")
        print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
