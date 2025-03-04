import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import *
import csv
from sklearn.metrics import r2_score
import subprocess
from datetime import datetime
# from bs4 import BeautifulSoup
from notebook import find_lines, write_to_notes_files, write_to_excel, calculate_model_picks, find_game_id
from hca import find_hca
import sqlite3
from input_into_db import parse_games, pull_matchup_data, get_model_picks
import re





def main(team1, team2, location, files_loaded, write_to_notes, plot, degree):


  team1_temp = team1
  team2_temp = team2
  team1 = adjust_name_for_scaping(team1) #virginia washington state  South florida (usf) Eastern Kentucky (E Kentucky)etc
  team2 = adjust_name_for_scaping(team2)
  
  if files_loaded == False:
    Rscript_path = "C:\\Program Files\\R\\R-4.4.2\\bin\\Rscript.exe"
    # C:\Program Files\R\R-4.4.2
    r_script_file = './scraper.R' 
    # r_script_file = './master_schedule.R' 


    command1 = [Rscript_path, r_script_file, team1]
    result = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(result.stdout)
    # print(result.stderr)
    # exit(0)

    command = [Rscript_path, r_script_file, team2]
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)



  current_date = datetime.now().strftime("%m_%d_%Y")
  # Generate file paths dynamically with the current date
  team1_sched_path = f'./data/{team1}_{current_date}.csv'
  team2_sched_path = f'./data/{team2}_{current_date}.csv'
  kenpom_path = './data/summary25.csv'
  team1_sched = open(team1_sched_path, 'r') 
  team2_sched = open(team2_sched_path, 'r')
  kenpom = open(kenpom_path, 'r')

  team1 = team1_temp
  team2 = team2_temp



  team1_adj_o, team1_adj_d = get_team_adj_efficiency(kenpom, team1)
  kenpom.seek(0)
  team2_adj_o, team2_adj_d = get_team_adj_efficiency(kenpom, team2)
  
  # would only be -1 if team was not found
  # print(team1_adj_o)
  # if team1_adj_o != -1 or team1_adj_d != -1 or team2_adj_o != -1 or team2_adj_d : 
  #   print("ERROR")
  # print(team1_adj_o)
  # print(team1_adj_d)
  # print(team2_adj_o)
  # print(team2_adj_d)

  #Entering X and Y values
  team1_proj_pts_allowed, team1_proj_pts_scored, team1_confidence = single_team_proj(team1_sched, kenpom, team2_adj_o, team2_adj_d, degree, plot, team1)
  # print(team1_proj_pts_allowed)
  # print(team1_proj_pts_scored)

  team2_proj_pts_allowed, team2_proj_pts_scored, team2_confidence = single_team_proj(team2_sched, kenpom, team1_adj_o, team1_adj_d, degree, plot, team2)
  # print(team2_proj_pts_allowed)
  # print(team2_proj_pts_scored)

  print("PROJECTIONS")
  team1_pts = (team1_proj_pts_scored + team2_proj_pts_allowed) / 2
  team2_pts = (team2_proj_pts_scored + team1_proj_pts_allowed) / 2
  team1_pts, team2_pts = adjust_points_for_location(team1, team1_pts, team2_pts, location)
  game_confidence = (team1_confidence + team2_confidence) / 2
  print(team1 + ": " + str(round(team1_pts, 1)))
  print(team2 + ": " + str(round(team2_pts, 1)))
  print("Game confidence score: " + str(round(game_confidence, 4)))


  model_total = round(team2_pts + team1_pts, 1)
  vegas_line, vegas_total = find_lines(team1, team2, team1_sched) # a lot of this is copied over from notebook.py would like to consolidate in the future
  if team1_pts > team2_pts:
    spread = team1 + " -" + str(round(team1_pts - team2_pts, 1))
  else:
    spread = team2 + " -" + str(round(team2_pts - team1_pts, 1))
  model_college, model_number = spread.split(" -") # split the lines into the college of the favorite and the points given to them
  # print(vegas_line)
  vegas_college, vegas_number = vegas_line.split(" -") # st tomas - minnesota and other schools with "-" cannot use this function, will need a workaround
  model_line_pick ,model_total_pick = calculate_model_picks(team1, team2, vegas_line, model_college, model_number, vegas_college, vegas_number, model_total, vegas_total)
  game_id = find_game_id(team1_sched)
  

  if(write_to_notes):
    write_to_notes_files(team1, team2, team1_pts, team2_pts, game_confidence, location, degree, vegas_line, vegas_total, game_id, "1.1")
    # database_entry(game_id, team1, team2, team1_pts, team2_pts, game_confidence, location, degree, vegas_line, vegas_total, model_line_pick, model_total_pick, current_date)
  


  team1_sched.close()
  team2_sched.close() 
  kenpom.close()

def database_entry(game_id, team1, team2, team1_pts, team2_pts, game_confidence, location, degree, vegas_line, vegas_total, model_line_pick, model_total_pick, current_date):
  con = sqlite3.connect("data.db")
  con.commit()


  cur = con.cursor()
  # res = cur.execute("""
  #   INSERT INTO games VALUES
  #       (game_id, team1_name, team1_model_proj_pts, team2_name, team2_model_proj_pts, 
  #       confidence, location, degree_modeled, vegas_line, vegas_total, model_line_pick, model_total_pick,
  #       model_line_pick_result, model_total_pick_result, team1_points_result,team1_points_result)
  # """)

  query = """
    INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
  """

  # Combine all variables into a tuple
  if degree == 1:
    game_id = game_id + ".1"
  elif degree == 3:
    game_id = game_id +".3"
  values = (
      game_id, team1, round(team1_pts,1), team2, round(team2_pts,1),
      round(game_confidence,4), location, degree, vegas_line, vegas_total,
      model_line_pick, model_total_pick, "NULL", "NULL", "NULL", "NULL", current_date
  )
  res = cur.execute(query, values)
  con.commit()




def adjust_points_for_location(team1_name, team1_pts, team2_pts, location): # Could use a lot of adjustment based on the homecourt advantage of each team
  
  if find_hca(team1_name) == "ERROR": # csu northridge and app state is a tough edge case
    if team1_name == "App State":
      team1_name = "Appalachian St."
    elif team1_name == "Southeast Missouri State":
      team1_name = "Southeast Missouri"
    elif team1_name == "San JosÃ© State":
      team1_name = "San Jose St."
    elif "State" in team1_name:
      team1_name = team1_name.replace("State", "St.")
    else:
      team1_name = adjust_team_name(team1_name)
    hca = float(find_hca(team1_name))
  else:
    hca = float(find_hca(team1_name))

  if location == "Standard":
    team1_pts += hca/2
    team2_pts -= hca/2
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
    if team == "App State":
      new_team_name = "Appalachian St."
    elif "State" in team:
      new_team_name = team.replace("State", "St.")
    else:
      new_team_name = adjust_team_name(team)
      if new_team_name == "NOT FOUND":
        return -1, -1
    return get_team_adj_efficiency(kenpom, new_team_name) #rerun function with updated names
  return team_adj_o,team_adj_d


def single_team_proj(schedule, kenpom, opp_adj_o, opp_adj_d, degree, plot, team_name):


  # degree = 1
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

  if plot:
    myline = np.linspace(90, 130, 150)
    plt.scatter(x, y)
    plt.plot(myline, mymodel(myline))
    plt.title("adjusted offense of opponents played by" + team_name +" vs pts allowed. Opp adj O:  " + str(opp_adj_o))
    # plt.title(opp_adj_o)
    plt.show()

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
  if plot:
    myline = np.linspace(90, 120, 150)
    plt.scatter(x, y)
    plt.plot(myline, mymodel(myline))
    plt.title("adjusted defense of opponents played by " + team_name +" vs pts points scored. Opp adj D:  " + str(opp_adj_d))
    plt.show()


  total_confidence = (confidence_score1 + confidence_score2) / 2

  return proj_pts_allowed, proj_pts_scored, total_confidence



def adjust_team_name(team_name):
  if team_name == "UConn":
    return "Connecticut"
  elif team_name == "UAlbany":
    return "Albany"
  elif team_name == "Pitt":
    return "Pittsburgh"
  elif team_name == "Loyola Maryland":
    return "Loyola MD"
  elif team_name == "Florida International":
    return "FIU"
  elif team_name == "Long Island University":
    return "LIU"
  elif team_name == "McNeese St.":
    return "McNeese"
  elif team_name == "Hawai'i":
    return "Hawaii"
  elif team_name == "Grambling":
    return "Grambling St."
  elif team_name == "Miami":
    return "Miami FL"
  elif team_name == "Ole Miss":
    return "Mississippi"
  elif team_name == "St. Francis PA" or team_name == "St. Francis (PA)":
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
  elif team_name == "Cal State Northridge" or team_name == "Cal St. Northridge":
    return "CSUN"
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
  elif team_name == "St Bonaventure":
    return "St. Bonaventure"
  elif team_name == "App State":
    return "Appalachian St."
  elif team_name == "SIU Edwardsville":
    return "SIUE"
  elif team_name == "Mississippi Valley State":
    return "Mississippi Valley St."
  elif team_name == "Miami (OH)":
    return "Miami OH"
  elif team_name == "Southeast Missouri St.":
    return "Southeast Missouri"
  elif team_name == "IU Indianapolis":
      return "IU Indy"
  else:
    # print("team not found: " + team_name)
    return "NOT FOUND"

def adjust_name_for_scaping(team_name): #virginia washington state  South florida (usf) Eastern Kentucky (E Kentucky)etc
  if team_name == "East Carolina":
    return "ECU"
  if team_name == "Virginia":
    return "UVA"
  elif team_name == "McNeese State" or team_name == "McNeese":
    return "Mcneese"
  elif team_name == "Washington State":
    return "Washington St"
  elif team_name == "St. Francis (PA)":
    return "St Francis (PA)"
  elif team_name == "Long Island University":
    return "LIU"
  elif team_name == "New Hampshire":
    return "UNH"
  elif team_name == "Mount St. Mary's":
    return "Mt St Mary's"
  elif team_name == "Florida Gulf Coast":
    return "FGCU"
  elif team_name == "South Florida":
    return "USF"
  elif team_name == "Eastern Kentucky":
    return "E Kentucky"
  elif team_name == "North Carolina":
    return "UNC"
  elif team_name == "Cal State Northridge":
    return "CSU Northridge"
  elif team_name == "Cal State Fullerton":
    return "CSU Fullerton"
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
  elif team_name == "South Dakota State":
    return "South Dakota St"
  elif team_name == "Northern Colorado":
    return "N Colorado"
  elif team_name == "Northern Kentucky":
    return "N Kentucky"
  elif team_name == "California":
    return "Cal"
  elif team_name == "North Carolina A&T":
    return "NC A&T"
  elif team_name == "Appalachian State":
    return "Appalachian St"
  elif team_name == "Seattle U":
    return "Seattle"
  elif team_name == "James Madison":
    return "JMU"
  elif team_name == "Northern Colorado":
    return "N Colorado"
  elif team_name == "East Tennessee State":
    return "ETSU"
  elif team_name == "Pittsburgh":
    return "Pitt"
  elif team_name == "Mississippi State":
    return "Miss St"
  elif team_name == "South Dakota State":
    return "South Dakota St"
  elif team_name == "Western Kentucky":
    return "W Kentucky"
  elif team_name == "Western Carolina":
    return "W Carolina"
  elif team_name == "Saint Peter's":
    return "St Peter's"
  elif team_name == "UAlbany":
    return "Albany"
  elif team_name == "Eastern Illinois":
    return "E Illinois"
  elif team_name == "Eastern Washington":
    return "E Washington"
  elif team_name == "Mississippi Valley State":
    return "Miss Valley St"
  elif team_name == "St. Bonaventure":
    return "St Bonaventure"
  elif team_name == "Tarleton State":
    return "Tarleton"
  elif team_name == "St. John's":
    return "St John's"
  elif team_name == "California Baptist":
    return "Cal Baptist"
  elif team_name == "Jacksonville State":
    return "Jacksonville St"
  elif team_name == "Sacramento State":
    return "Sacramento St"
  elif team_name == "Middle Tennessee":
    return "Mid Tennessee"
  elif team_name == "Florida International":
    return "FIU"
  elif team_name == "Southeast Missouri State":
    return "SE Missouri St"
  elif team_name == "Central Connecticut":
    return "Cent Conn St"
  elif team_name == "Fairleigh Dickinson":
    return "Fair Dickinson"
  elif team_name == "Northern Arizona":
    return "N Arizona"
  elif team_name == "Western Illinois":
    return "W Illinois"
  elif team_name == "Louisiana Tech":
    return "LA Tech"
  elif team_name == "Tennessee Tech":
    return "Tenn Tech"
  elif team_name == "SIU Edwardsville":
    return "SIUE"
  elif team_name == "Maryland Eastern Shore":
    return "MD-E Shore"
  elif team_name == "Rhode Island":
    return "URI"
  elif team_name == "North Dakota State":
    return "North Dakota St"
  elif team_name == "Tennessee State":
    return "Tennessee St"
  elif team_name == "Loyola Marymount":
    return "Loyola Mary"
  elif team_name == "Abilene Christian":
    return "Abil Christian"
  elif team_name == "Cal State Bakersfield":
    return "CSU Bakersfield"
  elif team_name == "UC Santa Barbara":
    return "UCSB"
  elif team_name == "Kansas City":
    return "UMKC"
  elif team_name == "St. Thomas-Minnesota":
    return "St. Thomas - Minnesota"
  elif team_name == "Loyola Chicago":
    return "Loyola-Chicago"
  elif team_name == "Western Michigan":
    return "W Michigan"
  elif team_name == "Eastern Michigan":
    return "E Michigan"
  elif team_name == "Northern Illinois":
    return "N Illinois"
  elif team_name == "Georgia Southern":
    return "Ga Southern"
  elif team_name == "Central Michigan":
    return "Cent Michigan"
  elif team_name == "App State":
    return "Appalachian St"
  elif team_name == "Central Arkansas":
    return "Cent Arkansas"
  elif team_name == "Arkansas-Pine Bluff":
    return "AR-Pine Bluff"
  elif team_name == "New Mexico State":
    return "New Mexico St"
  elif team_name == "East Texas A&M":
    return "Texas A&M-Commerce"
  elif team_name == "Stephen F. Austin":
    return "SF Austin"
  elif team_name == "North Carolina Central":
    return "NC Central"
  elif team_name == "South Carolina State":
    return "S Carolina St"
  elif team_name == "Prairie View A&M":
    return "PV A&M"
  elif team_name == "Northwestern State":
    return "Northwestern St" # john melvin
  elif team_name == "UT Rio Grande Valley":
    return "UT Rio Grande"
  elif team_name == "Texas A&M-Corpus Christi":
    return "Texas A&M-CC"
  elif team_name == "Massachusetts":
    return "UMass"
  elif team_name == "American University":
    return "American"
  elif team_name == "Charleston Southern":
    return "Charleston So"
  elif team_name == "George Washington":
    return "G Washington"
  elif team_name == "Saint Joseph's":
    return "Saint Joe's"
  elif team_name == "Southern Illinois":
    return "S Illinois"
  elif team_name == "Boston University":
    return "Boston U"
  elif team_name == "Loyola Maryland":
    return "Loyola (MD)"
  elif team_name == "IU Indianapolis":
    return "IU Indy"
  elif team_name == "UNC Greensboro":
    return "UNCG"
  elif team_name == "San JosÃ© State":
    return "San Jose State"
  elif team_name == "Florida Atlantic":
    return "FAU"
  elif team_name == "Pennsylvania":
    return "Penn"
  elif team_name == "Purdue Fort Wayne":
    return "Fort Wayne"
  elif team_name == "South Carolina Upstate":
    return "USC Upstate"
  else:
    return team_name

def run_daily_schedule(main, date):
    schedule_loaded = True
    # current_date = datetime.now().strftime("%m_%d_%Y")

    if schedule_loaded == False:
      Rscript_path = "C:\\Program Files\\R\\R-4.4.2\\bin\\Rscript.exe" 
      r_script_file = './master_schedule.R' 


      command1 = [Rscript_path, r_script_file, date]
      result = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    # print(result.stdout)
    # print(result.stderr)
    # exit(0)
    sched_path = f'./schedules/schedule_{date}.csv'
    sched = open(sched_path, 'r')
    sched.seek(0)
    sched_reader = csv.reader(sched)
  # print(team1_reader)

    next(sched_reader)
    for row in sched_reader:
      # print(row)
      away_team_name = row[1]
      home_team_name = row[2]
    # print(str(away_team_name) + " @ " + str(home_team_name))
      main(home_team_name, away_team_name, "Standard", False, True, False, 1)
      main(home_team_name, away_team_name, "Standard", True, True, False, 3)

def run_daily_results(date):
  schedule_loaded = False
  notes_path = "./notes_transition.txt"
  games = parse_games(notes_path)

  if schedule_loaded == False:
    Rscript_path = "C:\\Program Files\\R\\R-4.4.2\\bin\\Rscript.exe" 
    r_script_file = './master_schedule.R' 


    command1 = [Rscript_path, r_script_file, date]
    result = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
  # print(result.stdout)
  # print(result.stderr)
  # exit(0)
  sched_path = f'./schedules/schedule_{date}.csv'
  sched = open(sched_path, 'r')
  sched.seek(0)
  sched_reader = csv.reader(sched)
# print(team1_reader)

  next(sched_reader)
  notes = open('./notes_results.txt', 'a')
  notes.write("\n")

  for game in games:
    game_array = game.split("\n")
    matchup_line = game_array[0]
    _, _, game_id, _, _ = pull_matchup_data(matchup_line)
    sched.seek(0)
    for row in sched_reader:
      sched_game_id = row[0]
      if sched_game_id == game_id: ## game was found in schedule and in notes
        away_team_name = row[1]
        home_team_name = row[2]
        away_team_score = row[5]
        home_team_score = row[6]
        total_pick, line_pick = get_model_picks(game_array)

        # def evaluate_picks(spread_pick, total_pick, away_team_name, away_team_score, home_team_score):
        spread_hit, total_hit = evaluate_picks(line_pick, total_pick, away_team_name, away_team_score, home_team_score)
        # print(spread_hit, total_hit)


        notes.write(game_array[0] + "\n")
        notes.write(game_array[1] + "\n")
        notes.write("\t" + game_array[2] + "\n")
        notes.write("\t" +game_array[3] + "\n")
        notes.write("\t" +game_array[4] + "\n")
        notes.write("\t" +game_array[5] + "\n")
        notes.write("\t" +game_array[6] + " " + home_team_name + " " + home_team_score + " " + away_team_name + " " + away_team_score +"\n")
        notes.write("\t" +game_array[7] + f" line - {spread_hit}, total - {total_hit}\n\n")
        # notes.write(game_array[8] + "\n")

def evaluate_picks(spread_pick, total_pick, away_team_name, away_team_score, home_team_score):
  # Extract information from picks
  if total_pick == "NO PICK":
    total_hit = "NA"
  else:
    total_type, total_value = total_pick.split()
    total_value = float(total_value)
    total_score = int(home_team_score) + int(away_team_score)
    total_hit = total_score > total_value if total_type.lower() == "over" else total_score < total_value
    if total_hit:
      total_hit = "hit"
    else:
      total_hit = "miss"


  if spread_pick == "NO PICK":
    spread_hit = "NA"
  else:
    # spread_hit = ""
    spread_team, spread_value = parse_spread(spread_pick)
    spread_value = float(spread_value)

    # Determine if the spread pick was correct
    if spread_team == away_team_name:
        team_score = away_team_score
        opponent_score = home_team_score
    else:
        team_score = home_team_score
        opponent_score = away_team_score

    spread_hit = (int(team_score) + int(spread_value)) > int(opponent_score)  # Check if the team covered
    if spread_hit:
      spread_hit = "hit"
    else:
      spread_hit = "miss"


  return spread_hit, total_hit

def parse_spread(spread_pick):
    match = re.match(r"(.+)\s+([+-]?\d+\.?\d*)$", spread_pick)
    if match:
        spread_team = match.group(1).strip()
        spread_value = float(match.group(2))
        return spread_team, spread_value
    else:
        raise ValueError(f"Invalid spread format: {spread_pick}")


if __name__ == "__main__":
  # main(team1 (home), team2 (away), location, files_loaded, write_to_notes, plot, degree):
  date = "2025-03-04"
  run_daily_schedule(main, date)
  # run_daily_results(date)

  # main("Southern", "Texas Southern", "Neutral", True, True, False, 1)
  # main("Nebraska", "Creighton", "Neutral", True, True, False, 3)
