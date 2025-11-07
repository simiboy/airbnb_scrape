# 🏙️ Ingatlan.com Apartment Scraper

A Python-based web scraper that automatically collects **rental apartment listings** from [ingatlan.com](https://ingatlan.com) (Budapest area by default).

It uses **Selenium** with **undetected-chromedriver** to avoid bot detection and can automatically handle Cloudflare “browser checks” by simulating realistic mouse movements — even moving the *real* mouse cursor if needed.

---

## 🚀 What This Script Does

- Launches an undetected Chrome browser
- Accepts the cookie popup automatically
- Detects and bypasses Cloudflare protection (by simulating human activity)
- Scrapes all listings for:
  - 💰 Price  
  - 📍 Location  
  - 📏 Floor area  
  - 🛏️ Rooms  
  - 🌇 Balcony info
- Displays a live progress bar with ETA
- Saves everything to a single CSV file: `ingatlan_all_listings.csv`

---

## 🧩 Step-by-Step Installation Guide

### 📦 Step 1. Install All Dependencies

Run these commands to install everything the scraper needs:

```bash
pip install --upgrade pip
pip install undetected-chromedriver selenium pyautogui setuptools
```

### 🌐 Step 2. Make Sure Google Chrome Is Installed

The scraper launches your **local Chrome browser** to mimic a real user.

Check your Chrome version:
```bash
(Get-Item "C:\Program Files\Google\Chrome\Application\chrome.exe").VersionInfo.ProductVersion
```

> Example output:  
> `141.0.2265.75`

---

### ⚙️ Step 3. Adjust Chrome Version in the Script (if needed)

Open the Python script (`ingatlan_scraper.py`) in a text editor.

Find this line near the top:
```python
driver = uc.Chrome(version_main=141, headless=False)
```

Change `141` to match the **major version** of your Chrome (the number before the first dot).

For example:
- Chrome 141.x → `version_main=141` ✅  
- Chrome 142.x → `version_main=142` ✅

---

### Run the Scraper

In your terminal (with the virtual environment active):

```bash
python ingatlan_scraper.py
```