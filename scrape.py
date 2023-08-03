from selenium import webdriver
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys

def format_text(soup):
    # Add line breaks between different elements for minimal formatting
    for tag in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li', 'br']):
        tag.append('\n')
    return soup.get_text()

def download_page_as_text(driver, url, filename):
    try:
        driver.get(url)
        # Get the page source and extract formatted text using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text_content = format_text(soup)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text_content)
        print(f'Saved {filename} as plain text')
    except Exception as e:
        print(f'Error saving {url} as text: {e}')

def scrape_and_save_subpages(url, output_folder='text_output'):
    # Configure the Selenium web driver for Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    visited_urls = set()
    urls_to_visit = [url]

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        driver.get(current_url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Save the current page as plain text
        filename_base = urlparse(current_url).path.replace('/', '_').strip('_')
        # Remove any trailing underscores
        filename_base = filename_base.rstrip('_')
        text_file = os.path.join(output_folder, filename_base + '.txt')
        download_page_as_text(driver, current_url, text_file)

        # Find all links and add them to the list if they are on the same domain
        for link in soup.find_all('a'):
            href = link.get('href')
            if href and href.startswith('/'): # Ensure it's a relative link on the same domain
                sub_url = urljoin(current_url, href)
                if sub_url not in visited_urls:
                    urls_to_visit.append(sub_url)

    driver.quit()

if __name__ == "__main__":
    # Check if the URL is provided
    if len(sys.argv) < 2:
        print("Please provide the URL as an argument.")
        sys.exit(1)

    # Get the URL from the command-line argument
    url = sys.argv[1]

    # Start the scraping
    scrape_and_save_subpages(url)
