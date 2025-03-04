options(repos = c(CRAN = "https://cloud.r-project.org"))
# install.packages("devtools")
# install.packages("devtools", lib = "C:/Program Files/R/R-4.4.2/library")
# if (!requireNamespace("devtools", quietly = TRUE)) {
#   install.packages("devtools", lib = Sys.getenv("R_LIBS_USER"))
# }
# print("here1")
# Install ncaahoopR from GitHub
devtools::install_github("lbenz730/ncaahoopR")

# Access arguments passed from Python
args <- commandArgs(trailingOnly = TRUE)

# Assuming the team name is the first argument
team_name <- args[1]


# Your R code using the team name
library(ncaahoopR)

# data("ids", package = "ncaahoopR")
# # print(ids, n = Inf)  # Show all rows
# write.csv(ids, paste0("C:/Users/bnkar/Desktop/MBBModel/possible_team_names", ".csv"), row.names = FALSE)

schedule_data <- get_schedule(team = team_name)
current_date <- format(Sys.Date(), "%m_%d_%Y") # Formats the date as MM_DD_YYYY


# Adjust the file path as necessary, incorporating the current date
write.csv(schedule_data, paste0("C:/Users/bnkar/Desktop/MBBModel/data/", team_name, "_", current_date, ".csv"), row.names = FALSE)
