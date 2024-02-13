import os
import base64
import logging
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

class GmailAttachmentDownloader:
    def __init__(self, credentials_file='credentials.json'):
        self.credentials = Credentials.from_authorized_user_file(credentials_file)
        self.service = build('gmail', 'v1', credentials=self.credentials)
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(filename='gmail_attachment_downloader.log', level=logging.INFO)

    def list_messages(self, query):
        self.logger.info("Listing messages...")
        try:
            result = self.service.users().messages().list(userId='me', q=query).execute()
            messages = result.get('messages', [])
            return messages
        except Exception as e:
            self.logger.error(f"Failed to list messages: {e}")
            return []

    def get_message(self, message_id):
        self.logger.info(f"Getting message {message_id}...")
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            return message
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            return None

    def get_attachments(self, message_id, sender_name, dry_run=False):
        self.logger.info(f"Getting attachments for message {message_id} from sender {sender_name}...")
        try:
            message = self.get_message(message_id)
            if not message:
                self.logger.warning(f"Message {message_id} not found.")
                return
            parts = message['payload']['parts']

            if not os.path.exists(sender_name):
                os.makedirs(sender_name)

            for part in parts:
                if part['filename']:
                    attachment_id = part['body']['attachmentId']
                    attachment = self.service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
                    file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                    path = os.path.join(sender_name, part['filename'])

                    if not dry_run:
                        with open(path, 'wb') as f:
                            f.write(file_data)
                            self.logger.info(f"Downloaded attachment: {part['filename']}")
                    else:
                        self.logger.info(f"Would download attachment: {part['filename']}")
        except Exception as e:
            self.logger.error(f"Failed to get attachments for message {message_id}: {e}")

    def search_and_download_attachments(self, query, dry_run=False):
        self.logger.info(f"Searching for messages with query: {query}...")
        try:
            messages = self.list_messages(query)
            for message in messages:
                message_id = message['id']
                sender = self.get_message(message_id)['payload']['headers']
                sender_name = next(item['value'] for item in sender if item['name'] == 'From')
                sender_name = sender_name.split('<')[0].strip()  # Remove email address if present
                self.get_attachments(message_id, sender_name, dry_run)
        except Exception as e:
            self.logger.error(f"Failed to search and download attachments: {e}")

if __name__ == '__main__':
    gmail_downloader = GmailAttachmentDownloader()
    search_query = input("Enter your search query: ")
    dry_run_input = input("Do you want to perform a dry run? (y/n): ")
    dry_run = True if dry_run_input.lower() == 'y' else False
    gmail_downloader.search_and_download_attachments(search_query, dry_run)
