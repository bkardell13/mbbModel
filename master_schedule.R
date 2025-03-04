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

# Your R code using the team name
library(ncaahoopR)
schedule <- get_master_schedule(args[1])
print(schedule)
write.csv(schedule, paste0("C:/Users/bnkar/Desktop/MBBModel/schedules/", "schedule", "_", args[1], ".csv"), row.names = FALSE)