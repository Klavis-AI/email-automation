import os
import base64
import time
from typing import List, Optional

import requests

from constants import (
    RESEND_API_KEY,
    RESEND_API_BASE_URL,
    FROM_EMAIL,
    EMAIL_RECIPIENTS,
    REPLY_TO,
    SUBJECT,
    DELAY_SECONDS,
    ATTACHMENT_PATH,
    ATTACHMENT_NAME,
)

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "templates", "emails")

def load_email_templates(templates_dir: Optional[str] = None) -> List[str]:
    """
    Load all HTML templates from the templates directory (sorted by filename).

    Returns a list of HTML strings.
    """
    dir_path = templates_dir or TEMPLATES_DIR
    if not os.path.isdir(dir_path):
        raise FileNotFoundError(f"Templates directory not found: {dir_path}")

    html_files = [f for f in os.listdir(dir_path) if f.lower().endswith(".html")]
    html_files.sort()

    templates: List[str] = []
    for filename in html_files:
        full_path = os.path.join(dir_path, filename)
        with open(full_path, "r", encoding="utf-8") as f:
            templates.append(f.read())
    if not templates:
        raise ValueError("No HTML templates found in templates directory")
    return templates

def create_attachment(file_path: str, filename: Optional[str] = None) -> dict:
    """
    Create an attachment dictionary for email sending.
    
    Args:
        file_path (str): Path to the file to attach
        filename (str, optional): Custom filename for the attachment
    
    Returns:
        dict: Attachment dictionary with filename and base64 encoded content
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Attachment file not found: {file_path}")
    
    if not filename:
        filename = os.path.basename(file_path)
    
    with open(file_path, 'rb') as file:
        file_content = file.read()
        encoded_content = base64.b64encode(file_content).decode('utf-8')
    
    return {
        "filename": filename,
        "content": encoded_content
    }

def send_batch_emails(
    from_email: str,
    email_list: List[str],
    subject: str,
    message: str,
    reply_to: Optional[str] = REPLY_TO,
):
    """
    Send batch emails using Resend batch API.
    
    Args:
        from_email (str): Sender email address
        email_list (list): List of recipient email addresses
        subject (str): Email subject
        message (str): Email message (can be plain text or HTML)
    
    Returns:
        dict: Response from Resend batch API
    """
    # Ensure API key is available
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY environment variable is required")
    
    if not email_list:
        raise ValueError("Email list cannot be empty")
    
    # Prepare batch email data
    batch_emails = []
    for email in email_list:
        email_data = {
            "from": from_email,
            "to": [email],
            "subject": subject,
        }
        if reply_to:
            email_data["reply_to"] = [reply_to] if isinstance(reply_to, str) else reply_to
        
        # Auto-detect if message is HTML or plain text
        if message.strip().startswith('<') and message.strip().endswith('>'):
            email_data["html"] = message
        else:
            email_data["text"] = message
        
        batch_emails.append(email_data)
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        # Send batch emails using Resend batch API
        response = requests.post(
            f"{RESEND_API_BASE_URL}/emails/batch",
            json=batch_emails,
            headers=headers
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        result = response.json()
        print(f"Batch emails sent successfully! {len(result.get('data', []))} emails sent")
        for i, email_result in enumerate(result.get('data', [])):
            print(f"Email {i+1} ID: {email_result.get('id')}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error sending batch emails: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise
    except Exception as e:
        print(f"Error sending batch emails: {str(e)}")
        raise

def send_email(
    from_email: str,
    to_email: str,
    subject: str,
    message: str,
    attachments: Optional[List[dict]] = None,
    reply_to: Optional[str] = REPLY_TO,
):
    """
    Send an email using Resend HTTP API.
    
    Args:
        from_email (str): Sender email address
        to_email (str): Recipient email address
        subject (str): Email subject
        message (str): Email message (can be plain text or HTML)
        attachments (list, optional): List of attachment dictionaries with 'filename' and 'content' keys
    
    Returns:
        dict: Response from Resend API
    """
    # Ensure API key is available
    if not RESEND_API_KEY:
        raise ValueError("RESEND_API_KEY environment variable is required")
            
    # Prepare email data
    email_data = {
        "from": from_email,
        "to": [to_email],
        "subject": subject,
    }
    if reply_to:
        email_data["reply_to"] = [reply_to] if isinstance(reply_to, str) else reply_to
    
    # Auto-detect if message is HTML or plain text
    if message.strip().startswith('<') and message.strip().endswith('>'):
        email_data["html"] = message
    else:
        email_data["text"] = message
    
    # Add attachments if provided
    if attachments:
        email_data["attachments"] = attachments
    
    # Prepare headers
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json",
    }
    
    try:
        # Send email using Resend HTTP API
        response = requests.post(
            f"{RESEND_API_BASE_URL}/emails",
            json=email_data,
            headers=headers
        )
        
        # Check if request was successful
        response.raise_for_status()
        
        result = response.json()
        print(f"Email sent successfully! ID: {result.get('id')}")
        return result
    
    except requests.exceptions.RequestException as e:
        print(f"HTTP Error sending email: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response status: {e.response.status_code}")
            print(f"Response body: {e.response.text}")
        raise
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        raise

def send_emails_with_templates(
    from_email: str,
    email_list: List[str],
    attachments: Optional[List[dict]] = None,
    delay_seconds: int = DELAY_SECONDS,
    reply_to: Optional[str] = REPLY_TO,
    subject: Optional[str] = SUBJECT,
    templates_dir: Optional[str] = None,
):
    """
    Send emails using different HTML templates, cycling through all available email templates.
    
    Args:
        from_email (str): Sender email address
        email_list (list): List of recipient email addresses
        attachments (list, optional): List of attachment dictionaries
        delay_seconds (int, optional): Delay in seconds between each email (default: 1)
        reply_to (str, optional): Reply-to email address
        subject (str, optional): Email subject line
        templates_dir (str, optional): Directory containing HTML email templates
    
    Returns:
        list: List of results from each email send with template info
    """
    if not email_list:
        raise ValueError("Email list cannot be empty")
    
    # Load email templates dynamically
    templates = load_email_templates(templates_dir)
    email_templates = [
        {"email": html, "subject": subject, "template": str(i + 1)}
        for i, html in enumerate(templates)
    ]
    
    results = []
    total_emails = len(email_list)
    
    print(f"Starting to send {total_emails} emails with rotating templates (1-{len(templates)})...")
    print(f"Using {delay_seconds} second delay between each email...")
    
    for i, recipient_email in enumerate(email_list):
        # Cycle through templates
        template_index = i % len(email_templates)
        current_template = email_templates[template_index]
        
        try:
            print(f"Sending email {i+1}/{total_emails} to {recipient_email} (Template {current_template['template']})...")
            result = send_email(
                from_email=from_email,
                to_email=recipient_email,
                subject=current_template["subject"],
                message=current_template["email"],
                attachments=attachments,
                reply_to=reply_to,
            )
            results.append({
                "email": recipient_email, 
                "result": result, 
                "status": "success",
                "template": current_template["template"]
            })
            
            # Add delay between emails (except after the last email)
            if i < total_emails - 1:
                print(f"Waiting {delay_seconds} second(s) before next email...")
                time.sleep(delay_seconds)
                
        except Exception as e:
            print(f"Failed to send email to {recipient_email}: {str(e)}")
            results.append({
                "email": recipient_email, 
                "error": str(e), 
                "status": "failed",
                "template": current_template["template"]
            })
            
            # Still wait before next email even if this one failed
            if i < total_emails - 1:
                print(f"Waiting {delay_seconds} second(s) before next email...")
                time.sleep(delay_seconds)
    
    # Print summary
    successful = len([r for r in results if r["status"] == "success"])
    failed = len([r for r in results if r["status"] == "failed"])
    print(f"\nEmail sending completed!")
    print(f"Successfully sent: {successful}/{total_emails}")
    print(f"Failed: {failed}/{total_emails}")
    
    # Print template distribution
    template_counts = {}
    for result in results:
        if result["status"] == "success":
            template = result["template"]
            template_counts[template] = template_counts.get(template, 0) + 1
    
    print(f"\nTemplate distribution (successful sends only):")
    for template in sorted(template_counts.keys()):
        print(f"  Template {template}: {template_counts[template]} emails")
    
    return results

if __name__ == "__main__":
    # Prepare attachments if the file exists
    attachments_list = []
    if ATTACHMENT_PATH and os.path.exists(ATTACHMENT_PATH):
        attachments_list = [
            create_attachment(ATTACHMENT_PATH, ATTACHMENT_NAME)
        ]

    # Send emails with rotating templates using default configurations from constants.py
    send_emails_with_templates(
        from_email=FROM_EMAIL,
        email_list=EMAIL_RECIPIENTS,
        attachments=attachments_list,
    )
    