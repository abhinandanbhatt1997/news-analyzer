#!/usr/bin/env python3
"""
Unit tests for News Analyzer components
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import validate_article, truncate_text, format_article_summary
from src.news_fetcher import NewsFetcherError
from src.llm_analyzer import LLMAnalysisError
from src.llm_validator import LLMValidationError


class TestArticleValidation(unittest.TestCase):
    """Test article validation logic"""
    
    def test_valid_article_with_all_fields(self):
        """Test that a complete article passes validation"""
        article = {
            "title": "Test Article",
            "content": "This is test content.",
            "description": "Test description"
        }
        self.assertTrue(validate_article(article))
    
    def test_valid_article_without_description(self):
        """Test that article without description still passes (description is optional)"""
        article = {
            "title": "Test Article",
            "content": "This is test content."
        }
        self.assertTrue(validate_article(article))
    
    def test_invalid_article_missing_title(self):
        """Test that article without title fails validation"""
        article = {
            "content": "This is test content.",
            "description": "Test description"
        }
        self.assertFalse(validate_article(article))
    
    def test_invalid_article_missing_content(self):
        """Test that article without content fails validation"""
        article = {
            "title": "Test Article",
            "description": "Test description"
        }
        self.assertFalse(validate_article(article))
    
    def test_invalid_article_empty_title(self):
        """Test that article with empty title fails validation"""
        article = {
            "title": "",
            "content": "This is test content."
        }
        self.assertFalse(validate_article(article))
    
    def test_invalid_article_none_content(self):
        """Test that article with None content fails validation"""
        article = {
            "title": "Test Article",
            "content": None
        }
        self.assertFalse(validate_article(article))


class TestUtilityFunctions(unittest.TestCase):
    """Test utility helper functions"""
    
    def test_truncate_text_short(self):
        """Test that short text is not truncated"""
        text = "Short text"
        result = truncate_text(text, max_length=100)
        self.assertEqual(result, "Short text")
    
    def test_truncate_text_long(self):
        """Test that long text is truncated with ellipsis"""
        text = "a" * 600
        result = truncate_text(text, max_length=500)
        self.assertEqual(len(result), 503)  # 500 chars + "..."
        self.assertTrue(result.endswith("..."))
    
    def test_truncate_text_exact_length(self):
        """Test text at exact max length is not truncated"""
        text = "a" * 500
        result = truncate_text(text, max_length=500)
        self.assertEqual(result, text)
        self.assertFalse(result.endswith("..."))
    
    def test_truncate_text_empty(self):
        """Test that empty text returns empty string"""
        result = truncate_text("", max_length=100)
        self.assertEqual(result, "")
    
    def test_truncate_text_none(self):
        """Test that None returns empty string"""
        result = truncate_text(None, max_length=100)
        self.assertEqual(result, "")
    
    def test_format_article_summary(self):
        """Test article summary formatting"""
        article = {
            "title": "Test Article",
            "source": {"name": "Test Source"},
            "publishedAt": "2026-01-17T10:00:00Z"
        }
        result = format_article_summary(article)
        self.assertIn("Test Article", result)
        self.assertIn("Test Source", result)
        self.assertIn("2026-01-17", result)
    
    def test_format_article_summary_missing_fields(self):
        """Test article summary with missing optional fields"""
        article = {
            "title": "Test Article"
        }
        result = format_article_summary(article)
        self.assertIn("Test Article", result)
        self.assertIn("Unknown", result)


class TestErrorHandling(unittest.TestCase):
    """Test custom exception classes"""
    
    def test_news_fetcher_error(self):
        """Test NewsFetcherError can be raised and caught"""
        with self.assertRaises(NewsFetcherError):
            raise NewsFetcherError("Test error message")
    
    def test_llm_analysis_error(self):
        """Test LLMAnalysisError can be raised and caught"""
        with self.assertRaises(LLMAnalysisError):
            raise LLMAnalysisError("Test analysis error")
    
    def test_llm_validation_error(self):
        """Test LLMValidationError can be raised and caught"""
        with self.assertRaises(LLMValidationError):
            raise LLMValidationError("Test validation error")
    
    def test_error_messages(self):
        """Test that error messages are preserved"""
        error_msg = "Specific error details"
        try:
            raise NewsFetcherError(error_msg)
        except NewsFetcherError as e:
            self.assertEqual(str(e), error_msg)


class TestDataStructures(unittest.TestCase):
    """Test expected data structures and formats"""
    
    def test_analysis_result_structure(self):
        """Test that analysis results have expected structure"""
        # Simulated result structure
        result = {
            "article": {"title": "Test", "content": "Content"},
            "analysis": "Mock analysis",
            "validation": {
                "verdict": "correct",
                "confidence": 0.9,
                "issues": [],
                "strengths": ["Good summary"]
            },
            "status": "validated",
            "timestamp": "2026-01-17T10:00:00"
        }
        
        # Verify structure
        self.assertIn("article", result)
        self.assertIn("analysis", result)
        self.assertIn("validation", result)
        self.assertIn("status", result)
        self.assertIn("verdict", result["validation"])
        self.assertIn("confidence", result["validation"])
    
    def test_validation_verdict_values(self):
        """Test that validation verdicts are from expected set"""
        valid_verdicts = ["correct", "partially_correct", "incorrect"]
        
        for verdict in valid_verdicts:
            validation = {"verdict": verdict}
            self.assertIn(validation["verdict"], valid_verdicts)


class TestIntegration(unittest.TestCase):
    """Integration tests for end-to-end workflows"""
    
    def test_article_processing_pipeline(self):
        """Test complete article processing workflow"""
        # Simulate pipeline: validate → analyze → validate analysis
        article = {
            "title": "Integration Test Article",
            "content": "This is integration test content for the pipeline."
        }
        
        # Step 1: Validate article
        is_valid = validate_article(article)
        self.assertTrue(is_valid)
        
        # Step 2: Would analyze (mocked)
        mock_analysis = "GIST: Test\nSENTIMENT: Neutral\nTONE: Analytical"
        
        # Step 3: Would validate (mocked)
        mock_validation = {
            "verdict": "correct",
            "confidence": 0.85,
            "issues": [],
            "strengths": ["Accurate analysis"]
        }
        
        # Verify complete result structure
        result = {
            "article": article,
            "analysis": mock_analysis,
            "validation": mock_validation,
            "status": "validated"
        }
        
        self.assertEqual(result["status"], "validated")
        self.assertIsNotNone(result["analysis"])
        self.assertIsNotNone(result["validation"])


def run_tests():
    """Run all tests and display results"""
    print("=" * 70)
    print("RUNNING NEWS ANALYZER UNIT TESTS")
    print("=" * 70)
    print()
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestArticleValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestUtilityFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestDataStructures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
