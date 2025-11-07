import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.common.exceptions import WebDriverException
from datetime import date
import csv
import time
import random
import sys
import math
import os


# Optional OS mouse fallback
try:
    import pyautogui
    _HAS_PYAUTOGUI = True
except Exception:
    _HAS_PYAUTOGUI = False

# --- CONFIG ---
BASE_URL = "https://ingatlan.com/lista/kiado+lakas+budapest?page="
OUTPUT_DIR = "data"
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_CSV = os.path.join(OUTPUT_DIR, f"{date.today()}.csv")

SLEEP_MIN, SLEEP_MAX = 1.5, 3.5  # random delay between pages

# --- SETUP BROWSER ---
# adjust version_main if necessary for your Chrome version
driver = uc.Chrome(version_main=141, headless=False)
#driver.maximize_window()
print("✅ Launched undetected Chrome visibly — starting scrape...")

# --- GLOBALS ---
cookies_accepted = False
max_pages = 1
start_time = time.time()

# --- COOKIE HANDLER ---
def accept_cookies():
    """Accept cookies if popup appears — only once globally."""
    global cookies_accepted
    if cookies_accepted:
        return
    try:
        print("🍪 Waiting for cookie consent button...")
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll"))
        )
        time.sleep(1.2)
        btn.click()
        cookies_accepted = True
        print("✅ Accepted cookies.")
        time.sleep(1.2)
    except Exception as e:
        # not fatal — some pages may not show the dialog
        print("⚠️ No cookie popup found (or failed to click):", getattr(e, "msg", e))

def set_max_pages():
    """Read and set the maximum number of result pages (updates global max_pages)."""
    global max_pages
    try:
        # wait for pagination area to be present (heuristic)
        WebDriverWait(driver, 8).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".text-gray-200, .pagination"))
        )
        # try the .text-gray-200 element first (as in original)
        elems = driver.find_elements(By.CSS_SELECTOR, ".text-gray-200")
        if elems:
            text = elems[0].text.strip()
            if "/" in text:
                try:
                    max_pages = int(text.split("/")[1].strip())
                    print(f"📄 Found {max_pages} total pages.")
                    return
                except Exception:
                    pass

        # fallback: look for pagination links and take the last page number
        pag_links = driver.find_elements(By.CSS_SELECTOR, "ul.pagination li a")
        page_nums = []
        for a in pag_links:
            try:
                t = a.text.strip()
                if t.isdigit():
                    page_nums.append(int(t))
            except:
                pass
        if page_nums:
            max_pages = max(page_nums)
            print(f"📄 Found {max_pages} total pages (from pagination links).")
            return

        print("⚠️ Could not determine max pages; defaulting to 1.")
        max_pages = 1
    except Exception as e:
        print("⚠️ Error determining max pages:", e)
        max_pages = 1

# --- PROGRESS BAR ---
def print_progress(current_page, total_pages):
    """Visualize scraping progress and estimate remaining time."""
    elapsed = time.time() - start_time
    avg_time_per_page = elapsed / current_page if current_page else 0
    remaining_pages = max(total_pages - current_page, 0)
    est_remaining = avg_time_per_page * remaining_pages

    bar_length = 30
    progress = current_page / total_pages if total_pages > 0 else 0
    filled_length = int(bar_length * progress)
    bar = "▓" * filled_length + "░" * (bar_length - filled_length)

    sys.stdout.write(
        f"\r📊 Page {current_page}/{total_pages} | {bar} {progress*100:5.1f}% | "
        f"⏱️ Elapsed: {elapsed/60:.1f} min | ⌛ ETA: {est_remaining/60:.1f} min"
    )
    sys.stdout.flush()

# --- CLOUDFLARE HELPERS ---
def is_cloudflare_challenge():
    """Return True if page looks like a Cloudflare browser-check / challenge."""
    try:
        url = driver.current_url or ""
        title = (driver.title or "").lower()
        body_text = (driver.find_element(By.TAG_NAME, "body").text or "").lower()[:1200]
    except Exception:
        url = ""
        title = ""
        body_text = ""

    # heuristics
    if "/cdn-cgi/" in url:
        return True
    if "just a moment" in title or "checking your browser" in title:
        return True
    if "checking your browser before accessing" in body_text or "please enable javascript" in body_text:
        return True
    # also look for CF-specific fragments
    try:
        if driver.find_elements(By.CSS_SELECTOR, "div[id*='challenge'], form[id*='challenge'], .cf-browser-verification"):
            return True
    except Exception:
        pass
    return False

def simulate_mouse_move_in_browser(steps=30):
    """Dispatch synthetic mousemove events + ActionChains moves inside the page."""
    js = """
    (function(){
      const steps = arguments[0] || 30;
      const w = window.innerWidth, h = window.innerHeight;
      let x = Math.floor(w*0.5), y = Math.floor(h*0.5);
      for (let i=0;i<steps;i++){
         x = Math.max(1, Math.min(w-1, x + Math.floor((Math.random()-0.5)*80)));
         y = Math.max(1, Math.min(h-1, y + Math.floor((Math.random()-0.5)*80)));
         const ev = new MouseEvent('mousemove', {clientX: x, clientY: y, bubbles: true});
         window.dispatchEvent(ev);
      }
      return true;
    })();
    """
    try:
        driver.execute_script(js, steps)
        body = driver.find_element(By.TAG_NAME, "body")
        ac = ActionChains(driver)
        w = driver.execute_script("return Math.max(document.documentElement.clientWidth, window.innerWidth || 0);")
        h = driver.execute_script("return Math.max(document.documentElement.clientHeight, window.innerHeight || 0);")
        # a few random native moves within body
        for _ in range(3):
            ox = int(w * (0.2 + 0.6 * random.random()))
            oy = int(h * (0.2 + 0.6 * random.random()))
            ac.move_to_element_with_offset(body, ox, oy)
            ac.pause(0.05 + random.random() * 0.08)
        ac.perform()
        return True
    except WebDriverException as e:
        print("⚠️ simulate_mouse_move_in_browser failed:", e)
        return False
    except Exception as e:
        print("⚠️ simulate_mouse_move_in_browser unexpected error:", e)
        return False

def move_real_mouse_with_pyautogui(duration=0.9):
    """Fallback that moves the real OS mouse. Uses pyautogui (if available)."""
    if not _HAS_PYAUTOGUI:
        print("⚠️ pyautogui not available — install it to enable OS mouse fallback.")
        return False
    try:
        screen_w, screen_h = pyautogui.size()
        # aim near center (assuming browser is maximized)
        cx = int(screen_w * 0.5 + (random.random() - 0.5) * screen_w * 0.08)
        cy = int(screen_h * 0.45 + (random.random() - 0.5) * screen_h * 0.08)
        steps = random.randint(12, 26)
        for i in range(steps):
            nx = int(cx + math.sin(i / steps * math.pi * 2) * random.uniform(5, 160))
            ny = int(cy + math.cos(i / steps * math.pi * 2) * random.uniform(5, 160))
            t = duration / steps
            pyautogui.moveTo(nx, ny, duration=t, _pause=False)
        return True
    except Exception as e:
        print("⚠️ move_real_mouse_with_pyautogui failed:", e)
        return False

def handle_cloudflare(timeout=35):
    """
    Call after driver.get(url). If a CF challenge appears, try in-browser mouse moves,
    then fallback to moving real mouse. Wait until challenge disappears or timeout.
    Returns True if it cleared, False if not / timed out.
    """
    if not is_cloudflare_challenge():
        return False

    print("🛡️ Cloudflare challenge detected — attempting to simulate human behavior...")
    start = time.time()

    # try repeated cycles
    while time.time() - start < timeout:
        simulate_mouse_move_in_browser()
        time.sleep(0.6 + random.random() * 0.8)

        try:
            if not is_cloudflare_challenge():
                print("✅ Cloudflare cleared after in-browser simulation.")
                return True
        except Exception:
            pass

        # fallback to OS mouse if available
        if _HAS_PYAUTOGUI:
            print("🖱️ Falling back to moving the real mouse (pyautogui).")
            move_real_mouse_with_pyautogui(duration=0.8 + random.random() * 0.8)
            time.sleep(1.0 + random.random() * 1.2)
            try:
                if not is_cloudflare_challenge():
                    print("✅ Cloudflare cleared after real mouse movement.")
                    return True
            except Exception:
                pass

        # small scroll / jitter
        try:
            driver.execute_script("window.scrollBy(0, arguments[0]);", int(120 * (random.random() - 0.5)))
        except Exception:
            pass

        time.sleep(0.8 + random.random() * 1.0)

    print("❌ Cloudflare challenge did not clear within timeout.")
    return False

# --- SCRAPE A SINGLE PAGE ---
def scrape_page(page_number):
    url = f"{BASE_URL}{page_number}"
    print(f"\n🔗 Loading page {page_number}: {url}")
    driver.get(url)

    # detect and handle Cloudflare
    if is_cloudflare_challenge():
        cleared = handle_cloudflare(timeout=35)
        if not cleared:
            print("⚠️ Cloudflare not cleared automatically. You can intervene manually.")
            # let the caller decide: we return empty so main loop may prompt/ retry
            return []
        
    # handle cookies once if shown
    if not cookies_accepted:
        accept_cookies()

    # after CF & cookies, set max_pages once
    if page_number == 1:
        set_max_pages()

    # wait for listings
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".listing-card"))
        )
    except Exception:
        print("⚠️ No visible listings found after waiting.")
        return []

    listings = driver.find_elements(By.CSS_SELECTOR, ".listing-card")
    if not listings:
        return []

    listings_data = []

    for listing in listings:
        data = {}
        try:
            data["price"] = listing.find_element(By.CSS_SELECTOR, ".listing-card-content .me-2").text.strip()
        except:
            data["price"] = None

        try:
            data["location"] = listing.find_element(By.CSS_SELECTOR, ".d-block.fs-7.text-gray-900").text.strip()
        except:
            data["location"] = None

        details = listing.find_elements(By.CSS_SELECTOR, ".w-100.mt-3 .fs-6")
        data["alapterulet"] = details[0].text.strip() if len(details) > 0 else None
        data["szobak"] = details[1].text.strip() if len(details) > 1 else None
        data["erkely"] = details[2].text.strip() if len(details) > 2 else None

        data["page"] = page_number
        listings_data.append(data)

    print(f"✅ Collected {len(listings_data)} listings from page {page_number}.")
    return listings_data

# --- MAIN SCRAPER LOOP ---
all_data = []
page_number = 1

while True:
    page_data = scrape_page(page_number)
    if page_data:
        all_data.extend(page_data)
        print_progress(page_number, max_pages)
        page_number += 1
    else:
        print(f"\n❌ No listings on page {page_number} (or Cloudflare blocking).")
        user_input = input("👉 Type 'y' to quit, 'r' to retry this page, or press Enter to continue: ").strip().lower()
        if user_input == "y":
            print("🛑 User chose to stop scraping.")
            break
        elif user_input == "r":
            print("🔄 Retrying same page...")
            time.sleep(2 + random.random() * 2)
            continue
        else:
            print("🔄 Continuing to next page (skipping current).")
            page_number += 1

    if page_number > max_pages:
        print("\n✅ Reached last page.")
        break

    # polite delay
    time.sleep(random.uniform(SLEEP_MIN, SLEEP_MAX))

# --- SAVE TO CSV ---
if all_data:
    print(f"\n💾 Saving {len(all_data)} total listings to {OUTPUT_CSV}...")
    fieldnames = ["page", "price", "location", "alapterulet", "szobak", "erkely"]
    try:
        with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_data)
        print("✅ CSV saved successfully.")
    except Exception as e:
        print("⚠️ Failed to save CSV:", e)
else:
    print("\n⚠️ No data collected — nothing saved.")

driver.quit()
print("🚀 Scraping complete.")
