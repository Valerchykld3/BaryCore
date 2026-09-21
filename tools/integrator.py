import os
import io
import base64
from email.message import EmailMessage
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive', 'https://mail.google.com/']

def _get_google_credentials():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def _get_drive_service():
    return build('drive', 'v3', credentials=_get_google_credentials())

def _get_gmail_service():
    return build('gmail', 'v1', credentials=_get_google_credentials())

# Tools for DGDB

def search_drive(query: str, limit: int = 10) -> str:
    safe_limit = min(limit, 50) 
    print(f"Searching Drive for: {query} (limit: {safe_limit})")
    
    try:
        service = _get_drive_service()
        results = service.files().list(
            q=f"name contains '{query}'", 
            pageSize=safe_limit, 
            fields="files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        if not items:
            return f"No files found matching '{query}' on Google Drive."
            
        res = f"Found {len(items)} files:\n"
        for item in items:
            res += f"- {item['name']} (ID: {item['id']})\n"
        return res
    except Exception as e:
        return f"Drive search error: {str(e)}"

def list_drive_directory(folder_id: str = "root", limit: int = 50) -> str:
    safe_limit = min(limit, 100)
    print(f"Listing Drive directory: {folder_id} (limit: {safe_limit})")
    
    try:
        service = _get_drive_service()
        
        results = service.files().list(
            q=f"'{folder_id}' in parents and trashed=false",
            pageSize=safe_limit,
            fields="files(id, name, mimeType)"
        ).execute()
        
        items = results.get('files', [])
        if not items:
            return f"Directory '{folder_id}' is empty or not found."
            
        res = f"Contents of '{folder_id}' (Limit: {safe_limit}):\n"
        for item in items:
            is_dir = "Folder" if item.get('mimeType') == 'application/vnd.google-apps.folder' else "File"
            res += f"- [{is_dir}] {item['name']} (ID: {item['id']})\n"
            
        return res
    except Exception as e:
        return f"List directory error: {str(e)}"

def read_drive_file(file_id: str) -> str:
    print(f"Reading Drive file ID: {file_id}...")
    try:
        service = _get_drive_service()
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            
        content = fh.getvalue().decode('utf-8')
        snippet = content[:100]
        
        if len(content) > 100:
            snippet += "\n... (context economy)"
            
        return f"File content:\n{snippet}"
    except Exception as e:
        return f"Read error: {str(e)}"

def create_drive_folder(folder_name: str, parent_folder_id: str = None) -> str:
    print(f"Creating Drive folder: {folder_name}")
    try:
        service = _get_drive_service()
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
            
        file = service.files().create(body=file_metadata, fields='id').execute()
        return f"Success: Folder '{folder_name}' created with ID: {file.get('id')}"
    except Exception as e:
        return f"Create folder error: {str(e)}"

def batch_move_drive_items(file_ids: list, new_folder_id: str) -> str:
    print(f"Batch moving {len(file_ids)} items to {new_folder_id}")
    try:
        service = _get_drive_service()
        moved_count = 0
        for file_id in file_ids:
            file = service.files().get(fileId=file_id, fields='parents').execute()
            previous_parents = ",".join(file.get('parents', []))
            service.files().update(
                fileId=file_id,
                addParents=new_folder_id,
                removeParents=previous_parents,
                fields='id, parents'
            ).execute()
            moved_count += 1
        return f"Success: Moved {moved_count} items to folder {new_folder_id}"
    except Exception as e:
        return f"Batch move error: {str(e)}"

def create_drive_file(filename: str, content: str = "", as_google_doc: bool = False, parent_folder_id: str = None) -> str:
    print(f"Creating Drive file '{filename}'...")
    try:
        service = _get_drive_service()
        
        target_mime = 'application/vnd.google-apps.document' if as_google_doc else 'text/plain'
        
        file_metadata = {
            'name': filename, 
            'mimeType': target_mime
        }
        if parent_folder_id:
            file_metadata['parents'] = [parent_folder_id]
            
        media = MediaIoBaseUpload(
            io.BytesIO(content.encode('utf-8')), 
            mimetype='text/plain',
            resumable=True
        )
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return f"Success: File '{filename}' created with ID: {file.get('id')}"
    except Exception as e:
        return f"Create error: {str(e)}"

def copy_drive_item(file_id: str, new_filename: str = None, new_parent_id: str = None) -> str:
    print(f"Copying Drive item ID: {file_id}...")
    try:
        service = _get_drive_service()
        copied_file_metadata = {}
        
        if new_filename:
            copied_file_metadata['name'] = new_filename
        if new_parent_id:
            copied_file_metadata['parents'] = [new_parent_id]

        file = service.files().copy(
            fileId=file_id, 
            body=copied_file_metadata, 
            fields='id, name'
        ).execute()
        return f"Success: File copied as '{file.get('name')}' with new ID: {file.get('id')}"
    except Exception as e:
        return f"Copy error: {str(e)}"

def move_drive_item(file_id: str, new_folder_id: str) -> str:
    print(f"Moving item {file_id} to folder {new_folder_id}")
    try:
        service = _get_drive_service()
        file = service.files().get(fileId=file_id, fields='parents').execute()
        previous_parents = ",".join(file.get('parents', []))
        
        file = service.files().update(
            fileId=file_id, 
            addParents=new_folder_id,
            removeParents=previous_parents,
            fields='id, parents'
        ).execute()
        return f"Success: Moved item {file_id} to new folder {new_folder_id}"
    except Exception as e:
        return f"Move error: {str(e)}"

def delete_drive_item(file_id: str) -> str:
    print(f"Deleting Drive item: {file_id}")
    try:
        service = _get_drive_service()
        service.files().delete(fileId=file_id).execute()
        return f"Success: Item {file_id} successfully deleted."
    except Exception as e:
        return f"Delete error: {str(e)}"

def get_drive_item_info(file_id: str) -> str:
    print(f"Getting info for Drive item: {file_id}")
    try:
        service = _get_drive_service()
        file = service.files().get(
            fileId=file_id, 
            fields='id, name, mimeType, size, createdTime, modifiedTime'
        ).execute()
        
        size_mb = int(file.get('size', 0)) / (1024 * 1024) if 'size' in file else 0
        return (f"Info for '{file.get('name')}':\n"
                f"ID: {file.get('id')}\n"
                f"Type: {file.get('mimeType')}\n"
                f"Size: {size_mb:.2f} MB\n"
                f"Created: {file.get('createdTime')}\n"
                f"Modified: {file.get('modifiedTime')}")
    except Exception as e:
        return f"Info error: {str(e)}"

def upload_to_drive(local_path: str, filename_on_drive: str) -> str:
    print(f"Uploading {local_path} to Drive as '{filename_on_drive}'")
    try:
        service = _get_drive_service()
        file_metadata = {'name': filename_on_drive}
        media = MediaFileUpload(local_path, resumable=True)
        
        file = service.files().create(
            body=file_metadata, 
            media_body=media, 
            fields='id'
        ).execute()
        
        return f"Success: File uploaded to Google Drive. ID: {file.get('id')}"
    except FileNotFoundError:
        return f"Error: Local file '{local_path}' not found."
    except Exception as e:
        return f"Upload error: {str(e)}"

def upload_folder_to_drive(local_folder_path: str, parent_drive_folder_id: str = None) -> str:
    print(f"Uploading all files recursively from {local_folder_path} to Drive...")
    try:
        if not os.path.isdir(local_folder_path):
            return f"Error: '{local_folder_path}' is not a valid directory."
            
        service = _get_drive_service()
        uploaded_files = []
        
        folder_mapping = {local_folder_path: parent_drive_folder_id}
        
        for root, dirs, files in os.walk(local_folder_path):
            current_parent_id = folder_mapping.get(root)
            
            for dir_name in dirs:
                local_dir_path = os.path.join(root, dir_name)
                
                folder_metadata = {
                    'name': dir_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                if current_parent_id:
                    folder_metadata['parents'] = [current_parent_id]
                    
                drive_folder = service.files().create(
                    body=folder_metadata, 
                    fields='id'
                ).execute()
                
                folder_mapping[local_dir_path] = drive_folder.get('id')
            
            for filename in files:
                file_path = os.path.join(root, filename)
                file_metadata = {'name': filename}
                if current_parent_id:
                    file_metadata['parents'] = [current_parent_id]
                    
                media = MediaFileUpload(file_path, resumable=True)
                file = service.files().create(
                    body=file_metadata, 
                    media_body=media, 
                    fields='id, name'
                ).execute()
                
                uploaded_files.append(file.get('name'))
                
        preview_files = ', '.join(uploaded_files[:50])
        if len(uploaded_files) > 50:
            preview_files += " ... (and more)"
            
        return f"Success: Uploaded {len(uploaded_files)} files recursively from '{local_folder_path}' to Google Drive.\nFiles preview: {preview_files}"
        
    except Exception as e:
        return f"Folder upload error: {str(e)}"

def download_from_drive(file_id: str, local_path: str) -> str:
    print(f"Downloading file {file_id} to {local_path}")
    try:
        service = _get_drive_service()
        request = service.files().get_media(fileId=file_id)
        with io.FileIO(local_path, 'wb') as fh:
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
        return f"Success: File downloaded to '{local_path}'"
    except Exception as e:
        return f"Download error: {str(e)}"

def share_drive_file(file_id: str) -> str:
    print(f"Sharing file: {file_id}")
    try:
        service = _get_drive_service()
        permission = {'type': 'anyone', 'role': 'reader'}
        service.permissions().create(fileId=file_id, body=permission).execute()
        link = f"https://drive.google.com/file/d/{file_id}/view"
        return f"Success: File shared. Public link:\n{link}"
    except Exception as e:
        return f"Share error: {str(e)}"

# Tools for SGRB

def read_unread_emails(prompt: str = "") -> str:
    print("Reading unread emails from Gmail...")
    try:
        service = _get_gmail_service()
        results = service.users().messages().list(userId='me', labelIds=['UNREAD'], maxResults=5).execute()
        messages = results.get('messages', [])
        
        if not messages:
            return "You have no new unread emails."
            
        report = f"{len(messages)} unread emails found:\n"
        for msg in messages:
            msg_data = service.users().messages().get(userId='me', id=msg['id'], format='metadata', metadataHeaders=['From', 'Subject']).execute()
            headers = msg_data.get('payload', {}).get('headers', [])
            
            sender = next((h['value'] for h in headers if h['name'] == 'From'), "Unknown")
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), "Without theme")
            report += f"From: {sender}\nTheme: {subject}\n\n"
            
        return report.strip()
    except Exception as e:
        return f"A Gmail error: {str(e)}"

def get_mailbox_status(prompt: str = "") -> str:
    print("Fetching mailbox status...")
    try:
        service = _get_gmail_service()
        profile = service.users().getProfile(userId='me').execute()
        
        inbox_results = service.users().labels().get(userId='me', id='INBOX').execute()
        unread_count = inbox_results.get('messagesUnread', 0)
        
        spam_results = service.users().labels().get(userId='me', id='SPAM').execute()
        spam_unread = spam_results.get('messagesUnread', 0)

        return (f"Box: {profile.get('emailAddress')}\n"
                f"Unread messages in the inbox: {unread_count}\n"
                f"Unread messages in spam: {spam_unread}")
    except Exception as e:
        return f"Error retrieving status: {str(e)}"

def create_draft(prompt: str) -> str:
    print("Creating Gmail draft...")
    try:
        if ":" not in prompt or "|" not in prompt:
            return ("Invalid format. Use:\n"
                    "draft: email@gmail.com | Theme | Text")
        
        data_str = prompt.split(':', 1)[1]
        parts = data_str.split('|')
        
        if len(parts) < 3:
            return "Insufficient data. Format: draft: email | theme | text"
            
        to_email = parts[0].strip()
        subject = parts[1].strip()
        body_text = parts[2].strip()

        message = EmailMessage()
        message.set_content(body_text)
        message['To'] = to_email
        message['Subject'] = subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'message': {'raw': encoded_message}}

        service = _get_gmail_service()
        draft = service.users().drafts().create(userId='me', body=create_message).execute()
        
        draft_id = draft['message']['id']
        link = f"https://mail.google.com/mail/u/0/#drafts?compose={draft_id}"
        
        return f"Created!\nTo: {to_email}\nTheme: {subject}\nLink: {link}"
    except Exception as e:
        return f"Error creating draft: {str(e)}"