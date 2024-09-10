import requests
from bs4 import BeautifulSoup
import csv
from website_urls import NETFLIX_WEBSITE_URL


# Function to fetch and parse the webpage
def get_soup(url):
    response = requests.get(url)
    if response.status_code == 200:
        return BeautifulSoup(response.text, 'html.parser')
    else:
        print('Failed to retrieve the page')
        return None


# Function to extract the first and second <h2> and their content
def extract_h2_content(soup):
    all_content = []
    
    # Extract first <h2>
    first_h2 = soup.find('h2')
    if first_h2:
        first_h2_text = first_h2.get_text(strip=True)
        all_content.append([first_h2_text, "", "", ""])
        
        second_h2 = first_h2.find_next('h2')
        if second_h2:
            second_h2_text = second_h2.get_text(strip=True)
            siblings_content = get_siblings_between_h2(first_h2, second_h2)
            all_content.extend(siblings_content)
            all_content.append([second_h2_text, "", "", ""])
            
            following_siblings_content = get_following_siblings(second_h2)
            all_content.extend(following_siblings_content)
    
    return all_content


# Function to get siblings between two <h2> tags
def get_siblings_between_h2(first_h2, second_h2):
    siblings_content = []
    siblings = []

    # Collect siblings between first and second <h2>
    for sibling in first_h2.find_next_siblings():
        if sibling == second_h2:
            break
        siblings.append(sibling)

    # Remove last 2 siblings, if present
    if len(siblings) >= 2:
        siblings = siblings[:-2]

    for sibling in siblings:
        heading, description, link, image = parse_sibling(sibling)
        siblings_content.append([heading, description, link, image])

    return siblings_content


# Function to get siblings following the second <h2>
def get_following_siblings(second_h2):
    following_siblings_content = []
    following_siblings = []

    for sibling in second_h2.find_next_siblings():
        following_siblings.append(sibling)

    # Skip first 4 siblings, if present
    if len(following_siblings) >= 4:
        following_siblings = following_siblings[4:]

    for sibling in following_siblings:
        heading, description, link, image = parse_sibling(sibling)
        following_siblings_content.append([heading, description, link, image])

    return following_siblings_content


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

    return heading, description, link.strip(), image


# Function to save the content to a CSV file
def save_to_csv(content, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Heading', 'Description', 'Link', 'Image'])
        for row in content:
            writer.writerow([row[0], row[1], row[2], row[3]])
    print(f"Content saved to {filename}")


# Main function to scrape Netflix content
def scrape_netflix_content():
    soup = get_soup(NETFLIX_WEBSITE_URL)
    if soup:
        content = extract_h2_content(soup)
        save_to_csv(content, 'netflix_data.csv')


# Run the scraper
if __name__ == "__main__":
    scrape_netflix_content()
