import csv
import os

INPUT_FILE = 'result_emails_selenium.csv'  # Raw file after scraping
OUTPUT_FILE = 'clean_list_for_sending.csv'  # Clean file for mailing


def clean_data():
    if not os.path.exists(INPUT_FILE):
        print(f"File {INPUT_FILE} not found. Run the scraper first!")
        return

    unique_emails = set()
    clean_rows = []

    # Statistics
    total_rows = 0
    valid_emails = 0
    duplicates = 0

    print(f"Starting to clean the file {INPUT_FILE}...")

    with open(INPUT_FILE, mode='r', encoding='utf-8') as infile:
        reader = csv.DictReader(infile)

        for row in reader:
            total_rows += 1

            channel_name = row.get('Channel Name', '').strip()
            url = row.get('About URL', '').strip()
            raw_email = row.get('Found Emails', '').strip()

            # 1. Filter out garbage: skip "Not Found", "Error", and empty values
            if not raw_email or raw_email in ['Not Found', 'Error', '']:
                continue

            # 2. Handle multiple emails in a single cell
            # (sometimes formatted as "mail1@com, mail2@com")
            # We split them and process them individually
            emails_in_row = [e.strip() for e in raw_email.split(',')]

            for email in emails_in_row:
                # Convert to lowercase for accurate duplicate detection
                email_lower = email.lower()

                # 3. Check for duplicates
                if email_lower in unique_emails:
                    duplicates += 1
                    continue

                # If everything is fine, store it
                unique_emails.add(email_lower)
                # Save the clean data.
                # Included channel_name to address the streamer by name in the email campaign
                clean_rows.append([channel_name, url, email])
                valid_emails += 1

    # Write to the new file
    with open(OUTPUT_FILE, mode='w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        # Headers optimized for mail merge tools like YAMM
        writer.writerow(['Name', 'URL', 'Email'])
        writer.writerows(clean_rows)

    print("-" * 30)
    print(f"Done! Result saved in: {OUTPUT_FILE}")
    print(f"Statistics:")
    print(f"Total input rows: {total_rows}")
    print(f"Duplicates removed:   {duplicates}")
    print(f"Clean contacts found:     {valid_emails}")
    print("-" * 30)


if __name__ == "__main__":
    clean_data()
