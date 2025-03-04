import sqlite3
import matplotlib.pyplot as plt
import numpy as np

    
def main():
    con = sqlite3.connect("data.db")
    con.commit()
    # values = (
    #     game_id, team1, team1_pts, team2, team2_pts,
    #     confidence, location, degree, vegas_line, vegas_total,
    #     model_line_pick, model_total_pick, model_line_pick_result, model_total_pick_result, team1_points_result, team2_points_result, date
    # )


    cur = con.cursor()
    # res = cur.execute("""
    #   INSERT INTO games VALUES
    #       (game_id, team1_name, team1_model_proj_pts, team2_name, team2_model_proj_pts, 
    #       confidence, location, degree_modeled, vegas_line, vegas_total, model_line_pick, model_total_pick,
    #       model_line_pick_result, model_total_pick_result, team1_points_result, team2_points_result, date)
    # """)

    query = """SELECT * FROM games    """

    # Combine all variables into a tuple
    res = cur.execute(query)
    data = res.fetchall()  
    
    con.commit()

    num_game_deg_1_line_was_picked = 0
    num_game_deg_1_line_was_correctly = 0
    num_game_deg_1_line_was_incorrectly = 0
    num_game_deg_1_total_was_picked = 0
    num_game_deg_1_total_was_correctly = 0
    num_game_deg_1_total_was_incorrectly = 0

    num_game_deg_3_line_was_picked = 0
    num_game_deg_3_line_was_correctly = 0
    num_game_deg_3_line_was_incorrectly = 0
    num_game_deg_3_total_was_picked = 0
    num_game_deg_3_total_was_correctly = 0
    num_game_deg_3_total_was_incorrectly = 0

    num_deg_1_total_diff_4_hit = 0
    num_deg_1_total_diff_5_hit = 0
    num_deg_1_total_diff_6_hit = 0
    num_deg_1_total_diff_7_hit = 0
    num_deg_1_total_diff_8_hit = 0
    num_deg_1_total_diff_10_hit = 0
    num_deg_1_total_diff_12_hit = 0

    num_deg_1_total_diff_4_Picked = 0
    num_deg_1_total_diff_5_Picked = 0
    num_deg_1_total_diff_6_Picked = 0
    num_deg_1_total_diff_7_Picked = 0
    num_deg_1_total_diff_8_Picked = 0
    num_deg_1_total_diff_10_Picked = 0
    num_deg_1_total_diff_12_Picked = 0

    num_deg_1_over_picked = 0
    num_deg_1_over_picked_correctly = 0
    num_deg_1_under_picked = 0
    num_deg_1_under_picked_correctly = 0

    num_deg_1_total_conf_over_035 = 0
    num_deg_1_total_conf_over_035_correctly = 0

    num_deg_1_line_v1_1 = 0
    num_deg_1_line_v1_1_correctly = 0

    # (207, '1Michigan State', 81.2, '3Minnesota', 65.1, 0.2406, '6Standard', 1, '8Michigan State -13.5', 139.5, '10Michigan State -13.5', '11over 139.5', '12hit', '13miss', 73, 51, '16date', 17version)
    for game in data:
        if game[7] == 1: # degree
            if game [12] != "NA": #lines
                if 1.1 == game[17]:
                        num_deg_1_line_v1_1 +=1
                num_game_deg_1_line_was_picked += 1
                if game[12] == "hit":
                    if 1.1 == game[17]:
                        num_deg_1_line_v1_1_correctly +=1

                    num_game_deg_1_line_was_correctly += 1
                elif game[12] == "miss":
                    num_game_deg_1_line_was_incorrectly += 1
            if game [13] != "NA": # totals
                num_game_deg_1_total_was_picked += 1



                if (abs(game[2] + game[4] - game[9]) > 4): #if total difference was greater than 5
                        num_deg_1_total_diff_4_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 5): #if total difference was greater than 5
                        num_deg_1_total_diff_5_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 6): #if total difference was greater than 5
                        num_deg_1_total_diff_6_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 7): #if total difference was greater than 5
                        num_deg_1_total_diff_7_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 8): #if total difference was greater than 5
                        num_deg_1_total_diff_8_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 10): #if total difference was greater than 5
                        num_deg_1_total_diff_10_Picked += 1
                if (abs(game[2] + game[4] - game[9]) > 12): #if total difference was greater than 5
                        num_deg_1_total_diff_12_Picked += 1

                if "over" in game[11]:
                     num_deg_1_over_picked +=1
                elif "under" in game[11]:
                     num_deg_1_under_picked +=1


                if game[5] > 0.35:
                     num_deg_1_total_conf_over_035 +=1 



                if game[13] == "hit":
                    num_game_deg_1_total_was_correctly += 1


                    if "over" in game[11]:
                        num_deg_1_over_picked_correctly +=1
                    elif "under" in game[11]:
                         num_deg_1_under_picked_correctly +=1
                    if (abs(game[2] + game[4] - game[9]) > 4): #if total difference was greater than 5
                        num_deg_1_total_diff_4_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 5): #if total difference was greater than 5
                        num_deg_1_total_diff_5_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 6): #if total difference was greater than 5
                        num_deg_1_total_diff_6_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 7): #if total difference was greater than 5
                        num_deg_1_total_diff_7_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 8): #if total difference was greater than 5
                        num_deg_1_total_diff_8_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 10): #if total difference was greater than 5
                        num_deg_1_total_diff_10_hit += 1
                    if (abs(game[2] + game[4] - game[9]) > 12): #if total difference was greater than 5
                        num_deg_1_total_diff_12_hit += 1
                    if game[5] > 0.35:
                        num_deg_1_total_conf_over_035_correctly +=1
                    



                elif game[13] == "miss":
                    num_game_deg_1_total_was_incorrectly += 1
        elif game[7] == 3:
            if game [12] != "NA":
                num_game_deg_3_line_was_picked += 1
                if game[12] == "hit":
                    num_game_deg_3_line_was_correctly += 1
                elif game[12] == "miss":
                    num_game_deg_3_line_was_incorrectly += 1
            if game [13] != "NA":
                num_game_deg_3_total_was_picked += 1
                if game[13] == "hit":
                    num_game_deg_3_total_was_correctly += 1
                elif game[13] == "miss":
                    num_game_deg_3_total_was_incorrectly += 1


    print(f"OUT OF {int(len(data)/2)} GAMES\n" )

    print(f"Degree 1 Line Hit %: \t{round(num_game_deg_1_line_was_correctly/num_game_deg_1_line_was_picked*100,1)}% "
      f"\t{num_game_deg_1_line_was_correctly}/{num_game_deg_1_line_was_picked}")
    print(f"Degree 1 Total Hit %: \t{round(num_game_deg_1_total_was_correctly/num_game_deg_1_total_was_picked*100,1)}% "
      f"\t{num_game_deg_1_total_was_correctly}/{num_game_deg_1_total_was_picked}")
    print(f"Degree 3 Line Hit %: \t{round(num_game_deg_3_line_was_correctly/num_game_deg_3_line_was_picked*100,1)}% "
      f"\t{num_game_deg_3_line_was_correctly}/{num_game_deg_3_line_was_picked}")
    print(f"Degree 3 Total Hit %: \t{round(num_game_deg_3_total_was_correctly/num_game_deg_3_total_was_picked*100,1)}% "
      f"\t{num_game_deg_3_total_was_correctly}/{num_game_deg_3_total_was_picked}")
    
    print(f"\nDegree 1 Total Hit % when diff > 5:\t{round(num_deg_1_total_diff_5_hit/num_deg_1_total_diff_5_Picked*100,1) }%"
          f"\t{num_deg_1_total_diff_5_hit}/{num_deg_1_total_diff_5_Picked}")
    print(f"Degree 1 Total Hit % for overs:  \t{round(num_deg_1_over_picked_correctly/num_deg_1_over_picked*100,1) }%"
          f"\t{num_deg_1_over_picked_correctly}/{num_deg_1_over_picked}")
    print(f"Degree 1 Total Hit % for unders: \t{round(num_deg_1_under_picked_correctly/num_deg_1_under_picked*100,1) }%"
          f"\t{num_deg_1_under_picked_correctly}/{num_deg_1_under_picked}")
    print(f"Degree 1 Total Hit % for conf > 0.35: \t{round(num_deg_1_total_conf_over_035_correctly/num_deg_1_total_conf_over_035*100,1) }%"
          f"\t{num_deg_1_total_conf_over_035_correctly}/{num_deg_1_total_conf_over_035}")

    print(f"\nDegree 1 v1.1 Line Hit %: \t{round(num_deg_1_line_v1_1_correctly/num_deg_1_line_v1_1*100,1) }%"
          f"\t{num_deg_1_line_v1_1_correctly}/{num_deg_1_line_v1_1}")


    percentages = [(num_deg_1_total_diff_4_hit/num_deg_1_total_diff_4_Picked), 
                   (num_deg_1_total_diff_5_hit/num_deg_1_total_diff_5_Picked),
                   (num_deg_1_total_diff_6_hit/num_deg_1_total_diff_6_Picked),
                   (num_deg_1_total_diff_7_hit/num_deg_1_total_diff_7_Picked),
                   (num_deg_1_total_diff_8_hit/num_deg_1_total_diff_8_Picked),
                   (num_deg_1_total_diff_10_hit/num_deg_1_total_diff_10_Picked),
                   (num_deg_1_total_diff_12_hit/num_deg_1_total_diff_12_Picked),]
    
    diff = [4, 5, 6, 7, 8, 10, 12]


    # mymodel = np.poly1d(np.polyfit(diff, percentages, 3))
    # # myline = np.linspace(0, 120, 1)
    # plt.scatter(diff, percentages)
    # # plt.plot(myline, mymodel(myline))
    # # plt.title("adjusted defense of opponents played by " + team_name +" vs pts points scored. Opp adj D:  " + str(opp_adj_d))
    # plt.show()

if __name__ == "__main__":
    main()