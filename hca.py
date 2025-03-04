from bs4 import BeautifulSoup

def find_hca(team_name_given):

    # Load your HTML content
    with open("hca.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the table containing the data
    ratings_table = soup.find("table", {"id": "ratings-table"})

    # Extract rows from the table body
    rows = ratings_table.find("tbody").find_all("tr")
    # print(rows)
    # Prepare a list to store the data
    teams_data = []

    # Loop through each row to extract data
    for row in rows:
        # print(row)
        columns = row.find_all("td")
        try:
            team_name = columns[0].text.strip()  # First column - team name throwing error every 40 teams
        except:
            continue
        conference = columns[1].text.strip()  # Second column - conference
        hca = columns[2].text.strip()  # Home Court Advantage
        pf = columns[4].text.strip()  # PF advantage
        pts = columns[6].text.strip()  # Points advantage
        nst = columns[8].text.strip()  # NST advantage
        blk = columns[10].text.strip()  # Block advantage
        elev = columns[12].text.strip()  # Elevation advantage
        
        # Store data in a dictionary
        team_data = {
            "Team": team_name,
            "Conference": conference,
            "HCA": hca,
            "PF Advantage": pf,
            "Points Advantage": pts,
            "NST Advantage": nst,
            "Block Advantage": blk,
            "Elevation Advantage": elev,
        }
        teams_data.append(team_data)

    # Print the extracted data
    # print(team_name_given)
    for team in teams_data:
        # print(team['Team'])
        # print(team_name_given)
        if team_name_given == team['Team']:
            return team['HCA']
        
    return "ERROR"



# print(find_hca("Nebraska"))