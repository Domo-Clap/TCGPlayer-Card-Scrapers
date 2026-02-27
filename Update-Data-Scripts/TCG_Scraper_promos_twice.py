from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
from datetime import date, timedelta
import pandas as pd


def TransformToDF(CardDict):

    data = []

    for cardName, d in CardDict.items():
        inventoryPrice = d.get('Inventory Price', None)
        marketPrice = d.get('Market Price', None)
        cardSetName = d.get('Set Name', None)

        data.append([cardName, inventoryPrice, marketPrice, cardSetName])


    df = pd.DataFrame(data, columns=["Card Name", "Inventory Price", "Market Price", "Set Name"])

    df["Inventory Price"] = (
        pd.to_numeric(
            df["Inventory Price"].astype(str)
            .str.replace(r'[^\d\.\-]', '', regex=True),
            errors="coerce"
        )
        .fillna(0.00)
        .round(2)
    )

    df["Market Price"] = (
        pd.to_numeric(
            df["Market Price"].astype(str)
            .str.replace(r'[^\d\.\-]', '', regex=True),
            errors="coerce"
        )
        .fillna(0.00)
        .round(2)
    )

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
def StartScrape(promoGroupURL, setName, startingPage):

    # Creates a class object to call the scrape actual selenium scrape functions
    scraper = GetOnePieceInfo()

    # Assigns the url to pass in
    base_URL = promoGroupURL

    try:
        # Start at Page 1 of the cards
        page_num = startingPage

        # Loops until there are no more pages with card objects onm them
        while scraper.loop_var:

            if page_num >= (startingPage + 8):
                break

            page_url = f"{base_URL}?view=grid&productLineName=one-piece-card-game&setName={setName}&ProductTypeName=Cards&CardType=Leader|Event|Character|Stage&page={page_num}"

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
    goodData = TransformToDF(scraper.cardDict)

    # Returns our final df for the set of cards
    return goodData


# Main function
if __name__ == '__main__':

    Promos1 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/one-piece-promotion-cards", "one-piece-promotion-cards", 1)
    time.sleep(60)
    Promos2 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/one-piece-promotion-cards", "one-piece-promotion-cards", 9)
    time.sleep(60)
    Promos3 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/one-piece-promotion-cards", "one-piece-promotion-cards", 17)
    time.sleep(60)
    Promos4 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/one-piece-promotion-cards", "one-piece-promotion-cards", 25)
    time.sleep(60)
    Promos5 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/one-piece-promotion-cards", "one-piece-promotion-cards", 33)

    finalDF = pd.concat([Promos1, Promos2, Promos3, Promos4, Promos5])
    print(finalDF.count())
