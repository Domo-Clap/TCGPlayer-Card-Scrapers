# TCGPlayer-Card-Scrapers
TCGPlayer is a website that allows users to buy and sell cards for popular games like Pokemon, YuGiOh, Magic the Gathering, One Piece TCG, and many more. This repo contains a few scripts built to scrape data from TCGPlayer, specifically for the One Piece Card Game.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# Script Design
These scripts are built in Python and utilize Selenium for web scraping, and pandas for storing everything in one dataframe. These scripts are used normally to grab prices bi-daily from TCG-Player, and should work for the most part.

The scripts utilize a good amount of time.sleep() calls to make it seem like an actual user is browsing. The dictionaries in the internal getCards function (Specifically in the Full data scipts) are meant for the One Piece Card Game and have data points relative to it. These scripts can most likely be worked on to pull for pretty much any items on TCGPlayer.

There are two versions for each script:

  1. Full data grabbing script (Clicks into each card individually and grabs the data from it)
  2. Update data script (Does not click into each card. Grabs the price values directly from the usual page where 30 cards are shown)

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

# How to Setup and Run


