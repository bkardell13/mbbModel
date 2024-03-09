# Install devtools if you haven't already

options(repos = c(CRAN = "https://cloud.r-project.org"))
install.packages("devtools")

# Install ncaahoopR from GitHub
devtools::install_github("lbenz730/ncaahoopR")

# Access arguments passed from Python
args <- commandArgs(trailingOnly = TRUE)

# Assuming the team name is the first argument
cat("Received team name:", args[1], "\n")
team_name <- args[1]



# Your R code using the team name
library(ncaahoopR)

schedule_data <- get_schedule(team = team_name, season = "2023-24")

current_date <- format(Sys.Date(), "%m_%d_%Y") # Formats the date as MM_DD_YYYY

# Adjust the file path as necessary, incorporating the current date
write.csv(schedule_data, paste0("C:/Users/bnkar/OneDrive/Desktop/school/playground/mbbModel/data/", team_name, "_", current_date, ".csv"), row.names = FALSE)