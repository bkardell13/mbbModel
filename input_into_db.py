import sqlite3
from datetime import datetime


def input_into_db(notes_file_path):
    games = parse_games(notes_file_path)
    # print(games[0])
    # temp = games[4].split(':')
    # my_picks_array = temp[1].split(',')
    # game1 = games[0].split("\n")
    # print(game1)
    count = 0
    for game in games:
        count+=1
        game_array = game.split("\n")
        matchup_line = game_array[0]
        location, degree, game_id, date, version = pull_matchup_data(matchup_line)
        prediction_line = game_array[2]
        prediction_array = prediction_line.split(" ")
        # print(prediction_line)
        team1, team1_pts, team2, team2_pts, confidence = extract_teams_and_points(prediction_array)

        vegas_lines_line = game_array[4]
        vegas_lines_line = vegas_lines_line.split(" ")
        vegas_lines_line = vegas_lines_line[2:]
        vegas_total = vegas_lines_line[len(vegas_lines_line)-1]
        vegas_lines_line = vegas_lines_line[:-2]
        vegas_line = " ".join(vegas_lines_line)
        vegas_line = vegas_line.replace(",", "")
        model_total_pick, model_line_pick = get_model_picks(game_array)
        outcome_line = game_array[6]
        outcome_array = outcome_line.split(" ")
        team2_points_result = outcome_array[len(outcome_array)-1]
        outcome_array = outcome_array[1:-1]
        for i, item in enumerate(outcome_array):
            try:
                # Attempt to convert to a float
                number = float(item)
                number_index = i
                break
            except ValueError:
                continue
        team1_points_result = outcome_array[number_index]

        model_performance_line = game_array[7]
        model_performance_array = model_performance_line.split(",")
        if "hit" in model_performance_array[0]:
            model_line_pick_result = "hit"
        elif "miss" in model_performance_array[0]:
            model_line_pick_result = "miss"
        elif "NA" in model_performance_array[0]:
            model_line_pick_result = "NA"

        if "hit" in model_performance_array[1]:
            model_total_pick_result = "hit"
        elif "miss" in model_performance_array[1]:
            model_total_pick_result = "miss"
        elif "NA" in model_performance_array[1]:
            model_total_pick_result = "NA"
        
        

        if degree == 1:
            game_id = game_id + ".1"
        elif degree == 3:
            game_id = game_id +".3"        
        
        


        con = sqlite3.connect("data.db")
        con.commit()
        values = (
            game_id, team1, team1_pts, team2, team2_pts,
            confidence, location, degree, vegas_line, vegas_total,
            model_line_pick, model_total_pick, model_line_pick_result, model_total_pick_result, team1_points_result, team2_points_result, 
            date, version
        )


        cur = con.cursor()
        # res = cur.execute("""
        #   INSERT INTO games VALUES
        #       (game_id, team1_name, team1_model_proj_pts, team2_name, team2_model_proj_pts, 
        #       confidence, location, degree_modeled, vegas_line, vegas_total, model_line_pick, model_total_pick,
        #       model_line_pick_result, model_total_pick_result, team1_points_result, team2_points_result, date)
        # """)

        query = """
        INSERT INTO games VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # Combine all variables into a tuple

        res = cur.execute(query, values)
        con.commit()

def get_model_picks(game_array):
    model_picks_line = game_array[5]
    model_picks_line = model_picks_line.split(" ")
    model_picks_line = model_picks_line[2:]
    model_total_pick = model_picks_line[len(model_picks_line)-2] + " " + model_picks_line[len(model_picks_line)-1]
    model_picks_line = model_picks_line[:-2]
    model_line_pick = " ".join(model_picks_line)
    model_line_pick = model_line_pick.replace(",", "")
    return model_total_pick,model_line_pick

def parse_games(file_path):
  games = []
  game_data = []
  with open(file_path, 'r') as file:
      for line in file:
          # Check if the line signifies the start of a new game section
          if '@' in line or 'vs' in line:
              if game_data:  # If there's existing game data, save it before starting a new game
                  games.append("\n".join(game_data))
                  game_data = []
          game_data.append(line.strip())  # Add current line to the game data

  # Add the last game data if the file doesn't end with an '@' line
  if game_data:
      games.append("\n".join(game_data))

  return games

def pull_matchup_data(matchup_line):
    if "@" in matchup_line:
        location = "Standard"
    else:
        location = "Neutral"
    
    if "deg 1" in matchup_line:
        degree = 1
    else:
        degree = 3

    matchup_array = matchup_line.split("(")

    game_id_section = matchup_array[2].replace(")", "")
    game_id = game_id_section.split(" ")[1]
    date_section = matchup_array[3].replace(")", "")
    date = date_section.split(" ")[1]
    version_section = matchup_array[4].replace(")", "")
    version = version_section.split(" ")[1]
    
    return location, degree, game_id, date, version


def extract_teams_and_points(prediction_list):
    confidence = prediction_list[len(prediction_list)-1]
    prediction_list = prediction_list[1:-2]
    team2_pts = prediction_list[len(prediction_list)-1]
    team2_pts = team2_pts.replace(",", "")
    prediction_list = prediction_list[:-1]
    for i, item in enumerate(prediction_list):
        try:
            # Attempt to convert to a float
            number = float(item)
            number_index = i
            break
        except ValueError:
            continue

    team1 = " ".join(prediction_list[:number_index])
    team1_pts = prediction_list[number_index]
    team2 = " ".join(prediction_list[number_index + 1:])


    return team1, team1_pts, team2, team2_pts, confidence






input_into_db("./notes_results.txt")