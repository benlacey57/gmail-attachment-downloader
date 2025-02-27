import os
import base64
import logging
import yaml
import csv
import time
from datetime import datetime
from functools import wraps
from typing import List, Dict, Any, Optional, Tuple
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build


def timing_decorator(logger):
    """Decorator to measure and log function execution time."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            end_time = time.time()
            execution_time = end_time - start_time
            logger.info(f"Function {func.__name__} executed in {execution_time:.4f} seconds")
            return result
        return wrapper
    return decorator


class ConfigManager:
    """Handles loading and accessing configuration settings."""
    
    def __init__(self, config_file: str = 'config.yaml'):
        self.config_file = config_file
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_file, 'r') as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            # Create default configuration if file doesn't exist
            default_config = {
                'gmail': {'credentials_file': 'credentials.json'},
                'logging': {
                    'system_log': 'logs/system.log',
                    'search_log': 'logs/search.log',
                    'log_level': 'INFO'
                },
                'downloads': {
                    'output_directory': 'downloads',
                    'organize_by_sender': True
                },
                'csv_record': {
                    'enabled': True,
                    'filename': 'attachment_records.csv'
                }
            }
            
            # Create directory for config file if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Save default configuration
            with open(self.config_file, 'w') as file:
                yaml.dump(default_config, file)
            
            return default_config
    
    def get(self, section: str, key: str) -> Any:
        """Get configuration value."""
        try:
            return self.config[section][key]
        except KeyError:
            raise KeyError(f"Configuration key '{section}.{key}' not found")


class LoggerFactory:
    """Creates and configures loggers."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.loggers = {}
        self._setup_loggers()
    
    def _setup_loggers(self) -> None:
        """Set up system and search loggers."""
        log_level = getattr(logging, self.config_manager.get('logging', 'log_level'))
        
        # Create log directory if it doesn't exist
        log_dir = os.path.dirname(self.config_manager.get('logging', 'system_log'))
        os.makedirs(log_dir, exist_ok=True)
        
        # Configure system logger
        system_logger = logging.getLogger('system')
        system_logger.setLevel(log_level)
        
        system_handler = logging.FileHandler(self.config_manager.get('logging', 'system_log'))
        system_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        system_handler.setFormatter(system_formatter)
        
        system_logger.addHandler(system_handler)
        self.loggers['system'] = system_logger
        
        # Configure search logger
        search_logger = logging.getLogger('search')
        search_logger.setLevel(log_level)
        
        search_handler = logging.FileHandler(self.config_manager.get('logging', 'search_log'))
        search_formatter = logging.Formatter('%(asctime)s - %(message)s')
        search_handler.setFormatter(search_formatter)
        
        search_logger.addHandler(search_handler)
        self.loggers['search'] = search_logger
    
    def get_logger(self, name: str) -> logging.Logger:
        """Get logger by name."""
        if name not in self.loggers:
            raise ValueError(f"Logger '{name}' not found")
        return self.loggers[name]


class CSVRecordManager:
    """Manages CSV records of downloaded attachments."""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.enabled = config_manager.get('csv_record', 'enabled')
        self.csv_file = config_manager.get('csv_record', 'filename')
        
        if self.enabled:
            self._initialize_csv()
    
    def _initialize_csv(self) -> None:
        """Initialize CSV file with headers if it doesn't exist."""
        if not os.path.exists(self.csv_file):
            with open(self.csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([
                    'timestamp', 'message_id', 'sender', 'sender_email',
                    'subject', 'attachment_name', 'original_filename',
                    'file_size', 'file_type', 'download_path'
                ])
    
    def record_attachment(self, 
                          timestamp: str, 
                          message_id: str, 
                          sender: str, 
                          sender_email: str,
                          subject: str, 
                          attachment_name: str, 
                          original_filename: str,
                          file_size: int, 
                          file_type: str, 
                          download_path: str) -> None:
        """Record downloaded attachment information to CSV."""
        if not self.enabled:
            return
        
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([
                timestamp, message_id, sender, sender_email, 
                subject, attachment_name, original_filename,
                file_size, file_type, download_path
            ])


class EmailService:
    """Handles Gmail API interactions."""
    
    def __init__(self, config_manager: ConfigManager, system_logger: logging.Logger):
        self.config_manager = config_manager
        self.logger = system_logger
        self._initialize_service()
    
    def _initialize_service(self) -> None:
        """Initialize Gmail API service."""
        try:
            credentials_file = self.config_manager.get('gmail', 'credentials_file')
            credentials = Credentials.from_authorized_user_file(credentials_file)
            self.service = build('gmail', 'v1', credentials=credentials)
            self.logger.info("Gmail API service initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail API service: {e}")
            raise
    
    @timing_decorator(logging.getLogger('system'))
    def list_messages(self, query: str) -> List[Dict[str, str]]:
        """List messages matching the query."""
        try:
            result = self.service.users().messages().list(userId='me', q=query).execute()
            messages = result.get('messages', [])
            self.logger.info(f"Found {len(messages)} messages matching query: '{query}'")
            return messages
        except Exception as e:
            self.logger.error(f"Failed to list messages: {e}")
            return []
    
    @timing_decorator(logging.getLogger('system'))
    def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message details by ID."""
        try:
            message = self.service.users().messages().get(userId='me', id=message_id).execute()
            return message
        except Exception as e:
            self.logger.error(f"Failed to get message {message_id}: {e}")
            return None
    
    @timing_decorator(logging.getLogger('system'))
    def get_attachment(self, message_id: str, attachment_id: str) -> Optional[bytes]:
        """Get attachment data by message ID and attachment ID."""
        try:
            attachment = self.service.users().messages().attachments().get(
                userId='me', messageId=message_id, id=attachment_id
            ).execute()
            file_data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))
            return file_data
        except Exception as e:
            self.logger.error(f"Failed to get attachment {attachment_id} from message {message_id}: {e}")
            return None


class MessageProcessor:
    """Processes email messages and extracts information."""
    
    def __init__(self, system_logger: logging.Logger):
        self.logger = system_logger
    
    def extract_sender_info(self, message: Dict[str, Any]) -> Tuple[str, str]:
        """Extract sender name and email from message headers."""
        try:
            headers = message['payload']['headers']
            from_header = next((item for item in headers if item['name'] == 'From'), None)
            
            if not from_header:
                return "Unknown", "unknown@example.com"
            
            from_value = from_header['value']
            
            # Try to extract email and name
            if '<' in from_value and '>' in from_value:
                name_part = from_value.split('<')[0].strip()
                email_part = from_value.split('<')[1].split('>')[0].strip()
                
                # If name part is empty, use email part as name
                if not name_part:
                    name_part = email_part.split('@')[0]
            else:
                # Assume the value is just an email
                email_part = from_value.strip()
                name_part = email_part.split('@')[0]
            
            return name_part, email_part
        except Exception as e:
            self.logger.error(f"Failed to extract sender info: {e}")
            return "Unknown", "unknown@example.com"
    
    def extract_subject(self, message: Dict[str, Any]) -> str:
        """Extract subject from message headers."""
        try:
            headers = message['payload']['headers']
            subject_header = next((item for item in headers if item['name'] == 'Subject'), None)
            
            if not subject_header:
                return "No Subject"
            
            return subject_header['value']
        except Exception as e:
            self.logger.error(f"Failed to extract subject: {e}")
            return "No Subject"
    
    def has_attachments(self, message: Dict[str, Any]) -> bool:
        """Check if message has attachments."""
        try:
            if 'parts' not in message['payload']:
                return False
            
            for part in message['payload']['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    return True
            
            return False
        except Exception as e:
            self.logger.error(f"Failed to check for attachments: {e}")
            return False
    
    def get_attachment_parts(self, message: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all attachment parts from message."""
        try:
            if 'parts' not in message['payload']:
                return []
            
            attachment_parts = []
            for part in message['payload']['parts']:
                if part.get('filename') and part.get('body', {}).get('attachmentId'):
                    attachment_parts.append(part)
            
            return attachment_parts
        except Exception as e:
            self.logger.error(f"Failed to get attachment parts: {e}")
            return []

    def filter_attachments_by_type(self, attachment_parts: List[Dict[str, Any]], 
                                  file_types: List[str]) -> List[Dict[str, Any]]:
        """Filter attachments by file type."""
        if not file_types:
            return attachment_parts
        
        filtered_parts = []
        for part in attachment_parts:
            filename = part.get('filename', '')
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext in file_types:
                filtered_parts.append(part)
        
        return filtered_parts


class AttachmentHandler:
    """Handles downloading and organizing attachments."""
    
    def __init__(self, config_manager: ConfigManager, system_logger: logging.Logger):
        self.config_manager = config_manager
        self.logger = system_logger
        self.base_dir = config_manager.get('downloads', 'output_directory')
        self.organize_by_sender = config_manager.get('downloads', 'organize_by_sender')
        
        # Create base directory if it doesn't exist
        os.makedirs(self.base_dir, exist_ok=True)
    
    def _generate_sql_timestamp(self) -> str:
        """Generate SQL-format timestamp (YYYY-MM-DD HH:MM:SS)."""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def _get_file_type(self, filename: str) -> str:
        """Get file type/extension from filename."""
        return os.path.splitext(filename)[1].lower()
    
    def _get_file_size(self, file_data: bytes) -> int:
        """Get file size in bytes."""
        return len(file_data)
    
    def _prepare_output_directory(self, sender_name: str) -> str:
        """Prepare output directory based on sender name."""
        if self.organize_by_sender:
            # Clean up sender name for use as directory name
            clean_sender = "".join(c if c.isalnum() or c in [' ', '.', '-'] else '_' for c in sender_name)
            clean_sender = clean_sender.strip()
            
            output_dir = os.path.join(self.base_dir, clean_sender)
        else:
            output_dir = self.base_dir
        
        os.makedirs(output_dir, exist_ok=True)
        return output_dir
    
    def _rename_file(self, original_filename: str) -> Tuple[str, str]:
        """Rename file with SQL timestamp prefix."""
        timestamp = self._generate_sql_timestamp()
        new_filename = f"{timestamp}_{original_filename}"
        return new_filename, timestamp
    
    @timing_decorator(logging.getLogger('system'))
    def save_attachment(self, 
                        file_data: bytes, 
                        original_filename: str, 
                        sender_name: str) -> Tuple[str, str, int, str]:
        """Save attachment with proper naming and organization."""
        output_dir = self._prepare_output_directory(sender_name)
        new_filename, timestamp = self._rename_file(original_filename)
        file_path = os.path.join(output_dir, new_filename)
        
        file_type = self._get_file_type(original_filename)
        file_size = self._get_file_size(file_data)
        
        with open(file_path, 'wb') as f:
            f.write(file_data)
            self.logger.info(f"Saved attachment: {new_filename} ({file_size} bytes)")
        
        return new_filename, timestamp, file_size, file_path


class GmailAttachmentDownloader:
    """Main class to coordinate Gmail attachment downloading."""
    
    def __init__(self, config_file: str = 'config.yaml'):
        # Initialize configuration
        self.config_manager = ConfigManager(config_file)
        
        # Initialize loggers
        self.logger_factory = LoggerFactory(self.config_manager)
        self.system_logger = self.logger_factory.get_logger('system')
        self.search_logger = self.logger_factory.get_logger('search')
        
        # Initialize components
        self.email_service = EmailService(self.config_manager, self.system_logger)
        self.message_processor = MessageProcessor(self.system_logger)
        self.attachment_handler = AttachmentHandler(self.config_manager, self.system_logger)
        self.csv_manager = CSVRecordManager(self.config_manager)
        
        self.system_logger.info("GmailAttachmentDownloader initialized")
    
    def _parse_file_types(self, file_types_str: str) -> List[str]:
        """Parse file types string into a list of file extensions."""
        if not file_types_str:
            return []
        
        file_types = []
        for file_type in file_types_str.split(','):
            file_type = file_type.strip().lower()
            if not file_type.startswith('.'):
                file_type = '.' + file_type
            file_types.append(file_type)
        
        return file_types
    
    @timing_decorator(logging.getLogger('system'))
    def search_and_download_attachments(self, 
                                        query: str, 
                                        file_types_str: str = "", 
                                        dry_run: bool = False) -> None:
        """Search for messages and download their attachments."""
        try:
            start_time = time.time()
            self.system_logger.info(f"Starting search and download with query: '{query}'")
            
            # Log search parameters
            self.search_logger.info(
                f"Search initiated - Query: '{query}', File types: '{file_types_str}', Dry run: {dry_run}"
            )
            
            # Parse file types for filtering
            file_types = self._parse_file_types(file_types_str)
            if file_types:
                self.system_logger.info(f"Filtering attachments by types: {file_types}")
            
            # List messages matching the query
            messages = self.email_service.list_messages(query)
            self.search_logger.info(f"Found {len(messages)} messages")
            
            # Process each message
            processed_attachments = 0
            for message_data in messages:
                message_id = message_data['id']
                message = self.email_service.get_message(message_id)
                
                if not message:
                    continue
                
                # Extract message information
                sender_name, sender_email = self.message_processor.extract_sender_info(message)
                subject = self.message_processor.extract_subject(message)
                
                # Check if message has attachments
                if not self.message_processor.has_attachments(message):
                    self.system_logger.info(f"Message {message_id} has no attachments")
                    continue
                
                # Get and filter attachment parts
                attachment_parts = self.message_processor.get_attachment_parts(message)
                if file_types:
                    attachment_parts = self.message_processor.filter_attachments_by_type(
                        attachment_parts, file_types
                    )
                
                if not attachment_parts:
                    self.system_logger.info(
                        f"Message {message_id} has no attachments matching file types: {file_types}"
                    )
                    continue
                
                # Process each attachment
                for part in attachment_parts:
                    original_filename = part['filename']
                    attachment_id = part['body']['attachmentId']
                    
                    # Skip if dry run
                    if dry_run:
                        self.system_logger.info(
                            f"[DRY RUN] Would download attachment: {original_filename} "
                            f"from {sender_name} <{sender_email}>"
                        )
                        continue
                    
                    # Download attachment
                    file_data = self.email_service.get_attachment(message_id, attachment_id)
                    if not file_data:
                        continue
                    
            