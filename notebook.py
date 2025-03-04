from vegas import scrape_lines  # Import the function from file1.py
import csv
from openpyxl import load_workbook
from datetime import datetime

def find_lines(a,b,c):
    return "Alabama State -3.5", "145.5"
   

def find_lines(team1, team2, team1_sched):
    team1_return = team1 # Capitalization for returning 
    team2_return = team2
    team1 = team1.upper()
    team2 = team2.upper()

    game_id = find_game_id(team1_sched)
    vegas_line, vegas_total = scrape_lines(game_id)
    vegas_line_team, vegas_line_num = vegas_line.split()
    # print(vegas_line_team)
    # print(vegas_line_num)
    # print(list(vegas_line_team))
    with open("possible_team_names.csv", 'r') as file:
        csv_reader = csv.reader(file)
        header = next(csv_reader) # Skip the header row
        for row in csv_reader:
            # print(row)
            if vegas_line_team == row[3]: #team is favored
               vegas_line = row[0] + " " + vegas_line_num
               break
               

    # valid = True
    # for letter in list(vegas_line_team):
    #   if (letter not in team1):
    #     # print("not valid because letter is " + letter + " and team name is: " + team1)
    #     valid = False
      # else:
      #   print("valid because letter is " + letter + " and team name is: " + team1)

    # if valid == True:
    #   vegas_line = team1_return + " " + vegas_line_num
      # print("line being changed")

    # else:
    #   valid = True
    #   for letter in list(vegas_line_team):
    #     if (letter not in team2) and (letter != "U"):
    #       # print("not valid because letter is " + letter + " and team name is: " + team2)
    #       valid = False
    #     # else:
    #     #   print("valid because letter is " + letter + " and team name is: " + team2)

    #   if valid == True:
    #     vegas_line = team2_return + " " + vegas_line_num

    return vegas_line,vegas_total

def find_game_id(team_sched):
    team_sched.seek(0)
    team1_reader = csv.reader(team_sched)
    # print(team1_reader)
    next(team1_reader)
    for row in team1_reader:
      if row[4] == "NA":
        game_id = row[0]
        break # find the first game that has not been played, that is the game Id i need to scrape for the lines
    return game_id

def write_to_notes_files(team1, team2, team1_pts, team2_pts, game_confidence, location, degree, vegas_line, vegas_total, game_id, version):
    if location == "Standard":
      val = "@"
    elif location == "Neutral":
      val = "vs"
    notes = open('./notes_transition.txt', 'a')
    notes.write("\n")
    notes.write(f'{team2} {val} {team1} (deg {degree}) (gameid {game_id}) (date {datetime.now().strftime("%m/%d/%Y")}) (version {version})\n')
    notes.write("\n")
    notes.write(f"\tprediction: {team1} {round(team1_pts,1)} {team2} {round(team2_pts,1)}, confidence {round(game_confidence,4)}\n")


    if team1_pts > team2_pts:
      spread = team1 + " -" + str(round(team1_pts - team2_pts, 1))
    else:
      spread = team2 + " -" + str(round(team2_pts - team1_pts, 1))
    
    model_total = round(team2_pts + team1_pts, 1)

    model_college, model_number = spread.split(" -") # split the lines into the college of the favorite and the points given to them
    vegas_college, vegas_number = vegas_line.split(" -")

    model_line_pick, model_total_pick = calculate_model_picks(team1, team2, vegas_line, model_college, model_number, vegas_college, vegas_number, model_total, vegas_total)

    notes.write(f"\tModel spread: {spread}, model total: {model_total}\n")
    notes.write(f"\tvegas line: {vegas_line}, o/u {vegas_total}\n")
    notes.write(f"\tmodel picks: {model_line_pick}, {model_total_pick}\n")
    notes.write("\toutcome:\n")
    notes.write("\tmodel's performance:\n")
    notes.close()

def calculate_model_picks(team1, team2, vegas_line, model_college, model_number, vegas_college, vegas_number, model_total, vegas_total):
    model_line_pick = ""
    model_total_pick = ""

    if vegas_college == model_college:
        if (float(model_number) > float(vegas_number)) and (float(model_number) - float(vegas_number)) > 1.5:
            model_line_pick = vegas_line
        elif (float(vegas_number) > float(model_number)) and (float(vegas_number) - float(model_number)) > 1.5:
            if team1 == model_college: # check who is the favorite
                model_line_pick = team2 + " +" + vegas_number
            else:
                model_line_pick = team1 + " +" + vegas_number
        else:
            model_line_pick = "NO PICK"
    else: # model has a different favorite than vegas
        if (float(model_number) + float(vegas_number)) > 1.5:
            model_line_pick = model_college + " +" + vegas_number
        else:
            model_line_pick = "NO PICK"

    if (model_total > float(vegas_total)) and ((model_total - float(vegas_total)) > 3):
       model_total_pick = "over " + vegas_total
    elif (model_total < float(vegas_total)) and ((float(vegas_total) - model_total) > 3):
       model_total_pick = "under " + vegas_total
    else:
       model_total_pick = "NO PICK"

    return model_line_pick,model_total_pick
    

def write_to_excel(team1, team2, game_confidence):
    current_date = datetime.now().strftime("%m/%d/%Y")
    wb = load_workbook('./ModelResults.xlsx')
    ws = wb.active
    ws.append([f'{team2} @ {team1}', current_date, round(game_confidence,4)])
    wb.save('./ModelResults.xlsx')