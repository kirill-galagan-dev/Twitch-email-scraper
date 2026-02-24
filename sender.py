import boto3
import csv
import time
import random
import re
from botocore.exceptions import ClientError

# --- AWS CONFIGURATION ---
AWS_ACCESS_KEY = 'YOUR_ACCESS_KEY_HERE'
AWS_SECRET_KEY = 'YOUR_SECRET_KEY_HERE'
AWS_REGION = 'us-east-1'  # e.g., us-east-1 or eu-north-1

SENDER = "Name <your_email@gmail.com>" # Sender format: "Name <email>"

CSV_FILENAME = 'clean_list_for_sending.csv' # The clean CSV file to read from

# Email subjects (Script picks a random one to bypass spam filters):
SUBJECTS = [
    "Bonk critters for loot 💰 Planet Hoarders (Launch Key)",
    "Hunt, Hide, Bonk 🔨 Planet Hoarders (Steam Key)",
    "Feed, Bonk, Collect, Survive 🐾 Planet Hoarders (Key)"
]

# HTML Email Body:
HTML_BODY = """
<p>Hi {{Name}},</p>
<p>I’m Kirill, an indie dev from Estonia. I’ve been following your channel and wanted to show you my upcoming game <b>Planet Hoarders</b>.</p>
<p>It’s a chaotic 4-player co-op horror where you have to meet the quota by catching fast alien critters. The loop is tricky: you need to <b>feed them</b> to calm them down, <b>BONK them with a hammer</b>, and drag them <b>back to the ship</b>.</p>
<p>But while you hunt the small ones, <b>bigger monsters are hunting you</b>. You cannot fight back — you can only <b>run for your life or disguise yourself as a box</b> to hide in plain sight.</p>
<p>If you enjoy chaotic games with <i>Lethal Company</i> vibes, this might be a fun fit for your squad.</p>

<p>The game releases on December 17 on Steam. I’d be happy to send you a key.</p>
<p>To get one, simply reply to this email. Even writing just “key” is enough.</p>

<br>
<p><b>Steam page:</b> <a href="https://store.steampowered.com/app/3291090/Planet_Hoarders/">Planet Hoarders on Steam</a></p>
<br>
<p>If you need anything else (footage, assets) — just tell me.<br>
Hope Planet Hoarders brings your community some hilarious moments.</p>

<p>Best regards,<br>
Kirill<br>
Developer of Planet Hoarders</p>

<p style="font-size: 10px; color: gray;">P.S. If you are not interested, just reply 'no'.</p>
"""

# Plain text version (Required for older email clients and lower spam score):
TEXT_BODY = """
Hi {{Name}},

I’m Kirill, an indie dev from Estonia. I wanted to show you my upcoming game Planet Hoarders.
It’s a chaotic 4-player co-op horror where you hunt critters, BONK them with a hammer, and hide from monsters inside a  box.

Steam: https://store.steampowered.com/app/3291090/Planet_Hoarders/

Reply "key" to get a Steam key.

Best regards,
Kirill
"""

def clean_email_address(raw_email):
    if not raw_email:
        return None
    first_part = raw_email.split(',')[0]
    match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', first_part)
    if match:
        return match.group(0)
    return None

def send_bulk_email():
    """Main engine for sending bulk emails via AWS SES."""

    # Initialize AWS SES client
    client = boto3.client(
        'ses',
        aws_access_key_id=AWS_ACCESS_KEY,
        aws_secret_access_key=AWS_SECRET_KEY,
        region_name=AWS_REGION
    )

    print(f"Opening database: {CSV_FILENAME}...")

    with open(CSV_FILENAME, newline='', encoding='utf-8-sig') as csvfile:
        reader = csv.DictReader(csvfile)

        headers = reader.fieldnames
        name_col = 'Channel Name' if 'Channel Name' in headers else 'Name'
        email_col = 'Found Emails' if 'Found Emails' in headers else 'Email'

        count = 0
        for row in reader:
            raw_name = row.get(name_col, '').strip()
            raw_email = row.get(email_col, '').strip()
            # Clean email from potential garbage
            email = clean_email_address(raw_email)
            # Check
            if not email:
                print(f"Skipping: No valid email found in '{raw_email}'")
                continue

            # Fallback if name is empty
            clean_name = raw_name if raw_name else "there"

            personal_html = HTML_BODY.replace("{{Name}}", clean_name)
            personal_text = TEXT_BODY.replace("{{Name}}", clean_name)

            current_subject = random.choice(SUBJECTS)

            print(f"[{count + 1}] Sending to: {email} ({clean_name})... ", end='')

            try:
                # Send email via AWS SES
                response = client.send_email(
                    Source=SENDER,
                    Destination={
                        'ToAddresses': [email],
                    },
                    Message={
                        'Subject': {'Data': current_subject, 'Charset': 'UTF-8'},
                        'Body': {
                            'Text': {'Data': personal_text, 'Charset': 'UTF-8'},
                            'Html': {'Data': personal_html, 'Charset': 'UTF-8'},
                        }
                    },
                    ReplyToAddresses=[SENDER.split("<")[1].replace(">", "")]  # Reply-to address
                )
                print(f"OK! ID: {response['MessageId']}")
                count += 1

            except ClientError as e:
                print(f"AWS ERROR: {e.response['Error']['Message']}")
            except Exception as e:
                print(f"ERROR: {e}")

            # Anti-spam delay (randomized pause between emails)
            delay = random.uniform(6, 12)
            print(f"Waiting {delay:.1f} sec...")
            time.sleep(delay)

    print(f"\n Done! Total emails sent: {count}")

if __name__ == '__main__':
    confirm = input("Are you sure AWS keys are set and CSV is correct? Type 'yes' to start: ")
    if confirm.lower() == 'yes':
        send_bulk_email()
    else:
        print("Canceled.")


