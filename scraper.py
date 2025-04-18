import time,os
import logging


import logging
from colorama import init, Fore, Style

init(autoreset=True)

class ColorFormatter(logging.Formatter):
    def format(self, record):
        tag = getattr(record, 'tag', 'GENERAL')  # Default to GENERAL
        color = Fore.WHITE

        if tag == "SPLASH":
            color = Fore.LIGHTBLUE_EX
        elif tag == "SCRAPER":
            color = Fore.GREEN
        elif tag == "STEALTH":
            color = Fore.MAGENTA
        elif tag == "LYRICS":
            color = Fore.YELLOW
        elif tag == "NET":
            color = Fore.CYAN
        elif tag == "ERROR":
            color = Fore.RED

        level_symbol = {
            logging.INFO: "ℹ️",
            logging.WARNING: "⚠️",
            logging.ERROR: "❌",
            logging.DEBUG: "🔍",
            logging.CRITICAL: "💥"
        }.get(record.levelno, "🔸")

        msg = super().format(record)
        return f"{color}{level_symbol} [{tag}] {Style.RESET_ALL}{msg}"

# Set up logger with color + tag support
handler = logging.StreamHandler()
handler.setFormatter(ColorFormatter())

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.handlers = [handler]


# === Splash screen function ===
logger.info("Initializing splash screen...", extra={"tag": "SPLASH"})

def show_splash():
    os.system("cls" if os.name == "nt" else "clear")
    splash = r"""
 ███╗   ██╗██╗   ██╗██╗  ██╗███████╗███╗   ██╗     ███████╗ ██████╗██████╗ 
 ████╗  ██║██║   ██║██║ ██╔╝██╔════╝████╗  ██║     ██╔════╝██╔════╝██╔══██╗
 ██╔██╗ ██║██║   ██║█████╔╝ █████╗  ██╔██╗ ██║     █████╗  ██║     ██████╔╝
 ██║╚██╗██║██║   ██║██╔═██╗ ██╔══╝  ██║╚██╗██║     ██╔══╝  ██║     ██╔═══╝ 
 ██║ ╚████║╚██████╔╝██║  ██╗███████╗██║ ╚████║     ███████╗╚██████╗██║     
 ╚═╝  ╚═══╝ ╚═════╝ ╚═╝  ╚═╝╚══════╝╚═╝  ╚═══╝     ╚══════╝ ╚═════╝╚═╝     
    """
    print(splash)
    logger.info("⏳ Initializing GeniusScraper v1.0 - by Nyxen-XE", extra={"tag": "SPLASH"})
    time.sleep(2)
    logger.info("🕵️  Activating Stealth Browser Mode...", extra={"tag": "STEALTH"})
    
    time.sleep(1.2)
    logger.info("🔍 Loading Genius Search Interface...", extra={"tag": "STEALTH"})
    
    time.sleep(1.2)
    logger.info("🧠 Injecting Anti-Bot Scripts...", extra={"tag": "STEALTH"})
    time.sleep(1)
    logger.info("🚀 Ready to scrape. Let the hunt begin.\n", extra={"tag": "STEALTH"})
    time.sleep(1)
    os.system("cls" if os.name == "nt" else "clear")  # clear console after splash

# === Call splash screen before GUI ===
show_splash()


# logger.info("Injecting anti-bot stealth JS...", extra={"tag": "STEALTH"})
# logger.warning("No lyrics found. Possible rendering delay.", extra={"tag": "LYRICS"})
# logger.error("Internet connection failed!", extra={"tag": "NET"})


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import JavascriptException
from fuzzywuzzy import fuzz
import requests

import re

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--enable-unsafe-swiftshader")
# This can trick some detection
options.add_argument("--disable-blink-features=AutomationControlled")


# Set a legit user-agent
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                     "AppleWebKit/537.36 (KHTML, like Gecko) "
                     "Chrome/120.0.0.0 Safari/537.36")



# JavaScript patches to spoof navigator properties
stealth_js = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
Object.defineProperty(navigator, 'platform', {get: () => 'Win32'});
Object.defineProperty(navigator, 'chrome', {get: () => { return { runtime: {} }; }});
"""




options.add_argument("--log-level=3")  # Only show FATAL logs
options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Hide DevTools logs
service = Service()
browser = webdriver.Chrome(service=service,options=options)
   # Inject the stealth patches
browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
             "source": stealth_js
            })


from time import sleep
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


def internet_connection():
    try:
        requests.get('https://www.google.com', timeout=5)
        logger.info("Internet connection is available.", extra={"tag": "NET"})
        return True
    except requests.ConnectionError:
        logger.info("No internet connection", extra={"tag": "NET"})
        return False


def is_match(scraped_name, input_name, threshold=70):
    return fuzz.partial_ratio(scraped_name, input_name) > threshold

def click_show_more():
    try:
        browser.execute_script("""
        const atag = document.querySelector("body > routable-page > ng-outlet > search-results-page > div > div.column_layout > div.column_layout-column_span.column_layout-column_span--primary > div:nth-child(2) > search-result-section > div > a")
        atag.click()
            """)
        # show_more_btn = WebDriverWait(browser, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, '/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[2]/search-result-section/div/a'))
        # )
        #show_more_btn = browser.find_element(By.XPATH,'/html/body/routable-page/ng-outlet/search-results-page/div/div[2]/div[1]/div[2]/search-result-section/div/a')
        logger.info("Show more songs button found. Clicking...", extra={"tag": "SCRAPER"})
    except JavascriptException as e:
        logger.error("⚠️ Failed to click 'Show more' button. Page might have failed to load.", extra={"tag": "SCRAPER"})
        #logger.error(f"Error: {e}", extra={"tag": "SCRAPER"})
        return False 
    return True

def clean_text(text):
    text = re.sub(r'[\(\)\[\]\{\}]', '', text)  # Remove brackets
    text = re.sub(r'feat\..*', '', text, flags=re.IGNORECASE)  # Remove "feat. ..."
    return text.strip().lower()

def find_song_and_open(artistName, trackName):
    global trackTitle
    global trackLink
    trackLink = ''
    trackTitle = ''
    try:
        logger.info("⏳ Waiting for page to render...", extra={"tag": "SCRAPER"})
        # Wait for the songs container to load
        sleep(5)

        # Execute JavaScript to grab all mini song cards
        allCards = browser.execute_script("""
            const miniCards = document.querySelectorAll('mini-song-card');
            const cards = [];

            miniCards.forEach(card => {
                const titleEl = card.querySelector('.mini_card-title');
                const subtitleEl = card.querySelector('.mini_card-subtitle');
                const linkEl = card.querySelector('a');

                if (titleEl && subtitleEl && linkEl) {
                    cards.push({
                        title: titleEl.textContent.trim(),
                        subtitle: subtitleEl.textContent.trim(),
                        link: linkEl.href
                    });
                }
            });

            return cards;
        """)

        if not allCards:
            logging.error("No results loaded. Page might have failed.", extra={"tag": "SCRAPER"})
            return

        logger.info(f"✅ {len(allCards)} results fetched. Scanning...", extra={"tag": "SCRAPER"})
        # Clean the track and artist names for comparison
        trackName = trackName.replace('feat.','').replace('ft.','').replace('(','').replace(')','').replace('[','').replace(']','').strip()
        artistName = artistName.replace('feat.','').replace('ft.','').replace('(','').replace(')','').replace('[','').replace(']','').strip()

        track_clean = clean_text(trackName)
        artist_clean = clean_text(artistName)
        found = False
        for card in allCards:
            card_title = clean_text(card['title'])
            card_subtitle = clean_text(card['subtitle'])

            if is_match(track_clean, card_title) and is_match(artist_clean, card_subtitle):
                logging.info(f"🎯 Match found: {card['title']} by {card['subtitle']}",extra={"tag": "SCRAPER"})
                trackTitle = card['title'] + ' by ' + card['subtitle']
                trackLink = card['link']
                logging.info(f"🔗 Opening link: {card['link']}",extra={"tag": "SCRAPER"})
                time.sleep(1.5)
                logger.warning("This might take a few seconds...", extra={"tag": "LYRICS"})
                found = True
                # Open the link in the browser
                #browser.execute_script("window.open(arguments[0]);", card['link'])
                browser.get(card['link'])
                # Wait for the page to load
                extract_lyrics()
                break
        if not found:
         logger.info("❌ Track not found in the search results.", extra={"tag": "SCRAPER"})
         logger.info("❌ No matching track found. Please check the artist and track names.", extra={"tag": "SCRAPER"})
         return False
        
    except TimeoutException:
        logger.error("⚠️ Timeout: Songs container or result failed to load.", extra={"tag": "SCRAPER"})
       


        logger.error("⚠️ Please check your internet connection or try again later.", extra={"tag": "NET"})

def extract_lyrics():
    try:
        logger.info("📝 Waiting for lyrics to load...", extra={"tag": "LYRICS"})

        #lyricsRoot = browser.find_element(By.ID,'lyrics-root')
        lyricsRoot = WebDriverWait(browser,5).until(EC.presence_of_element_located((By.ID,'lyrics-root')))
        lyrics = ''
        if lyricsRoot:
            browser.execute_script("""
            window.stop()
                """)
            lyricsContainer = lyricsRoot.find_elements(By.CSS_SELECTOR,'.Lyrics__Container-sc-78fb6627-1')
            for l in lyricsContainer:
                lyrics += l.text
        return lyrics
                

    except Exception as e:
        logger.error(f"❌ Failed to extract lyrics: {e}", extra={"tag": "LYRICS"})
        logger.error("⚠️ Lyrics not found. Page might have failed to load.", extra={"tag": "LYRICS"})
        return None


def scrape_lyrics(artistName, trackName):
    # if not internet_connection():
    #     logger.error("No internet connection. Please check your connection.")
    #     return None
    if not artistName or not trackName:
        logger.error("Please provide both artist and track names.", extra={"tag": "SCRAPER"})
        
        return None
    if not isinstance(artistName, str) or not isinstance(trackName, str):
        logger.error("Artist and track names must be strings.", extra={"tag": "SCRAPER"})
        return None
    if not artistName.strip() or not trackName.strip():
        logger.error("Artist and track names cannot be empty.", extra={"tag": "SCRAPER"})
        return None
    if not re.match(r'^[a-zA-Z0-9\s]+$', artistName) or not re.match(r'^[a-zA-Z0-9\s]+$', trackName):
        logger.error("Artist and track names can only contain alphanumeric characters and spaces.", extra={"tag": "SCRAPER"})
        return None
    try: 
        global browser
        global trackTitle
        global trackLink
     
        logger.info("Scraping initiated for requested track...", extra={"tag": "SCRAPER"})
        time.sleep(2)
        logger.info("Scraping has begun.", extra={"tag": "SCRAPER"})
        time.sleep(2.5)
        logger.info("Initializing browser...", extra={"tag": "SCRAPER"})
        time.sleep(2)
        logger.info("Launching browser...", extra={"tag": "SCRAPER"})
        time.sleep(2)
        logger.info("Loading Genius...", extra={"tag": "SCRAPER"})
        time.sleep(2.6)
        logger.info("Loading Genius...", extra={"tag": "LYRICS"})
        time.sleep(2.6)
        logger.warning("This might take a few seconds...", extra={"tag": "LYRICS"})

        browser.implicitly_wait(5)
        browser.get(f'https://genius.com/search?q={artistName}+{trackName}')
        browser.maximize_window()

        logger.info(f"Searching for: '{trackName}' by {artistName}", extra={"tag": "SCRAPER"})
        logger.info("Waiting for page to load...", extra={"tag": "SCRAPER"})
     
        time.sleep(2)
        logger.info("Page loaded successfully.", extra={"tag": "SCRAPER"})
        if click_show_more():
            find_song_and_open(artistName, trackName)
        else:
            return
        
        lyrics = extract_lyrics()
        if lyrics:
            logger.info("Lyrics found!", extra={"tag": "LYRICS"})
            logger.info("Lyrics extracted successfully!", extra={"tag": "LYRICS"})
            lyricsData = {"track_title": trackTitle, 
                          'track_link': trackLink, 
                          'artist': artistName,
                            'track': trackName,
                              'lyrics': lyrics + "\n"}
            return lyricsData
        else:
            logger.error("No lyrics found.", extra={"tag": "LYRICS"})
            logger.error("Lyrics extraction failed.", extra={"tag": "LYRICS"})
            logger.warning("Please check the track name or artist name.", extra={"tag": "LYRICS"})
            return None
    except requests.ConnectionError:
        logger.error("No internet connection. Please check your connection.", extra={"tag": "NET"})
        
        return None
    except TimeoutException:
        logger.error("Page took too long to load. Please try again.", extra={"tag": "NET"})
        return None
    

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}", extra={"tag": "ERROR"})

    finally:
        browser.quit()
        logger.info("Browser closed.", extra={"tag": "SCRAPER"})
        logger.info("Scraping session ended.", extra={"tag": "SCRAPER"})
        logger.info("Thank you for using LyricsFusion!", extra={"tag": "SCRAPER"})



# scrape_lyrics('playboi carti','crank')