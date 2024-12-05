import pytest
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.crawler import main, setup_logging
import os
import argparse
import logging

@pytest.fixture
def reset_logging():
    """Reset logging configuration before and after each test"""
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)
    yield
    logging.root.handlers = []
    logging.root.setLevel(logging.WARNING)

def test_main_with_no_arguments(capsys):
    """Test main function with no command line arguments"""
    # Simulate no command line arguments
    with patch.object(sys, 'argv', ['crawler.py']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 2
        
        # Check if usage message was printed
        captured = capsys.readouterr()
        assert "usage: crawler.py" in captured.err
        assert "domain" in captured.err

def test_main_with_domain():
    """Test main function with a valid domain argument"""
    # Create a mock WebsiteCrawler
    mock_crawler = MagicMock()
    
    # Patch the WebsiteCrawler class
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        # Set up command line argument
        with patch.object(sys, 'argv', ['crawler.py', 'example.com']):
            main()
            
            # Verify crawler methods were called
            mock_crawler.crawl.assert_called_once_with(recursive=False)
            mock_crawler.save_results.assert_called_once()

def test_main_with_external_links():
    """Test main function with external links flag"""
    mock_crawler = MagicMock()
    
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        with patch.object(sys, 'argv', ['crawler.py', 'example.com', '-e']):
            main()
            
            # Verify crawler methods were called with correct arguments
            mock_crawler.crawl.assert_called_once_with(collect_external=True, recursive=False)
            mock_crawler.save_external_links_results.assert_called_once()
            assert not mock_crawler.save_results.called

def test_main_with_recursive():
    """Test main function with recursive flag"""
    mock_crawler = MagicMock()
    
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        with patch.object(sys, 'argv', ['crawler.py', 'example.com', '-r']):
            main()
            
            # Verify crawler methods were called with recursive=True
            mock_crawler.crawl.assert_called_once_with(recursive=True)
            mock_crawler.save_results.assert_called_once()

def test_setup_logging_verbose(reset_logging):
    """Test logging setup in verbose mode"""
    setup_logging(verbose=True)
    assert logging.getLogger().level == logging.DEBUG

def test_setup_logging_normal(reset_logging):
    """Test logging setup in normal mode"""
    setup_logging(verbose=False)
    assert logging.getLogger().level == logging.INFO

def test_main_with_error(capsys, reset_logging):
    """Test main function when crawler encounters an error"""
    mock_crawler = MagicMock()
    test_error = Exception("Network error")
    mock_crawler.crawl.side_effect = test_error
    
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        with patch.object(sys, 'argv', ['crawler.py', 'example.com']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            
            assert exc_info.value.code == 1
            # Verify error was logged to stderr
            captured = capsys.readouterr()
            assert "An error occurred: Network error" in captured.err

def test_main_with_all_options():
    """Test main function with all flags enabled"""
    mock_crawler = MagicMock()
    
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        with patch.object(sys, 'argv', ['crawler.py', 'example.com', '-e', '-v', '-r']):
            main()
            
            # Verify crawler methods were called with all options
            mock_crawler.crawl.assert_called_once_with(collect_external=True, recursive=True)
            mock_crawler.save_external_links_results.assert_called_once()
            assert not mock_crawler.save_results.called
