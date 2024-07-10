# install.packages('dplyr')
# install.packages('readr')

# Load required libraries
library(dplyr)
library(readr)

# Read the CSV file
getwd()
data <- read_csv("./results/csv/evaluation.csv")
summary(data)

# Function to calculate harmonic mean
harmonic_mean <- function(x) {
  return(length(x) / sum(1/x))
}

# Group by Filename and calculate harmonic mean for numeric columns
result <- data %>%
  group_by(Config, OCR_module, LLM_model) %>%
  summarise(across(c(Accuracy, Precision, Recall, F1_Score), ~harmonic_mean(.[. != 0])), .groups = "drop")

result %>% arrange(desc(F1_Score))
result %>% arrange(desc(Accuracy))


# View the result
print(result)

# Optionally, write the result to a new CSV file
write_csv(result, "./results/csv/evaluated.csv")
