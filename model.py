import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
import csv
from sklearn.metrics import r2_score
import subprocess
from datetime import datetime
from openpyxl import load_workbook



def main(team1, team2, location, files_loaded, write_to_notes):


  team1_temp = team1
  team2_temp = team2
  team1 = adjust_name_for_scaping(team1) #virginia washington state  South florida (usf) Eastern Kentucky (E Kentucky)etc
  team2 = adjust_name_for_scaping(team2)
  
  if files_loaded == False:
    Rscript_path = "C:\\Program Files\\R\\R-4.3.2\\bin\\Rscript.exe"
    r_script_file = './scraper.R' 


    command1 = [Rscript_path, r_script_file, team1]
    subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    command = [Rscript_path, r_script_file, team2]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)



  current_date = datetime.now().strftime("%m_%d_%Y")

  # Generate file paths dynamically with the current date
  team1_sched_path = f'./data/{team1}_{current_date}.csv'
  team2_sched_path = f'./data/{team2}_{current_date}.csv'
  kenpom_path = './data/summary24.csv'

  # format_file(team1_sched_path)
  # format_file(team2_sched_path)

  team1_sched = open(team1_sched_path, 'r') 
  team2_sched = open(team2_sched_path, 'r')
  kenpom = open(kenpom_path, 'r')

  team1 = team1_temp
  team2 = team2_temp



  team1_adj_o, team1_adj_d = get_team_adj_efficiency(kenpom, team1)
  kenpom.seek(0)
  team2_adj_o, team2_adj_d = get_team_adj_efficiency(kenpom, team2)
  
  # print(team1_adj_o)
  # print(team1_adj_d)
  # print(team2_adj_o)
  # print(team2_adj_d)

  #Entering X and Y values
  team1_proj_pts_allowed, team1_proj_pts_scored, team1_confidence = single_team_proj(team1_sched, kenpom, team2_adj_o, team2_adj_d)
  # print(team1_proj_pts_allowed)
  # print(team1_proj_pts_scored)

  team2_proj_pts_allowed, team2_proj_pts_scored, team2_confidence = single_team_proj(team2_sched, kenpom, team1_adj_o, team1_adj_d)
  # print(team2_proj_pts_allowed)
  # print(team2_proj_pts_scored)

  print("PROJECTIONS")
  team1_pts = (team1_proj_pts_scored + team2_proj_pts_allowed) / 2
  team2_pts = (team2_proj_pts_scored + team1_proj_pts_allowed) / 2
  team1_pts, team2_pts = adjust_points_for_location(team1_pts, team2_pts, location)
  game_confidence = (team1_confidence + team2_confidence) / 2
  print(team1 + ": " + str(round(team1_pts, 1)))
  print(team2 + ": " + str(round(team2_pts, 1)))
  print("Game confidence score: " + str(round(game_confidence, 4)))


  if(write_to_notes):
    write_to_notes_files(team1, team2, team1_pts, team2_pts, game_confidence, location)
    # current_date = datetime.now().strftime("%m/%d/%Y")
    # wb = load_workbook('./ModelResults.xlsx')
    # ws = wb.active
    # ws.append([f'{team2} @ {team1}', "", round(game_confidence,4)])
    # wb.save('./ModelResults.xlsx')
  


  team1_sched.close()
  team2_sched.close() 
  kenpom.close()

def write_to_notes_files(team1, team2, team1_pts, team2_pts, game_confidence, location):
    if location == "Standard":
      val = "@"
    elif location == "Neutral":
      val = "vs"
    notes = open('./notes.txt', 'a')
    notes.write("\n")
    notes.write(f'{team2} {val} {team1}\n')
    notes.write("\n")
    notes.write(f"\tprediction: {team1} {round(team1_pts,1)} {team2} {round(team2_pts,1)}, confidence {round(game_confidence,4)}\n")
    notes.write("\tline:\n")
    notes.write("\tmy model:\n")
    notes.write("\toutcome:\n")
    notes.write("\tmodel's performance:\n")
    notes.close()

def adjust_points_for_location(team1_pts, team2_pts, location): # Could use a lot of adjustment based on the homecourt advantage of each team
  if location == "Standard":
    team1_pts += 2.0
    team2_pts -= 2.0
    return team1_pts, team2_pts
  else:
    return team1_pts, team2_pts


def get_team_adj_efficiency(kenpom, team):
  team_adj_o = 0
  team_adj_d = 0
  kenpom.seek(0)
  kenpom_reader = csv.reader(kenpom)
  for line in kenpom_reader:
    if line[1] == team:
      team_adj_o = line[8]
      team_adj_d = line[12]
  if team_adj_o == 0: # team not originally found
    if "State" in team:
      new_team_name = team.replace("State", "St.")
    else:
      new_team_name = adjust_team_name(team)
      if new_team_name == "NOT FOUND":
        return -1, -1
    return get_team_adj_efficiency(kenpom, new_team_name) #rerun function with updated names
  return team_adj_o,team_adj_d

def single_team_proj(schedule, kenpom, opp_adj_o, opp_adj_d):
  degree = 3
  adj_o_list = []
  pts_allowed_list = []
  adj_d_list = []
  pts_scored_list = []
  weights = []
  team1_reader = csv.reader(schedule)
  next(team1_reader)
  for line in team1_reader:
    if line[4] != "NA": # if the game has been played
      opponent = line[2]
      value1, value2 = get_team_adj_efficiency(kenpom, opponent)
      if value1 != -1 and value2 != -1: # would only be -1 if team was not found
        adj_o_list.append(float(value1))
        adj_d_list.append(float(value2))
        pts_scored = line[4]
        pts_allowed = line[5]
        pts_scored_list.append(int(pts_scored))
        pts_allowed_list.append(int(pts_allowed))
        kenpom.seek(0)
        weights.append(1)
  
  recent_games_count = 10
  if len(weights) > recent_games_count: #accounting last 10 games as 1.5
    for i in range(-recent_games_count, 0):
        weights[i] = 1.5
  weights = np.array(weights)



  x = np.array(adj_o_list, float) #adj o of teams played
  y = np.array(pts_allowed_list, float) #points allowed
  if len(x) != len(y):
    print("ERROR")
  mymodel = np.poly1d(np.polyfit(x, y, degree, w=weights))
  # mymodel = np.poly1d(np.polyfit(x, y, degree))

  # test(x,y)


  z = float(opp_adj_o) # adj o of team about to play
  # doing this manually for now, would like to automate it in the future
  proj_pts_allowed = mymodel(z)
  confidence_score1 = r2_score(y, mymodel(x))

  # myline = np.linspace(90, 130, 150)
  # plt.scatter(x, y)
  # plt.plot(myline, mymodel(myline))
  # plt.title("adjusted offense of opponents vs pts allowed ")
  # plt.show()

  #Entering X and Y values
  z = float(opp_adj_d) # adj d of team about to play
  # doing this manually for now, would like to automate it in the future
  x = np.array(adj_d_list, float) #adj d of teams played
  y = np.array(pts_scored_list, float) #points scored
  if len(x) != len(y):
    print("ERROR")
  mymodel = np.poly1d(np.polyfit(x, y, degree, w=weights))
  # mymodel = np.poly1d(np.polyfit(x, y, degree))
  proj_pts_scored = mymodel(z)
  confidence_score2 = r2_score(y, mymodel(x))

  # test(x,y)

  # myline = np.linspace(90, 120, 150)
  # plt.scatter(x, y)
  # plt.plot(myline, mymodel(myline))
  # plt.title("adj o of opps vs pts scored")
  # plt.show()


  total_confidence = (confidence_score1 + confidence_score2) / 2

  return proj_pts_allowed, proj_pts_scored, total_confidence



def adjust_team_name(team_name):
  if team_name == "UConn":
    return "Connecticut"
  elif team_name == "UAlbany":
    return "Albany"
  elif team_name == "Loyola Maryland":
    return "Loyola MD"
  elif team_name == "Florida International":
    return "FIU"
  elif team_name == "Long Island University":
    return "LIU"
  elif team_name == "McNeese":
    return "McNeese St."
  elif team_name == "Hawai'i":
    return "Hawaii"
  elif team_name == "Grambling":
    return "Grambling St."
  elif team_name == "Miami":
    return "Miami FL"
  elif team_name == "Ole Miss":
    return "Mississippi"
  elif team_name == "St. Francis PA":
    return "Saint Francis"
  elif team_name == "Seattle U":
    return "Seattle"
  elif team_name == "Arkansas-Pine Bluff":
    return "Arkansas Pine Bluff"
  elif team_name == "Gardner-Webb":
    return "Gardner Webb"
  elif team_name == "Kansas City":
    return "UMKC"
  elif team_name == "Nicholls":
    return "Nicholls St."
  elif team_name == "California Baptist":
    return "Cal Baptist"
  elif team_name == "NC St.":
    return "N.C. State"
  elif team_name == "Queens University":
    return "Queens"
  elif team_name == "UL Monroe":
    return "Louisiana Monroe"
  elif team_name == "Texas A&M-Corpus Christi":
    return "Texas A&M Corpus Chris"
  elif team_name == "Pennsylvania":
    return "Penn"
  elif team_name == "Maryland-Eastern Shore":
    return "Maryland Eastern Shore"
  elif team_name == "American University":
    return "American"
  elif team_name == "St. Thomas-Minnesota":
    return "St. Thomas"
  elif team_name == "UIC":
    return "Illinois Chicago"
  elif team_name == "SE Louisiana":
    return "Southeastern Louisiana"
  elif team_name == "UT Martin":
    return "Tennessee Martin"
  elif team_name == "San JosÃ© St.":
    return "San Jose St."
  elif team_name == "Omaha":
    return "Nebraska Omaha"
  elif team_name == "Texas A&M-Commerce":
    return "Texas A&M Commerce"
  elif team_name == "South Carolina Upstate":
    return "USC Upstate"
  elif team_name == "Bethune-Cookman":
    return "Bethune Cookman"
  elif team_name == "Sam Houston":
    return "Sam Houston St."
  else:
    # print("team not found: " + team_name)
    return "NOT FOUND"

def adjust_name_for_scaping(team_name): #virginia washington state  South florida (usf) Eastern Kentucky (E Kentucky)etc
  if team_name == "East Carolina":
    return "ECU"
  if team_name == "Virginia":
    return "UVA"
  elif team_name == "Washington State":
    return "Washington St"
  elif team_name == "South Florida":
    return "USF"
  elif team_name == "Eastern Kentucky":
    return "E Kentucky"
  elif team_name == "North Carolina":
    return "UNC"
  elif team_name == "Cal State Northridge":
    return "CSU Northridge"
  elif team_name == "Coastal Carolina":
    return "C. Carolina"
  elif team_name == "Youngstown State":
    return "Youngstown St"
  elif team_name == "Northern Kentucky":
    return "N Kentucky"
  elif team_name == "California":
    return "Cal"
  elif team_name == "North Carolina A&T":
    return "NC A&T"
  else:
    return team_name

if __name__ == "__main__":
    # main(team1, team2, location, files_loaded, write_to_notes):
    main("Kansas State", "Iowa State", "Standard", False, True)
    # main("Tennessee", "Kentucky", "Standard", False, True)
    # main("Duke", "North Carolina", "Standard", False, True)


