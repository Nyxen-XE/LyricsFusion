from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import JavascriptException
from fuzzywuzzy import fuzz
import requests
import logging
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

from time import sleep
# Setup logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()


def internet_connection():
    try:
        requests.get('https://www.google.com', timeout=5)
        logger.info("Internet connection is available.")
        return True
    except requests.ConnectionError:
        logging.info("No internet connection")
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
        #logger.info("Show more songs button found. Clicking...")
    except JavascriptException as e:
        logger.error(e)
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
        print("⏳ Waiting for page to render...")
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
            print("🚫 No results loaded. Page might have failed.")
            return

        print(f"✅ {len(allCards)} results fetched. Scanning...")

        track_clean = clean_text(trackName)
        artist_clean = clean_text(artistName)
        found = False
        for card in allCards:
            card_title = clean_text(card['title'])
            card_subtitle = clean_text(card['subtitle'])

            if is_match(track_clean, card_title) and is_match(artist_clean, card_subtitle):
                print(f"🎯 Match found: {card['title']} by {card['subtitle']}")
                trackTitle = card['title'] + ' by ' + card['subtitle']
                trackLink = card['link']
                print(f"🔗 Opening link: {card['link']}")
                found = True
                browser.get(card['link'])
                extract_lyrics()
                break
        if not found:

         print("❌ Track not found in the search results.")
         return False
        
    except TimeoutException:
        print("⚠️ Timeout: Songs container or result failed to load.")
       



def extract_lyrics():
    try:
        print("📝 Waiting for lyrics to load...")
        #lyricsRoot = browser.find_element(By.ID,'lyrics-root')
        lyricsRoot = WebDriverWait(browser,5).until(EC.presence_of_element_located((By.ID,'lyrics-root')))
        lyrics = ''
        if lyricsRoot:
            lyricsContainer = lyricsRoot.find_elements(By.CSS_SELECTOR,'.Lyrics__Container-sc-78fb6627-1')
            for l in lyricsContainer:
                lyrics += l.text
        return lyrics
                

    except Exception as e:
        print(f"❌ Failed to extract lyrics: {e}")
        return None


def scrape_lyrics(artistName, trackName):
    if not internet_connection():
        logger.error("No internet connection. Please check your connection.")
        return None
    if not artistName or not trackName:
        logger.error("Please provide both artist and track names.")
        return None
    if not isinstance(artistName, str) or not isinstance(trackName, str):
        logger.error("Artist and track names must be strings.")
        return None
    if not artistName.strip() or not trackName.strip():
        logger.error("Artist and track names cannot be empty.")
        return None
    if not re.match(r'^[a-zA-Z0-9\s]+$', artistName) or not re.match(r'^[a-zA-Z0-9\s]+$', trackName):
        logger.error("Artist and track names can only contain alphanumeric characters and spaces.")
        return None
    try: 
        global browser
        global trackTitle
        global trackLink
        browser = webdriver.Chrome(service=service, options=options) 
        # Inject the stealth patches
        browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
             "source": stealth_js
            })
        logger.info("Launching Genius search...")
        browser.implicitly_wait(5)
        browser.get(f'https://genius.com/search?q={artistName}+{trackName}')
        browser.maximize_window()

        logger.info(f"Searching for: '{trackName}' by {artistName}")
        if click_show_more():
            find_song_and_open(artistName, trackName)
        else:
            return
        
        lyrics = extract_lyrics()
        if lyrics:
            logger.info("Lyrics found!")
            lyricsData = {"track_title": trackTitle, 
                          'track_link': trackLink, 
                          'artist': artistName,
                            'track': trackName,
                              'lyrics': lyrics + "\n"}
            return lyricsData
        else:
            logger.error("No lyrics found.")
            return None
    except requests.ConnectionError:
        logger.error("No internet connection. Please check your connection.")
        return None
    except TimeoutException:
        logger.error("Page took too long to load. Please try again.")
        return None
    

    except Exception as e:
        logger.exception(f"An unexpected error occurred: {e}")

    finally:
        browser.quit()



# scrape_lyrics('playboi carti','crank')