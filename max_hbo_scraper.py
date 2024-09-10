import requests
from bs4 import BeautifulSoup
import csv
from website_urls import NEW_ON_MAX_HBO_WEBSITE_URL


# Function to fetch and parse HTML content from the URL
def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print('Failed to retrieve the page')
        return None


# Function to extract content from the parsed HTML
def extract_content(soup):
    all_content = []
    shortcode_content_div = soup.find('div', class_='c-ShortcodeContent')

    if shortcode_content_div:
        # Extract the first heading and image
        current_heading = extract_first_heading(shortcode_content_div)
        if current_heading:
            all_content.append([current_heading, "", "", ""])

        first_image = extract_first_image(shortcode_content_div)
        if first_image:
            all_content.append(["", "", "", first_image])

        # Extract content until the third H2 tag
        third_h2 = get_third_h2(shortcode_content_div)
        siblings = get_siblings_before_third_h2(shortcode_content_div, third_h2)

        for sibling in siblings:
            heading, description, link, image = parse_sibling(sibling)
            all_content.append([heading, description, link, image])

    return all_content


# Function to extract the first heading
def extract_first_heading(container):
    first_h2_strong = container.find('h2').strong if container.find('h2') else None
    return first_h2_strong.get_text(strip=True) if first_h2_strong else None


# Function to extract the first image
def extract_first_image(container):
    first_figure = container.find('figure')
    if first_figure:
        img_tag = first_figure.find('img')
        if img_tag:
            return img_tag['src']
    return None


# Function to retrieve the third H2 element
def get_third_h2(container):
    h2_elements = container.find_all('h2')
    return h2_elements[2] if len(h2_elements) >= 3 else None


# Function to collect all siblings before the third H2
def get_siblings_before_third_h2(container, third_h2):
    first_figure = container.find('figure')
    siblings = []
    skip_first_p = False
    skip_first_ul = False

    for sibling in first_figure.find_next_siblings():
        if sibling.name == 'div' and 'c-commercePromo' in sibling.get('class', []):
            skip_first_p = True
            skip_first_ul = True
            continue
        if skip_first_p and sibling.name == 'p':
            skip_first_p = False
            continue
        if skip_first_ul and sibling.name == 'ul':
            skip_first_ul = False
            continue
        if sibling == third_h2:
            break
        siblings.append(sibling)

    return siblings


# Function to parse content from each sibling
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

    return heading, description, link.strip(), image


# Function to save the content to a CSV file
def save_to_csv(content, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Heading', 'Description', 'Link', 'Image'])
        for row in content:
            writer.writerow([row[0], row[1], row[2], row[3]])
    print(f"Content saved to {filename}")


# Main function to run the scraper
def scrape_max_hbo_content():
    soup = get_soup(NEW_ON_MAX_HBO_WEBSITE_URL)
    if soup:
        content = extract_content(soup)
        save_to_csv(content, 'max_hbo_website_data.csv')


# Run the scraper
if __name__ == "__main__":
    scrape_max_hbo_content()
