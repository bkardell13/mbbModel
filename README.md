# mbbModel
Work-in-progress College Basketball Model to predict game outcomes

## Data
Data is scraped using scraper.R, which leverages the lbenz730/ncaahoopR package to get each team's respective schedule. Scraper.R takes a singular team as an argument and runtime could potentially be improved by giving both teams as arguments at once. Each team's schedule is stored in the data folder and given the date of which the schedule was scraped. 

Data from kenpom.com is used to assess each teams offensive and defensive efficiency.

The results of the games that are being predicted are stored in notes.txt and ModelResults.xlsx. There is a large efficiency gap as the majority of the data is being input manually, such as the results and the line and total. 

## Prediction method
A regression model is used using basic python packages. The model is run 4 times, twice for each team. For each team, a model is created for the correlation of the points they have allowed to their opponents offensive efficiency and a model for the points they have scored to their oppenents defensive efficiency throughout the course of the season up to this point. In other words the model is "f(opponents defensive efficiency) = points" scored and "f(opponents defensive efficiency) = points scored". Then, the efficiencies of the new opponent, the opponent they are playing in the game that the model attepts to predict, are input into the regression model. This is done for both teams. The projected points allowed for team 1 are averaged with the projected points scored of team 2 and the projected points allowed for team 2 are averaged with the projected points scored of team 1.

These numbers are adjusted for the location of the game (Neutral or Standard, where Standard is at one of the team's home arena). The confidence score associated with the game is the averages r2 score of all 4 models that are created. It essentially signifies the predictability and consistency of the 2 teams playing in the predicted game
