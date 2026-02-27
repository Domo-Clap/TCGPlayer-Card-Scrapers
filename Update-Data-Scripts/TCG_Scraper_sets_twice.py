from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import date, timedelta
import pandas as pd


def TransformToDF(CardDict, setNum):
    data = []
    for cardName, d in CardDict.items():
        inventoryPrice = d.get('Inventory Price', None)
        marketPrice = d.get('Market Price', None)
        cardSetName = d.get('Set Name', None)

        data.append([cardName, inventoryPrice, marketPrice, cardSetName, setNum])

    df = pd.DataFrame(data, columns=["Card Name", "Inventory Price", "Market Price", "Set Name", "Set ID"])

    df["Inventory Price"] = df["Inventory Price"].str.replace("[\$,]", "", regex=True).astype(float).round(2)
    df["Market Price"] = df["Market Price"].str.replace("[\$,]", "", regex=True).astype(float).round(2)

    df['Date'] = date.today().strftime('%Y-%m-%d')

    return df


########################################################################################################################
########################################################################################################################
########################################################################################################################
class GetOnePieceInfo:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
        # Web Driver used to connect to our website
        self.driver = webdriver.Chrome(options=chrome_options)

        # Holds the cards for the current set, alongside the wanted info
        self.cardDict = {}

        self.loop_var = True

    def get_cards(self, page_url):

        try:
            self.driver.get(page_url)

            WebDriverWait(self.driver, 30).until(
                lambda d: len(d.find_elements(By.CLASS_NAME, "product-card__product")) > 10
            )

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            page_text = self.driver.page_source.lower()

            block_signals = [
                "access denied",
                "unusual activity",
                "temporarily blocked",
                "verify you are human",
                "request blocked"
            ]

            if any(signal in page_text for signal in block_signals):
                self.loop_var = False
                return

            all_cards = self.driver.find_elements(By.CLASS_NAME, "product-card__product")

            if not all_cards or len(all_cards) < 5:
                self.loop_var = False
                return

            for card in all_cards:
                card_name = card.find_element(By.CLASS_NAME, "product-card__title")
                card_price = card.find_element(By.CLASS_NAME, "inventory__price-with-shipping")
                card_mprice = card.find_element(By.CLASS_NAME, "product-card__market-price--value")
                card_set_name = card.find_element(By.CLASS_NAME, "product-card__set-name__variant")

                cName = card_name.text.strip()
                cPrice = card_price.text.strip()
                cMPrice = card_mprice.text.strip()
                cSetName = card_set_name.text.strip()

                self.cardDict[cName] = {"Inventory Price": cPrice, "Market Price": cMPrice, "Set Name": cSetName}

            print(self.cardDict)

        except Exception as e:
            print(f"Exception occurred: {e}")
            self.loop_var = False
            return

    # Makes it easier to stop the webdriver
    def stopDriver(self):
        self.driver.quit()


########################################################################################################################
########################################################################################################################
########################################################################################################################
# Function used to start the web scraping process. Is called in the main function
# Takes in the webpage URL to scrape, as well as the name of the card set, and the number/string associated with the set
# Will run through every page with card objects on the webpage until there are no more.
def StartScrape(setURL, setName, setNum):
    # Creates a class object to call the scrape actual selenium scrape functions
    scraper = GetOnePieceInfo()

    # Assigns the url to pass in
    base_URL = setURL

    try:

        # Start at Page 1 of the cards
        page_num = 1

        # Loops until there are no more pages with card objects onm them
        while scraper.loop_var:
            page_url = f"{base_URL}?view=grid&productLineName=one-piece-card-game&setName={setName}&page={page_num}&productTypeName=Cards&CardType=Character|Event|Stage|Leader"

            if page_num == 19 and (setName == 'premium-booster-the-best' or setName == 'premium-booster-the-best-vol-2'):
                break

            if page_num == 10 and (setName in ["the-azure-seas-seven"]):
                break

            if page_num == 8 and (setName in ["romance-dawn", "paramount-war", "pillars-of-strength", "kingdoms-of-intrigue", "awakening-of-the-new-era", "wings-of-the-captain", "500-years-in-the-future", "two-legends", "emperors-in-the-new-world", "royal-blood", "a-fist-of-divine-speed", "legacy-of-the-master", "carrying-on-his-will"]):
                break

            if page_num == 7 and (setName in ['extra-booster-memorial-collection', 'extra-booster-anime-25th-collection']):
                break

            

            # Pulls in the data for the cards by using the dict from the scraper object
            scraper.get_cards(page_url)

            time.sleep(5)
            
            page_num += 1

    except KeyboardInterrupt:
        print("Interrupted by user, stopping....")

    # Stops the driver for the current card set
    finally:
        scraper.stopDriver()

    # Moves the returned card dict to a pandas df
    goodData = TransformToDF(scraper.cardDict, setNum)

    # Returns our final df for the set of cards
    return goodData


# Main function
if __name__ == '__main__':

    setsToRead = {
        "OP01": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/romance-dawn",
            "set_name": "romance-dawn",
            "set_id": "OP-01",
        },
        "OP02": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/paramount-war",
            "set_name": "paramount-war",
            "set_id": "OP-02",
        },
        "OP03": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/pillars-of-strength",
            "set_name": "pillars-of-strength",
            "set_id": "OP-03",
        },
        "OP04": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/kingdoms-of-intrigue",
            "set_name": "kingdoms-of-intrigue",
            "set_id": "OP-04",
        },
        "OP05": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/awakening-of-the-new-era",
            "set_name": "awakening-of-the-new-era",
            "set_id": "OP-05",
        },
        "OP06": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/wings-of-the-captain",
            "set_name": "wings-of-the-captain",
            "set_id": "OP-06",
        },
        "OP07": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/500-years-in-the-future",
            "set_name": "500-years-in-the-future",
            "set_id": "OP-07",
        },
        "OP08": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/two-legends",
            "set_name": "two-legends",
            "set_id": "OP-08",
        },
        "OP09": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/emperors-in-the-new-world",
            "set_name": "emperors-in-the-new-world",
            "set_id": "OP-09",
        },
        "OP10": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/royal-blood",
            "set_name": "royal-blood",
            "set_id": "OP-10",
        },
        "OP11": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/a-fist-of-divine-speed",
            "set_name": "a-fist-of-divine-speed",
            "set_id": "OP-11",
        },
        "OP12": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/legacy-of-the-master",
            "set_name": "legacy-of-the-master",
            "set_id": "OP-12",
        },
        "OP13": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/carrying-on-his-will",
            "set_name": "carrying-on-his-will",
            "set_id": "OP-13",
        },
        "OP14": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/the-azure-seas-seven",
            "set_name": "the-azure-seas-seven",
            "set_id": "OP14-EB04",
        },
        "EB01": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/extra-booster-memorial-collection",
            "set_name": "extra-booster-memorial-collection",
            "set_id": "EB-01",
        },
        "EB02": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/extra-booster-anime-25th-collection",
            "set_name": "extra-booster-anime-25th-collection",
            "set_id": "EB-02",
        },
        "EB03" : {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/extra-booster-one-piece-heroines-edition",
            "set_name": "extra-booster-one-piece-heroines-edition",
            "set_id": "EB-03",
        },
        "PRB01": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/premium-booster-the-best",
            "set_name": "premium-booster-the-best",
            "set_id": "PRB-01",
        },
        "PRB02": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/premium-booster-the-best-vol-2",
            "set_name": "premium-booster-the-best-vol-2",
            "set_id": "PRB-02",
        },
    }

    setCounter = 0
    setDFs = []

    for key, cardSet in setsToRead.items():

        setCounter += 1

        # Want to reset each 4 sets
        if (setCounter % 4 == 0):

            print()
            time.sleep(60)


        url = cardSet["url"]
        setName = cardSet["set_name"]
        setID = cardSet["set_id"]

        df = StartScrape(url, setName, setID)

        if df is not None:
            setDFs.append(df)

        time.sleep(30)

    print(f"Here is the set counter after running through the loop: {setCounter}")
    
    finalDF = pd.concat(setDFs, ignore_index=True)
