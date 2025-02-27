import argparse
import yaml
from gmail_attachment_downloader import GmailAttachmentDownloader

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Gmail Attachment Downloader')
    
    parser.add_argument('--config', '-c', default='config.yaml',
                      help='Path to configuration file')
    parser.add_argument('--query', '-q',
                      help='Search query to override configuration')
    parser.add_argument('--file-types', '-t',
                      help='File types to filter (comma-separated, e.g., .pdf,.doc)')
    parser.add_argument('--dry-run', '-d', action='store_true',
                      help='Perform a dry run without downloading attachments')
    
    return parser.parse_args()

def main():
    """Main function to run the application."""
    args = parse_arguments()
    
    # Load configuration
    try:
        with open(args.config, 'r') as file:
            config = yaml.safe_load(file)
    except FileNotFoundError:
        print(f"Configuration file not found: {args.config}")
        return
    
    # Initialize downloader
    gmail_downloader = GmailAttachmentDownloader(args.config)
    
    # Get search parameters from config or command line arguments
    search_query = args.query if args.query else config.get('search', {}).get('query', '')
    file_types = args.file_types if args.file_types else config.get('search', {}).get('file_types', '')
    dry_run = args.dry_run if args.dry_run else config.get('search', {}).get('dry_run', False)
    
    if not search_query:
        print("No search query provided. Please specify a query in config file or via --query argument.")
        return
    
    # Perform search and download
    gmail_downloader.search_and_download_attachments(search_query, file_types, dry_run)

if __name__ == '__main__':
    main()