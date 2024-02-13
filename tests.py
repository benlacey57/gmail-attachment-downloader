import os
import unittest
from unittest.mock import MagicMock, patch
from gmail_attachment_downloader import list_messages, get_message, get_attachments, search_and_download_attachments

class TestGmailAttachmentDownloader(unittest.TestCase):
    
    @patch('gmail_attachment_downloader.service')
    def test_list_messages(self, mock_service):
        mock_service.users().messages().list().execute.return_value = {'messages': [{'id': '123'}, {'id': '456'}]}
        result = list_messages('test_query')
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['id'], '123')
        self.assertEqual(result[1]['id'], '456')

    @patch('gmail_attachment_downloader.service')
    def test_get_message(self, mock_service):
        mock_service.users().messages().get().execute.return_value = {'id': '123', 'payload': {'headers': [{'name': 'From', 'value': 'sender@example.com'}]}}
        result = get_message('test_message_id')
        self.assertEqual(result['id'], '123')
        self.assertEqual(result['payload']['headers'][0]['value'], 'sender@example.com')

    @patch('gmail_attachment_downloader.service')
    def test_get_attachments(self, mock_service):
        message_data = {'payload': {'parts': [{'filename': 'file1.txt', 'body': {'attachmentId': '123', 'data': 'base64_data'}}]}}
        mock_get_message = MagicMock(return_value={'payload': {'parts': [{'filename': 'file1.txt', 'body': {'attachmentId': '123', 'data': 'base64_data'}}]}})
        mock_service.users().messages().get = mock_get_message
        with patch('builtins.open', MagicMock()) as mock_open:
            get_attachments('test_message_id', 'sender', dry_run=False)
            mock_open.assert_called_once()
        
    @patch('gmail_attachment_downloader.list_messages')
    @patch('gmail_attachment_downloader.get_message')
    @patch('gmail_attachment_downloader.get_attachments')
    def test_search_and_download_attachments(self, mock_get_attachments, mock_get_message, mock_list_messages):
        mock_list_messages.return_value = [{'id': '123'}, {'id': '456'}]
        mock_get_message.return_value = {'payload': {'headers': [{'name': 'From', 'value': 'sender@example.com'}]}}
        search_and_download_attachments('test_query', dry_run=False)
        self.assertEqual(mock_get_message.call_count, 2)
        self.assertEqual(mock_get_attachments.call_count, 2)

if __name__ == '__main__':
    unittest.main()
  
