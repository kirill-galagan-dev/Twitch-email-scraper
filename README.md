# Twitch Email Scraper (Selenium)

## 1. Setup & Prerequisites
Before the first run, ensure you have installed:
* Python (version 3.8 or newer).
* Google Chrome (latest version).

Then, install the required libraries. [cite_start]Open your terminal and run[cite: 3]:
```bash
pip install selenium webdriver-manager
```

## 2. Files & Folders
For the script to work correctly, your project folder must contain two files:

* scraper_selenium.py (The script itself).

* channels.csv (The table containing the channels to check).
  
Input CSV Format: The file must have headers. It must include a column named URL.
EXAMPLE:

Channel,URL

EXAMPLE,[https://www.twitch.tv/EXAMPLE](https://www.twitch.tv/EXAMPLE)

## 3. Configuration (Constants)
Open the scraper_selenium.py file in any text editor (e.g., VS Code, Notepad++). At the top of the file, you will find a settings block:
Check Limit:
LIMIT_NICKNAMES = 10 (For testing: set it to 10 or 5)
For a full run: Set it to None (without quotes) to check all links in the file.

Files:
INPUT_CSV_FILE = 'channels.csv' (Your input file with links).
OUTPUT_CSV_FILE = 'result_emails_selenium.csv' (Where to save the results).
NB: Ensure the INPUT_CSV_FILE exactly matches the name of your file in the folder.

Speed & Safety:
DELAY_SECONDS = 5. The waiting time (in seconds) on each page. Recommended: 4 or 5. If set lower (1-2), the website might not load in time, or Twitch might block you for spamming.

Hidden mode (Headless):
In the code (around line 45), there is a browser visibility setting:
# options.add_argument("--headless")
With the hash (#): You will see the browser open and switch pages.
Without the hash: The browser will run in the background (invisible). This is convenient if you need to use your computer for other tasks simultaneously.

## 4. How to Run & Stop
How to start:
Open the project folder in your terminal.
Run the command: python scraper_selenium.py.
Do not close the terminal window until you see the message "Execution finished.".

How to force stop:
If you need to stop the script immediately, press Ctrl + C in the terminal. The browser will close automatically.

## 5.Safety Tips (How to avoid bans)

Twitch protects itself from bots. To prevent your IP address from being blocked:

Do not log into your account: The script opens a "clean" browser (Incognito mode). Do not attempt to log into your personal Twitch account within this automated window. If Twitch bans the bot, it will only ban the current session, not your personal profile.
+2

Respect the delay: Do not set DELAY_SECONDS to less than 4 seconds.

Don't be greedy: If you have a list of 10,000 channels, it is better to split it into smaller chunks and run them with breaks, or use a VPN.

Watch the terminal: If you see multiple errors in a row, stop the script and check your internet connection or the website's availability.


## 6. Results
After the execution is complete, a file named result_emails_selenium.csv will appear.

Email Found: The successfully extracted email addresses.

Not Found: There is no text-based email on the page (it might be inside an image, or missing entirely).

Error: Page access error.

## 7.Data Cleaning
Raw scraped data often contains duplicates, empty values, or formatting noise. To prepare a clean mailing list:
Ensure your raw output file (result_emails_selenium.csv) is generated.
Run the cleaning script in your terminal:

```bash
python cleaner.py
```

The script will filter out invalid entries, remove duplicates, and separate multiple emails found on a single page.
The final, ready-to-use data will be saved as clean_list_for_sending.csv, formatted with headers (Name, URL, Email) optimized for mail merge tools like YAMM.
