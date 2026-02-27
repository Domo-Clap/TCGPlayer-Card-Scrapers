from datetime import date
from selenium.common import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
import time
import pandas as pd

########################################################################################################################
########################################################################################################################
########################################################################################################################
def TransformToDF(CardDict, setNum, setName):
    data = []

    for cardName, d in CardDict.items():
        inventoryPrice = d.get('Inventory Price', None)
        marketPrice = d.get('Market Price', None)
        cardSetName = d.get('Set Name', None)
        cardText = d.get('Card Text', None)
        rarity = d.get('Rarity', None)
        cardSID = d.get('Card Set ID', None)
        cardColor = d.get('Card Color', None)
        cardType = d.get('Card Type', None)
        leaderLife = d.get('Life', None)
        cardCost = d.get('Card Cost', None)
        cardPower = d.get('Card Power', None)
        subTypes = d.get('SubTypes', None)
        counterAmnt = d.get('Counter', 0)
        attrib = d.get('Attribute', None)

        print(str(cardSetName).strip())
        print(str(setName).strip())

        if str(cardSetName).strip() == 'Extra Booster: One Piece Heroines Edition':
            data.append(
                [cardName, inventoryPrice, marketPrice, cardSetName, cardText, setNum, rarity, cardSID, cardColor, cardType,
                leaderLife, cardCost, cardPower, subTypes, counterAmnt, attrib])


    df = pd.DataFrame(data, columns=["Card Name", "Inventory Price", "Market Price", "Set Name", "Card Text", "Set ID",
                                     "Rarity",
                                     "Card Set ID", "Card Color", "Card Type", "Life", "Card Cost", "Card Power",
                                     "Sub Types", "Counter Amount",
                                     "Attribute"])

    df["Inventory Price"] = df["Inventory Price"].str.replace("[\$,]", "", regex=True).astype(float).round(2)
    df["Market Price"] = df["Market Price"].str.replace("[\$,]", "", regex=True).astype(float).round(2)

    df['Date_Scraped'] = date.today().strftime('%Y-%m-%d')

    return df


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

        # All of the structure dicts are different because of the way the data is formatted on the specific sites we scrape from
        # character card sites have slightly different data compared to the leader card sites, etc...

        # Dict used to assign the data for character cards
        self.charStructDict_counter = {
            0: "Card Name",
            1: "Inventory Price",
            2: "Market Price",
            3: "Set Name",
            4: "Card Text",
            5: "Rarity",
            6: "Card Set ID",
            7: "Card Color",
            8: "Card Type",
            9: "Card Cost",
            10: "Card Power",
            11: "SubTypes",
            12: "Counter",
            13: "Attribute"
        }

        self.charStructDict_no_counter = {
            0: "Card Name",
            1: "Inventory Price",
            2: "Market Price",
            3: "Set Name",
            4: "Card Text",
            5: "Rarity",
            6: "Card Set ID",
            7: "Card Color",
            8: "Card Type",
            9: "Card Cost",
            10: "Card Power",
            11: "SubTypes",
            12: "Attribute"
        }

        # Dict used to assign the data for leader cards
        self.leaderStructDict = {
            0: "Card Name",
            1: "Inventory Price",
            2: "Market Price",
            3: "Set Name",
            4: "Card Text",
            5: "Rarity",
            6: "Card Set ID",
            7: "Card Color",
            8: "Card Type",
            9: "Life",
            10: "Card Power",
            11: "SubTypes",
            12: "Attribute"
        }

        # Dict used to assign the data for the event cards
        self.eventStructDict = {
            0: "Card Name",
            1: "Inventory Price",
            2: "Market Price",
            3: "Set Name",
            4: "Card Text",
            5: "Rarity",
            6: "Card Set ID",
            7: "Card Color",
            8: "Card Type",
            9: "Card Cost",
            10: "SubTypes"
        }

        self.stageStructDict = {
            0: "Card Name",
            1: "Inventory Price",
            2: "Market Price",
            3: "Set Name",
            4: "Card Text",
            5: "Rarity",
            6: "Card Set ID",
            7: "Card Color",
            8: "Card Type",
            9: "Card Cost",
            10: "SubTypes"
        }

    # Function used to get the cards from the specific website. Runs through a loop that gets all of the elements from the specifc set/page of the set
    def get_cards(self, page_url):

        try:
            self.driver.get(page_url)

            # Wait until all cards from the indiv page are loaded in
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.CLASS_NAME, "product-card__product")))

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

            # Used to track if we can move to the next page and where we are when we regrab the page to avoid stale elements
            cardLoopVar = 0

            while True:
                # Get all of the cards on the current page
                all_cards = self.driver.find_elements(By.CLASS_NAME, "product-card__product")

                if cardLoopVar >= len(all_cards):
                    break

                try:

                    # Get the card name, price, marketprice, and set name before going into the details page of each card
                    card_name = all_cards[cardLoopVar].find_element(By.CLASS_NAME, "product-card__title")

                    try:
                        card_price = all_cards[cardLoopVar].find_element(By.CLASS_NAME, "inventory__price-with-shipping")

                    except NoSuchElementException:
                        card_price = None

                    try:
                        card_mprice = all_cards[cardLoopVar].find_element(By.CLASS_NAME, "product-card__market-price--value")

                    except NoSuchElementException:
                        card_mprice = None

                    card_set_name = all_cards[cardLoopVar].find_element(By.CLASS_NAME, "product-card__set-name__variant")

                    # Gets the text for each element
                    cName = card_name.text.strip()

                    if cName == 'Five Elders (Alternate Art)' or cName == 'Five Elders':
                        cardLoopVar += 1
                        continue

                    if card_price is not None:
                        cPrice = card_price.text.strip()

                    if card_mprice is not None:
                        cMPrice = card_mprice.text.strip()

                    cSetName = card_set_name.text.strip()

                    # places them in our individual card/object dict
                    card_details = {
                        "Inventory Price": cPrice,
                        "Market Price": cMPrice,
                        "Set Name": cSetName
                    }

                    # Finds the first card in the all_cards list for the page. Then, clicks on it to locate to the next page

                    title_el = all_cards[cardLoopVar].find_element(
                        By.CLASS_NAME, "product-card__title"
                    )

                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        title_el
                    )
                    time.sleep(0.5)
                    self.driver.execute_script("arguments[0].click();", title_el)
                    #all_cards[cardLoopVar].find_element(By.CLASS_NAME, "product-card__title").click()

                    # Waits until the card details are on page
                    WebDriverWait(self.driver, 10).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "product-details__name")))

                    time.sleep(2)

                    try:
                        card_text = self.driver.find_element(By.CLASS_NAME, "product__item-details__description")

                    except NoSuchElementException:
                        card_text = None

                    if card_text is not None:
                        card_text = card_text.text.strip()

                    card_details["Card Text"] = card_text

                    # Gets the unordered list on each card detail page
                    detailUL = self.driver.find_element(By.CLASS_NAME, "product__item-details__attributes")

                    # Gets the span elements inside the unordered list
                    span_elements = detailUL.find_elements(By.TAG_NAME, "span")

                    # print(span_elements)

                    card_type = None

                    # Looks at each card detail in the span_elements list
                    # Then, we compare the text value of the span/card detail to see what type of card it is
                    for span in span_elements:

                        # position 8 in dict is counter. if character card and the value of the span is not 0 and is equal to the key Counter
                        if 'character' == span.text.lower():

                            try:
                                counter_val = int(span_elements[7].text)
                                if counter_val > 0:
                                    card_type = "Character with Counter"
                                else:
                                    card_type = "Character without Counter"
                            except ValueError:
                                card_type = "Character without Counter"

                            break

                        elif 'event' == span.text.lower():
                            card_type = "Event"
                            break

                        elif 'leader' == span.text.lower():
                            card_type = "Leader"
                            break

                        elif 'stage' == span.text.lower():
                            card_type = "Stage"
                            break

                    # Next, we get all of the card details from the card page, and assign them to the specific dictionary
                    # depending on the card type we scanned for earlier
                    for index, span in enumerate(span_elements):

                        if card_type == "Character with Counter" and (index + 5) in self.charStructDict_counter:

                            key = self.charStructDict_counter[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                        elif card_type == "Character without Counter" and (index + 5) in self.charStructDict_no_counter:

                            key = self.charStructDict_no_counter[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                        elif card_type == "Event" and (index + 5) in self.eventStructDict:

                            key = self.eventStructDict[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                        elif card_type == "Leader" and (index + 5) in self.leaderStructDict:

                            key = self.leaderStructDict[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                        elif card_type == "Stage" and (index + 5) in self.stageStructDict:

                            key = self.stageStructDict[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                        else:

                            key = self.charStructDict_counter[index + 5]
                            value = span.text.strip()

                            card_details[key] = value

                    print(card_details)

                    self.cardDict[cName] = card_details

                    time.sleep(2)

                    # Goes back to main card page
                    self.driver.back()

                    WebDriverWait(self.driver, 20).until(
                        EC.visibility_of_element_located((By.CLASS_NAME, "product-card__product")))


                except Exception as e:
                    print(f"error: {e}")
                    continue

                cardLoopVar += 1

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
            # Pulls in the data for the cards by using the dict from the scraper object
            scraper.get_cards(page_url)

            time.sleep(5)

            page_num += 1

            if page_num == 15 and (setName == 'premium-booster-the-best' or setName == 'premium-booster-the-best-vol-2'):
                break

            if page_num == 6:
                break

    except KeyboardInterrupt:
        print("Interrupted by user, stopping....")

    # Stops the driver for the current card set
    finally:
        scraper.stopDriver()

    # Moves the returned card dict to a pandas df
    goodData = TransformToDF(scraper.cardDict, setNum, setName)

    print(goodData.count())

    # Returns our final df for the set of cards
    return goodData


# Main function
if __name__ == '__main__':
    EB03 = StartScrape("https://www.tcgplayer.com/search/one-piece-card-game/extra-booster-one-piece-heroines-edition", "extra-booster-one-piece-heroines-edition", "EB-03")

    finalDF = pd.concat([EB03])
    print(finalDF)
    print(finalDF.count())
