import requests
from bs4 import BeautifulSoup
import csv
from website_urls import NEW_ON_HULU_WEBSITE_URL


# Function to fetch and parse the HTML content from the URL
def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print('Failed to retrieve the page')
        return None


# Function to extract the content from the webpage
def extract_content(soup):
    all_content = []
    shortcode_content_div = soup.find('div', class_='c-ShortcodeContent')

    if shortcode_content_div:
        current_heading = ""

        # Extract first heading and first image
        first_h2_strong = shortcode_content_div.find('h2').strong if shortcode_content_div.find('h2') else None
        if first_h2_strong:
            current_heading = first_h2_strong.get_text(strip=True)
            all_content.append([current_heading, "", "", ""])

        first_figure = shortcode_content_div.find('figure')
        if first_figure:
            img_tag = first_figure.find('img')
            if img_tag:
                all_content.append(["", "", "", img_tag['src']])

        last_h2 = shortcode_content_div.find_all('h2')[-1] if shortcode_content_div.find_all('h2') else None

        # Loop through the siblings to extract headings, descriptions, links, and images
        for sibling in first_figure.find_next_siblings():
            if sibling == last_h2:
                break

            heading = ""
            description = ""
            link = ""
            image = ""
            sibling_text = ""

            if sibling.name in ['h2', 'h3', 'strong']:
                heading = sibling.get_text(strip=True)
                all_content.append([heading, "", "", ""])
                continue

            # Extract text, links, and images from the sibling
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
            all_content.append([heading, description.strip(), link.strip(), image])

    return all_content


# Function to save the extracted content to a CSV file
def save_to_csv(content, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Heading', 'Description', 'Link', 'Image'])
        for row in content:
            writer.writerow([row[0], row[1], row[2], row[3]])
    print(f"Content saved to {filename}")


# Main function to run the scraper
def scrape_hulu_content():
    soup = get_soup(NEW_ON_HULU_WEBSITE_URL)
    if soup:
        content = extract_content(soup)
        save_to_csv(content, 'hulu_website_data.csv')


# Run the scraper
if __name__ == "__main__":
    scrape_hulu_content()
