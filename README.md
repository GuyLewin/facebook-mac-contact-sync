# facebook-mac-contact-sync
This project was purposed to sync my Facebook contact pictures with my iPhone contacts. It is done by syncing the Facebook contacts with my macOS address book, which is synced via my Google account to my phone.
It does not get data from Facebook by itself, but expects data formatted by [my fork of Ultimate-Facebook-Scraper](https://github.com/GuyLewin/Ultimate-Facebook-Scraper).

## Prerequisites
Install the required Python packages by running
```sh
pip install -r requirements.txt
```
in this code directory.

## Usage
1. Configure and run my fork of Ultimate-Facebook-Scraper to get a scraped Facebook directory
2. Open a shell within that directory
3. Run:
```sh
python path/to/facebook-mac-contact-sync/sync_friends.py
```

This script is written in Python 2.7, while Ultimate-Facebook-Scraper is in Python 3. You will need them both to complete the sync.
