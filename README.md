# Gmail Attachment Downloader
Gmail Attachment Downloader is a Python script that allows you to search Gmail for emails with attachments and download the attachments, organizing them into folders named after the sender.

Author: Ben Lacey [Author Website](https://benlacey.co.uk)

Date: February 2024

---

## Installation
1. Clone or download this repository to your local machine.
2. Make sure you have Python 3 installed on your system.
3. Install the required Python packages by running the following command in your terminal:

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

4. Create a Google Cloud project and enable the Gmail API. Follow the instructions [here](https://developers.google.com/gmail/api/quickstart/python) to set up your project and obtain the `credentials.json` file.

5. Place the `credentials.json` file in the same directory as the script.

## Usage Examples

1. Open a terminal and navigate to the directory containing the script.
2. Run the script by executing the following command:
3. Enter your search query when prompted. This can be any search query you would normally use in Gmail.
4. Choose whether you want to perform a dry run or not. If you choose a dry run, the script will show what files would be downloaded without actually downloading them.
5. The script will search Gmail for emails matching the query, download attachments, and organize them into folders named after the sender.

Note: Ensure that you have granted the necessary permissions to access your Gmail account.

## Config File
```json
{
  "output_folder": "",
  "upload": [
    "name": "Google Drive",
    "output_folder_id": ""
  ]
}
```
