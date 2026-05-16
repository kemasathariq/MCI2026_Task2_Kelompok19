import http.client
import unittest
from unittest.mock import Mock, patch, MagicMock


def check_server_status():
    """Check the status of jsonplaceholder.typicode.com/posts"""
    try:
        connection = http.client.HTTPSConnection('jsonplaceholder.typicode.com')
        connection.request('GET', '/posts')
        response = connection.getresponse()
        status = response.status
        connection.close()
        
        if status == 200:
            return "Server is up!"
        else:
            return "Server is down!"
    except Exception:
        return "Server is down!"


class TestCheckServerStatus(unittest.TestCase):
    """Unit tests for check_server_status function"""
    
    @patch('http.client.HTTPSConnection')
    def test_server_up(self, mock_connection_class):
        """Test when server returns status 200"""
        # Setup mock
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection
        
        mock_response = Mock()
        mock_response.status = 200
        mock_connection.getresponse.return_value = mock_response
        
        # Call function
        result = check_server_status()
        
        # Verify calls
        print(f"connection called with: {mock_connection_class.call_args}")
        print(f"request called with: {mock_connection.request.call_args}")
        print(f"connection closed: {mock_connection.close.call_args}")
        print(f"test attribute passed: {result} is equal to Server is up!")
        
        # Assert
        self.assertEqual(result, "Server is up!")
        mock_connection_class.assert_called_once_with('jsonplaceholder.typicode.com')
        mock_connection.request.assert_called_once_with('GET', '/posts')
        mock_connection.close.assert_called_once()
    
    @patch('http.client.HTTPSConnection')
    def test_server_down(self, mock_connection_class):
        """Test when server returns status other than 200"""
        # Setup mock
        mock_connection = MagicMock()
        mock_connection_class.return_value = mock_connection
        
        mock_response = Mock()
        mock_response.status = 500
        mock_connection.getresponse.return_value = mock_response
        
        # Call function
        result = check_server_status()
        
        # Verify calls
        print(f"connection called with: {mock_connection_class.call_args}")
        print(f"request called with: {mock_connection.request.call_args}")
        print(f"connection closed: {mock_connection.close.call_args}")
        print(f"test attribute passed: {result} is equal to Server is down!")
        
        # Assert
        self.assertEqual(result, "Server is down!")
        mock_connection_class.assert_called_once_with('jsonplaceholder.typicode.com')
        mock_connection.request.assert_called_once_with('GET', '/posts')
        mock_connection.close.assert_called_once()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Run with unit tests
        unittest.main(argv=[''], exit=False)
    else:
        # Run without unit tests
        print(check_server_status())
