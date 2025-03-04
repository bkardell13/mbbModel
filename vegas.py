import requests
from bs4 import BeautifulSoup


# def scrape_lines(game_id):
#     return "USA -13.5", "133.5"

def scrape_lines(game_id):
    
    url_base = "https://www.espn.com/mens-college-basketball/game/_/gameId/"
    url = url_base + str(game_id)
    

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.5672.64 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers)
        
        response.raise_for_status()
        
        html_content_1 = response.text
        # print("HTML content retrieved successfully!")
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")  # Print HTTP error message
    except Exception as err:
        print(f"An error occurred: {err}")  # Print other errors (e.g., connection issues)


    soup = BeautifulSoup(html_content_1, "html.parser")
    # pretty_soup = soup.prettify()
    # with open("example.txt", "w") as file:
    #     # Write text to the file
    #     file.write(pretty_soup)
        
    line_section = soup.find("div", class_="ScoreCell__Odds")
    # line = soup.find("div", class_="ScoreCell__Odds")
    line = line_section.get_text(strip=True)
    # print(line)


    divs = soup.find_all("div", {"class": "nfCSQ iygLn FuEs", "id": "topOdds"})
    total_section = ""
    # this total section only returns what the total OPENED at
    # print(divs)
    for div in divs: 
        # print(div)
        text_content = div.get_text().strip()  # Extract the text and remove any surrounding whitespace
        if 'u' in text_content or 'o' in text_content:
            total_section = div
            # print("Found the correct div:", total_section)
            break  # Exit the loop once you find the matching div
    
    if total_section == "":
        print("TOTAL SECTION ERROR")

    # total_section = soup.find("div", {"class": "rIczU iygLn FuEs", "id": "topOdd"})
    # print(total_section)
    # print(total_section)
    total_raw = total_section.get_text(strip=True)
    # print(total_raw)
    total = total_raw.replace('u', '').replace('o', '')
    # print(total)


    return str(line), total

