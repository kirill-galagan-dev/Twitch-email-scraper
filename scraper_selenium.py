import csv
import re
import time
from typing import List

# Libraries for browser automation:
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

# --- CONFIGURATION ---
LIMIT_NICKNAMES = None  # Number of channels to check (set to None to process all)
INPUT_CSV_FILE = 'channels.csv'  # Input file name (With Twitch channels)
OUTPUT_CSV_FILE = 'result_emails_selenium.csv' # Result file after scraping
DELAY_SECONDS = 5  # Increased delay to allow the page to fully load

# Email Regex + Blacklist
EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
IGNORE_WORDS = ['twitch.tv', 'support', 'privacy', 'legal', 'jobs', 'example', 'sullygnome', 'w3.org']


def extract_emails(text: str) -> List[str]:
    """Extracts emails and filters out unwanted matches/noise"""
    if not text:
        return []
    raw_emails = re.findall(EMAIL_REGEX, text)
    clean_emails = []
    for email in raw_emails:
        email_lower = email.lower()
        if any(bad_word in email_lower for bad_word in IGNORE_WORDS):
            continue
        # Filter out image extensions that occasionally match the regex
        if email_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
            continue
        clean_emails.append(email)
    return list(set(clean_emails))


def main():
    print("Starting Selenium script...")

    # 1. Configure Chrome browser
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless") # Uncomment to run in background (headless mode)
    options.add_argument("--mute-audio")  # Mute audio to prevent streams from playing out loud
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36")

    # Automatically install and setup ChromeDriver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    processed_count = 0

    try:
        with open(INPUT_CSV_FILE, mode='r', encoding='utf-8') as infile, \
                open(OUTPUT_CSV_FILE, mode='w', newline='', encoding='utf-8') as outfile:

            reader = csv.DictReader(infile)
            writer = csv.writer(outfile)
            writer.writerow(['Channel Name', 'About URL', 'Found Emails'])

            for row in reader:
                if LIMIT_NICKNAMES is not None and processed_count >= LIMIT_NICKNAMES:
                    print("Limit reached.")
                    break

                base_url = row.get('URL', '').strip()
                channel_name = row.get('Channel', 'Unknown').strip()

                if not base_url:
                    continue

                # Build the /about URL
                target_url = base_url
                if not target_url.endswith('/about'):
                    target_url = target_url.rstrip('/') + '/about'

                print(f"🔎 ({processed_count + 1}) Opening: {channel_name}...")

                try:
                    # 2. Navigate to the page
                    driver.get(target_url)

                    # 3. Wait for JavaScript to load
                    time.sleep(DELAY_SECONDS)

                    # 4. Slight scroll down to trigger lazy loading
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
                    time.sleep(1)

                    # 5. Get the ENTIRE page source (now containing the loaded text)
                    page_content = driver.page_source

                    # 6. Search for Emails
                    found_emails = extract_emails(page_content)

                    if found_emails:
                        email_str = ", ".join(found_emails)
                        print(f"FOUND: {email_str}")
                        writer.writerow([channel_name, target_url, email_str])
                    else:
                        print("Email not found.")
                        writer.writerow([channel_name, target_url, "Not Found"])

                except Exception as e:
                    print(f"Processing error: {e}")
                    writer.writerow([channel_name, target_url, "Error"])

                processed_count += 1

    except FileNotFoundError:
        print(f"File {INPUT_CSV_FILE} not found!")
    finally:
        # Always close the browser at the end
        print("Execution finished. Closing browser.")
        driver.quit()


if __name__ == "__main__":
    main()