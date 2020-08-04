# Google-Images-Scraper

Google-Images-Scraper allows you to download any images from Google Images.

## 1. Installation

1. Clone the repository
   ```bash
   git clone https://github.com/DGMaxime/Google-Images-Scraper.git
   ```
2. Install the required packages
   ```bash
   pip install -r requirements.txt
   ```



## 2. Basic Usage

Specify at least the search terms. You can specify one or more terms and do one or more searches. A list will be created. See examples below :

 ```bash
    > python google_images_scraping.py --search "flower"
    ['flower']
 ```
One term and one search.

 ```bash
    > python google_images_scraping.py --search "flower hat" "tea tree oil" "bird flying"
    ['flower hat', 'tea tree oil', 'bird flying']
 ```
Multiples terms and multiple searches.

## 2. Options
You can specify three options in addition to the search terms.

 ```bash
     --images     Number of images to download (int)
     --first      Position of the first images to download (int)
     --thb        Download thumbnail (True) or large images (False)
 ```
Please note that Google Images can display about 500 images at the most.