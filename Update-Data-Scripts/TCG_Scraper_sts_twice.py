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

            #WebDriverWait(self.driver, 20).until(
                #EC.visibility_of_element_located((By.CLASS_NAME, "product-card__product")))

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
            page_url = f"{base_URL}?view=grid&productLineName=one-piece-card-game&setName={setName}&page={page_num}&CardType=Character|Event|Leader|Stage"

            if page_num == 2:
                break

            # Pulls in the data for the cards by using the dict from the scraper object
            scraper.get_cards(page_url)
        
            time.sleep(10)

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
    decksToRead = {
        "ST01": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-1-straw-hat-crew",
            "set_name": "starter-deck-1-straw-hat-crew",
            "set_id": "ST-01"
        },
        "ST02": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-2-worst-generation",
            "set_name": "starter-deck-2-worst-generation",
            "set_id": "ST-02"
        },
        "ST03": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-3-the-seven-warlords-of-the-sea",
            "set_name": "starter-deck-3-the-seven-warlords-of-the-sea",
            "set_id": "ST-03"
        },
        "ST04": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-4-animal-kingdom-pirates",
            "set_name": "starter-deck-4-animal-kingdom-pirates",
            "set_id": "ST-04"
        },
        "ST05": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-5-film-edition",
            "set_name": "starter-deck-5-film-edition",
            "set_id": "ST-05"
        },
        "ST06": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-6-absolute-justice",
            "set_name": "starter-deck-6-absolute-justice",
            "set_id": "ST-06"
        },
        "ST07": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-7-big-mom-pirates",
            "set_name": "starter-deck-7-big-mom-pirates",
            "set_id": "ST-07"
        },
        "ST08": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-8-monkeydluffy",
            "set_name": "starter-deck-8-monkeydluffy",
            "set_id": "ST-08"
        },
        "ST09": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-9-yamato",
            "set_name": "starter-deck-9-yamato",
            "set_id": "ST-09"
        },
        "ST10": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/ultra-deck-the-three-captains",
            "set_name": "ultra-deck-the-three-captains",
            "set_id": "ST-10"
        },
        "ST11": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-11-uta",
            "set_name": "starter-deck-11-uta",
            "set_id": "ST-11"
        },
        "ST12": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-12-zoro-and-sanji",
            "set_name": "starter-deck-12-zoro-and-sanji",
            "set_id": "ST-12"
        },
        "ST13": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/ultra-deck-the-three-brothers",
            "set_name": "ultra-deck-the-three-brothers",
            "set_id": "ST-13"
        },
        "ST14": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-14-3d2y",
            "set_name": "starter-deck-14-3d2y",
            "set_id": "ST-14"
        },
        "ST15": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-15-red-edwardnewgate",
            "set_name": "starter-deck-15-red-edwardnewgate",
            "set_id": "ST-15"
        },
        "ST16": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-16-green-uta",
            "set_name": "starter-deck-16-green-uta",
            "set_id": "ST-16"
        },
        "ST17": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-17-blue-donquixote-doflamingo",
            "set_name": "starter-deck-17-blue-donquixote-doflamingo",
            "set_id": "ST-17"
        },
        "ST18": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-18-purple-monkeydluffy",
            "set_name": "starter-deck-18-purple-monkeydluffy",
            "set_id": "ST-18"
        },
        "ST19": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-19-black-smoker",
            "set_name": "starter-deck-19-black-smoker",
            "set_id": "ST-19"
        },
        "ST20": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-20-yellow-charlotte-katakuri",
            "set_name": "starter-deck-20-yellow-charlotte-katakuri",
            "set_id": "ST-20"
        },
        "ST21": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-ex-gear-5",
            "set_name": "starter-deck-ex-gear-5",
            "set_id": "ST-21"
        },
        "ST22": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-22-ace-and-newgate",
            "set_name": "starter-deck-22-ace-and-newgate",
            "set_id": "ST-22"
        },
        "ST23": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-23-red-shanks",
            "set_name": "starter-deck-23-red-shanks",
            "set_id": "ST-23"
        },
        "ST24": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-24-green-jewelry-bonney",
            "set_name": "starter-deck-24-green-jewelry-bonney",
            "set_id": "ST-24"
        },
        "ST25": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-25-blue-buggy",
            "set_name": "starter-deck-25-blue-buggy",
            "set_id": "ST-25"
        },
        "ST26": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-26-purple-black-monkeydluffy",
            "set_name": "starter-deck-26-purple-black-monkeydluffy",
            "set_id": "ST-26"
        },
        "ST27": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-27-black-marshalldteach",
            "set_name": "starter-deck-27-black-marshalldteach",
            "set_id": "ST-27"
        },
        "ST28": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-28-green-yellow-yamato",
            "set_name": "starter-deck-28-green-yellow-yamato",
            "set_id": "ST-28"
        },
        "ST29": {
            "url": "https://www.tcgplayer.com/search/one-piece-card-game/starter-deck-29-egghead",
            "set_name": "starter-deck-29-egghead",
            "set_id": "ST-29"
        },
    }

    setCounter = 0
    stDFs = []

    for key, cardSet in decksToRead.items():

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
            stDFs.append(df)

        time.sleep(30)

    finalDF = pd.concat(stDFs, ignore_index=True)
