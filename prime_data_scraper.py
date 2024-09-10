import requests
from bs4 import BeautifulSoup
import csv
from website_urls import PRIME_WEBSITE_URL


# Function to fetch and parse the webpage
def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print('Failed to retrieve the page')
        return None


# Function to extract content from the shortcode content div
def extract_content_from_div(soup):
    all_content = []
    shortcode_content_div = soup.find('div', class_='c-ShortcodeContent')

    if shortcode_content_div:
        siblings = list(shortcode_content_div.children)
        all_content = process_siblings(siblings)

    return all_content


# Function to process sibling elements and extract relevant content
def process_siblings(siblings):
    all_content = []
    first_h2_found = False
    skip_count = 0
    skip_after_last_h2 = False

    for sibling in siblings:
        if not first_h2_found:
            if sibling.name == 'h2':
                first_h2_found = True
                first_h2_text = sibling.get_text(strip=True)
                all_content.append([first_h2_text, "", "", ""])
                continue

        if first_h2_found:
            if sibling.name == 'h2':
                all_content.append([sibling.get_text(strip=True), "", "", ""])
                skip_after_last_h2 = True
                continue

            if skip_after_last_h2:
                if skip_count < 3:
                    skip_count += 1
                    continue

            heading, description, link, image = parse_sibling(sibling)
            all_content.append([heading, description, link, image])

    return all_content


# Function to parse content from each sibling element
def parse_sibling(sibling):
    heading = ""
    description = ""
    link = ""
    image = ""
    sibling_text = ""

    if sibling.name in ['h2', 'h3', 'strong']:
        heading = sibling.get_text(strip=True)
    else:
        for part in sibling.descendants:
            if part.name == 'a' and part.get('href'):
                link_text = part.get_text(strip=True)
                link_href = part['href']
                link += f"{link_text}({link_href})\n"
            elif part.name == 'img' and part.get('src'):
                image = part['src']
            elif part.name in ['p', 'li', 'br']:
                sibling_text += "\n"
            elif part.name is None:
                sibling_text += part.strip() + " "

        description = sibling_text.strip()

    return heading, description.strip(), link.strip(), image


# Function to save the content to a CSV file
def save_to_csv(content, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Heading', 'Description', 'Link', 'Image'])
        for row in content:
            writer.writerow([row[0], row[1], row[2], row[3]])
    print(f"Content saved to {filename}")


# Main function to scrape Prime website content
def scrape_prime_content():
    soup = get_soup(PRIME_WEBSITE_URL)
    if soup:
        content = extract_content_from_div(soup)
        save_to_csv(content, 'prime_data.csv')


# Run the scraper
if __name__ == "__main__":
    scrape_prime_content()
