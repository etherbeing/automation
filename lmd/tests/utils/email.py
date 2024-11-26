import os
from email import policy
from email.parser import BytesParser
from email.utils import getaddresses

def extract_email_info(email_file_path):
    """Extracts email information from the file created by FileBasedEmailBackend."""
    
    if not os.path.exists(email_file_path):
        print(f"File {email_file_path} does not exist.")
        return
    
    email_info = []

    with open(email_file_path, 'rb') as f:
        # Read all emails in the file (assuming each email is separated by some delimiter)
        data = f.read()
        emails = data.split(b'From ')  # Split based on 'From ' header
        
        # Iterate over all the emails found in the file
        for email_raw in emails:
            if email_raw.strip():  # Ignore empty entries
                # Parse the raw email message
                msg = BytesParser(policy=policy.default).parsebytes(b'From ' + email_raw)
                
                email_data = {
                    "Subject": msg.get('Subject'),
                    "From": msg.get('From'),
                    "To": getaddresses(msg.get_all('To', [])),
                    "Reply-To": msg.get('Reply-To'),
                    "Date": msg.get('Date'),
                    "Body": msg.get_body(preferencelist=('plain', 'html')).get_payload(decode=True).decode(errors='ignore') if msg.is_multipart() else msg.get_payload(decode=True).decode(errors='ignore')
                }

                email_info.append(email_data)

    return email_info

def print_extracted_email_info(email_info):
    """Prints the extracted email information in a readable format."""
    for idx, info in enumerate(email_info):
        print(f"\nEmail {idx + 1}:")
        print(f"Subject: {info['Subject']}")
        print(f"From: {info['From']}")
        print(f"To: {', '.join([addr[1] for addr in info['To']])}")  # Get only the email address from (name, email)
        print(f"Reply-To: {info['Reply-To']}")
        print(f"Date: {info['Date']}")
        print(f"Body: {info['Body'][:100]}...")  # Display the first 100 characters of the body

# Example usage
# email_file_path = 'path_to_your_email_log_file.txt'  # Specify the file path of the email log
# email_info = extract_email_info(email_file_path)
# print_extracted_email_info(email_info)
