import os
import base64
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# Set up Google API credentials
credentials = Credentials.from_authorized_user_file('credentials.json')
service = build('gmail', 'v1', credentials=credentials)

def list_messages(query):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = result.get('messages', [])
    return messages

def get_message(message_id):
    message = service.users().messages().get(userId='me', id=message_id).execute()
    return message

def get_attachments(message_id, sender_name, dry_run=False):
    message = get_message(message_id)
    parts = message['payload']['parts']

    if not os.path.exists(sender_name):
        os.makedirs(sender_name)

    for part in parts:
        if part['filename']:
            attachment_id = part['body']['attachmentId']
            attachment = service.users().messages().attachments().get(userId='me', messageId=message_id, id=attachment_id).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

            path = os.path.join(sender_name, part['filename'])

            if not dry_run:
                with open(path, 'wb') as f:
                    f.write(file_data)
                    print(f"Downloaded attachment: {part['filename']}")
            else:
                print(f"Download attachment: {part['filename']}")

def search_and_download_attachments(query, dry_run=False):
    messages = list_messages(query)
    for message in messages:
        message_id = message['id']
        sender = get_message(message_id)['payload']['headers']
        sender_name = next(item['value'] for item in sender if item['name'] == 'From')
        sender_name = sender_name.split('<')[0].strip()  # Remove email address if present
        get_attachments(message_id, sender_name, dry_run)

if __name__ == '__main__':
    search_query = input("Search Emails: ")
    dry_run_input = input("Do you want to perform a dry run? (y/n): ")
    dry_run = True if dry_run_input.lower() == 'y' else False
    search_and_download_attachments(search_query, dry_run)
  
