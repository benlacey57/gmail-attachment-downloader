# Gmail Attachment Downloader

A tool to search Gmail for specific attachments, download them, and organise them by sender. This application provides comprehensive logging, and offers flexible configuration options.

Author: Ben Lacey [Author Website](https://benlacey.co.uk)

Date: February 2025

---

## Table of Contents
- [Requirements](#requirements)
- [Setup](#setup)
  - [Google API Credentials](#google-api-credentials)
  - [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Command-Line Arguments](#command-line-arguments)
- [Logs and Reports](#logs-and-reports)
- [Example Workflows](#example-workflows)

## Requirements

Create a `requirements.txt` file with the following content:

```
google-api-python-client>=2.0.0
google-auth-oauthlib>=0.4.0
google-auth-httplib2>=0.1.0
pyyaml>=6.0
typing>=3.7.4
```

Install the dependencies with:

```bash
pip install -r requirements.txt
```

## Setup

### Google API Credentials

Before using this tool, you need to obtain a `credentials.json` file from Google:

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Note your project ID

2. **Enable the Gmail API**:
   - In your project, navigate to "APIs & Services" > "Library"
   - Search for "Gmail API" and select it
   - Click "Enable"

3. **Create OAuth Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop application" as the application type
   - Name your OAuth client
   - Click "Create"

4. **Download Credentials**:
   - After creation, you'll see a download button (JSON)
   - Download and save the file as `credentials.json` in your project directory

5. **First Authentication**:
   - The first time you run the script, it will open a browser window
   - Log in with your Google account and grant the requested permissions
   - This will create a token that's stored for future use

### Installation

1. Clone or download this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Place your `credentials.json` file in the project directory

## Configuration

The application uses a YAML configuration file. If not present, a default one will be created automatically. You can specify a custom config file location with the `--config` argument.

### Default Configuration

```yaml
gmail:
  credentials_file: credentials.json

logging:
  system_log: logs/system.log
  search_log: logs/search.log
  log_level: INFO

downloads:
  output_directory: downloads
  organize_by_sender: true

csv_record:
  enabled: true
  filename: attachment_records.csv

search:
  query: has:attachment
  file_types: .pdf,.doc,.docx,.xls,.xlsx
  dry_run: false
```

### Configuration Options

#### Gmail Section
- `credentials_file`: Path to your Google API credentials file

#### Logging Section
- `system_log`: Path to system log file (records function calls and durations)
- `search_log`: Path to search log file (records search queries and results)
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

#### Downloads Section
- `output_directory`: Base directory for downloaded attachments
- `organize_by_sender`: Whether to create subdirectories by sender name

#### CSV Record Section
- `enabled`: Whether to keep a CSV record of downloaded files
- `filename`: Path to the CSV record file

#### Search Section
- `query`: Default Gmail search query
- `file_types`: Comma-separated list of file extensions to filter (.pdf,.doc,etc.)
- `dry_run`: If true, performs a simulation without downloading files

## Usage

Basic usage:

```bash
python main.py
```

This will use the values from your config file. For more control, use command-line arguments.

## Command-Line Arguments

The script supports several command-line arguments that override config file settings:

```
--config, -c    Path to configuration file (default: config.yaml)
--query, -q     Search query to override configuration
--file-types, -t File types to filter (comma-separated, e.g., .pdf,.doc)
--dry-run, -d   Perform a dry run without downloading attachments
```

### Examples

Search for PDF attachments from a specific sender:
```bash
python main.py --query "from:example@gmail.com has:attachment" --file-types ".pdf"
```

Perform a dry run to see what would be downloaded:
```bash
python main.py --query "subject:invoice has:attachment" --dry-run
```

Use a custom configuration file:
```bash
python main.py --config my_custom_config.yaml
```

## Logs and Reports

The application generates several files to help track activity:

1. **System Log** (`logs/system.log`):
   - Records function calls with execution times
   - Tracks errors and system events

2. **Search Log** (`logs/search.log`):
   - Records search queries and criteria
   - Logs number of results and processing time

3. **CSV Record** (`attachment_records.csv`):
   - Detailed information about each downloaded attachment
   - Includes message details, file information, and storage paths

## Example Workflows

### Downloading Invoice PDFs

Config:
```yaml
search:
  query: "subject:invoice has:attachment"
  file_types: .pdf
  dry_run: false
```

Command:
```bash
python main.py
```

### Finding Documents from a Specific Sender

Config:
```yaml
search:
  query: "from:supplier@example.com has:attachment"
  file_types: .doc,.docx,.pdf
  dry_run: false
```

Command:
```bash
python main.py
```

### Backing up All Attachments from Last Month

Command:
```bash
python main.py --query "after:2023/01/01 before:2023/02/01 has:attachment"
```

---

This tool provides a flexible and powerful way to manage email attachments while maintaining good organization and record-keeping practices. For questions or issues, please open an issue in the repository.