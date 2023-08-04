from selenium import webdriver
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import sys
import re

def format_text(soup, classes):
    """Extract and format text from elements with the specified classes."""
    text_content = []
    for class_name in classes:
        for element in soup.find_all(class_=class_name):
            text_content.append(element.get_text())
    text_content = '\n'.join(text_content)
    text_content = re.sub(r'[^\w\s.,?!;:\-\'"]+', '', text_content)
    return text_content

def download_page_as_text(driver, url, filename, classes):
    """Download a web page as a plain text file."""
    try:
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        text_content = format_text(soup, classes)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(text_content)
        print(f'Saved {filename} as plain text')
    except Exception as e:
        print(f'Error saving {url} as text: {e}')

def scrape_and_save_subpages(url, classes, output_folder='text_output'):
    """Scrape and save subpages from the given URL as text files."""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(options=options)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    visited_urls = set()
    urls_to_visit = [url]

    while urls_to_visit:
        current_url = urls_to_visit.pop()
        if current_url in visited_urls:
            continue

        visited_urls.add(current_url)

        filename_base = urlparse(current_url).path.replace('/', '_').strip('_')
        filename_base = filename_base.rstrip('_')
        text_file = os.path.join(output_folder, filename_base + '.txt')

        download_page_as_text(driver, current_url, text_file, classes)

        for link in BeautifulSoup(driver.page_source, 'html.parser').find_all('a'):
            href = link.get('href')
            if href and href.startswith('/'):
                sub_url = urljoin(current_url, href)
                if sub_url not in visited_urls:
                    urls_to_visit.append(sub_url)

    driver.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide the URL as the first argument.")
        sys.exit(1)

    url = sys.argv[1]
    # Get the classes from the command-line argument, or use the default
    classes = sys.argv[2].split(',') if len(sys.argv) > 2 else ['theme-doc-markdown']

    scrape_and_save_subpages(url, classes)
