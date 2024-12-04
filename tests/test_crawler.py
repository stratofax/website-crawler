import pytest
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.crawler import main
import os

def test_main_with_no_arguments(capsys):
    """Test main function with no command line arguments"""
    # Simulate no command line arguments
    with patch.object(sys, 'argv', ['crawler.py']):
        with pytest.raises(SystemExit) as exc_info:
            main()
        
        assert exc_info.value.code == 1
        
        # Check if usage message was printed
        captured = capsys.readouterr()
        assert "Usage: python crawler.py domain" in captured.out
        assert "Example: python crawler.py www.example.com" in captured.out

def test_main_with_domain(tmp_path, monkeypatch):
    """Test main function with a valid domain argument"""
    # Create a mock WebsiteCrawler
    mock_crawler = MagicMock()
    mock_crawler.base_url = 'https://example.com'
    mock_crawler.visited_urls = set(['https://example.com'])
    
    # Patch the WebsiteCrawler class
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler) as mock_class:
        # Set up command line argument
        with patch.object(sys, 'argv', ['crawler.py', 'example.com']):
            # Freeze datetime to a known value
            frozen_time = datetime(2024, 1, 1, 12, 0)
            with patch('src.crawler.datetime') as mock_datetime:
                mock_datetime.now.return_value = frozen_time
                
                # Run main function
                main()
                
                # Verify WebsiteCrawler was created with correct domain
                mock_class.assert_called_once_with('example.com')
                
                # Verify crawler methods were called
                mock_crawler.crawl_page.assert_called_once_with(mock_crawler.base_url)
                mock_crawler.save_results.assert_called_once()
                
                # Verify the filename format
                expected_filename = f"example.com_2024-01-01T1200.csv"
                actual_filename = mock_crawler.save_results.call_args[0][0]
                assert os.path.basename(actual_filename) == expected_filename

def test_main_with_crawler_error(capsys):
    """Test main function when crawler encounters an error"""
    # Create a mock WebsiteCrawler that raises an exception
    mock_crawler = MagicMock()
    mock_crawler.crawl_page.side_effect = Exception("Network error")
    
    # Patch the WebsiteCrawler class
    with patch('src.crawler.WebsiteCrawler', return_value=mock_crawler):
        # Set up command line argument
        with patch.object(sys, 'argv', ['crawler.py', 'example.com']):
            # Run main function
            with pytest.raises(Exception) as exc_info:
                main()
            
            assert str(exc_info.value) == "Network error"
            
            # Verify save_results was not called after error
            mock_crawler.save_results.assert_not_called()
