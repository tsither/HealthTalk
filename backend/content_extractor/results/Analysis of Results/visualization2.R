library(psych)   
library(RColorBrewer) # display.brewer.all()
library(tidyverse)
library(dplyr)
library(ggplot2)
library(stringr)
library(wesanderson)

##########################CONFIG###########################

df <- read.csv('raw_episodes.csv')

extract_model_name <- function(full_model_name) {
  return(sub("^(.*?)-t0\\.0.*", "\\1", full_model_name))
}

extract_no_episode <- function(episode_string) {
  return(sub("episode_", "Episode ", episode_string))
}

model_mapping <- c(
  "Mistral-Nemo"                    = "Mistral NeMo (12B)",
  "Qwen2-72B-Instruct"              = "Qwen2 (72B)",
  "Mixtral-8x22B-Instruct-v0.1"    = "Mixtral 8x22B",
  "gemini-1.0-pro-latest"           = "Gemini (1.6T)",
  "gemma-2-27b-it"                  = "Gemma2 (27B)",
  "Meta-Llama-3-70B-Instruct-Lite" = "Llama3 (70B)",
  "Mixtral-8x7B-Instruct-v0.1" = "Mixtral 8x7B"
)

experiment_mapping <- c(
  "1_full_no_special_cards" = "Exp. 2: Full Game No Special Cards",
  "8_short_pos3_easy"       = "Exp. 9: Short Game Pos. 3 Easy",
  "7_short_pos2_hard"       = "Exp. 8: Short Game Pos. 2 Hard",
  "4_short_pos1_easy"       = "Exp. 5: Short Game Pos. 1 Easy",
  "3_short_no_reprompting"  = "Exp. 4: Short Game No Reprompting",
  "5_short_pos1_hard"       = "Exp. 6: Short Game Pos. 1 Hard",
  "0_full_game"             = "Exp. 1: Full Game",
  "6_short_pos2_easy"       = "Exp. 7: Short Game Pos. 2 Easy",
  "2_full_programmatic2"    = "Exp. 3: Full Game Programmatic",
  "9_short_pos3_hard"       = "Exp. 10: Short Game Pos. 3 Hard"
)

experiment_order <- c(
  "Exp. 1: Full Game",
  "Exp. 2: Full Game No Special Cards",
  "Exp. 3: Full Game Programmatic",
  "Exp. 4: Short Game No Reprompting",
  "Exp. 5: Short Game Pos. 1 Easy",
  "Exp. 6: Short Game Pos. 1 Hard",
  "Exp. 7: Short Game Pos. 2 Easy",
  "Exp. 8: Short Game Pos. 2 Hard",
  "Exp. 9: Short Game Pos. 3 Easy",
  "Exp. 10: Short Game Pos. 3 Hard"
)

df <- df[2:length(df)]
df$model <- sapply(df$model, extract_model_name)
df$episode <- sapply(df$episode, extract_no_episode)
df$model <- model_mapping[df$model]
df$experiment <- experiment_mapping[df$experiment]
df$metric <- as.factor(df$metric)
summary(df)
head(df)

##########################Counted metrics###########################
unique(df$metric)
# Boxes
plot_data <- df %>%
  filter(metric %in% c("Lose", "Played", "Aborted", "Success")) %>%
  group_by(model, metric) %>%
  summarise(
    count = sum(value == 1, na.rm = TRUE),
    total = n(),
    percentage = mean(value == 1, na.rm = TRUE) * 100
  ) %>%
  arrange(metric)

p <- ggplot(subset(plot_data, metric=="Success"), aes(x = model, y = percentage, fill = model)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.1f%%", percentage)), 
            vjust = -0.5, size = 3) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Percentage of Successful Games by Model",
       subtitle = "Count of all episodes and experiments.",
       x = "Model", 
       y = "Percentages") +
  scale_y_continuous(limits = c(0, 100))

ggsave(
  filename = "./plots/metrics/aborted_per_model.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

# Heatmap
plot_data <- df %>%
  filter(metric %in% c("Lose", "Played", "Aborted", "Success")) %>%
  group_by(model, experiment, metric) %>%
  summarise(
    count = sum(value == 1, na.rm = TRUE),
    total = n(),
    percentage = mean(value == 1, na.rm = TRUE) * 100
  ) %>%
  arrange(metric)

p <- ggplot(subset(plot_data, metric=="Lose"), aes(x = experiment, y = model, fill = percentage)) +
  geom_tile() +
  geom_text(aes(label = sprintf("%.1f%%", percentage)), color = "white", size = 3) +
  scale_fill_gradient(low = "#0079FF", high = "#FF0060") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Percentage of Lost Games by Model and Experiment",
       subtitle = "Mean of all episodes and experiments.",
       x = "Experiment", 
       y = "Model",
       fill = "Percentage")

ggsave(
  filename = "./plots/metrics/Lost_per_model_per_experiment.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

##########################Errors###########################

# Boxes: Semantics vs Syntax
plot_data <- df %>%
  filter(metric %in% c("semantics_errors", "syntax_errors" )) %>%
  mutate(metric=replace(metric, metric=="Violated Request Count", "violated_request_count")) %>%
  group_by(model, metric) %>%
  summarise(
    count = sum(value, na.rm = TRUE),
  )  %>% group_by(model) %>%
  mutate(percentage = count / sum(count) * 100)

p <- ggplot(plot_data, aes(fill=metric, y=count, x=model)) + 
  geom_bar(position="fill", stat="identity") +
  geom_text(aes(label = paste0(round(percentage, 1), "%"), 
                y = cumsum(count)),
            position = position_fill(vjust = 0.5), 
            color = "white", size = 4) +
  scale_y_continuous(labels = scales::percent_format(), expand = c(0, 0)) +
  scale_fill_manual(values = c("semantics_errors" = "#1e3a5f", "syntax_errors" = "#ff6f40")) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(title = "Breakdown of Violated Request Count",
       subtitle = "Semantics Errors vs Syntax Errors. Count of all episodes and experiments.",
       x = "Model", 
       y = "Percentage")

ggsave(
  filename = "./plots/metrics/errors_per_model.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

# Boxes: Parsed vs Violated
plot_data <- df %>%
  filter(metric %in% c("Violated Request Count", "Parsed Request Count" )) %>%
  #mutate(metric=replace(metric, metric=="Violated Request Count", "violated_request_count")) %>%
  #mutate(metric=replace(metric, metric=="Parsed Request Count", "parsed_request_count")) %>%
  group_by(model, metric) %>%
  summarise(
    count = sum(value, na.rm = TRUE),
  )  %>% group_by(model) %>%
  mutate(percentage = count / sum(count) * 100)

p <- ggplot(plot_data, aes(fill=metric, y=count, x=model)) + 
  geom_bar(position="fill", stat="identity") +
  geom_text(aes(label = paste0(round(percentage, 1), "%"), 
                y = cumsum(count)),
            position = position_fill(vjust = 0.5), 
            color = "white", size = 4) +
  scale_y_continuous(labels = scales::percent_format(), expand = c(0, 0)) +
  scale_fill_manual(values = c("Parsed Request Count" = "#1e3a5f", "Violated Request Count" = "#ff6f40")) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(title = "Breakdown of Request Count",
       subtitle = "Count of all episodes and experiments.",
       x = "Model", 
       y = "Percentage")

ggsave(
  filename = "./plots/metrics/parsedvsviolated_per_model.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

# Boxes: Other errors
plot_data <- df %>%
  filter(metric %in% c("error_card_doesnt_follow_suit", "error_card_not_in_hand", "error_prediction_int_not_possible" )) %>%
  group_by(model, metric) %>%
  summarise(
    count = sum(value, na.rm = TRUE),
  )  %>% group_by(model) %>%
  mutate(percentage = count / sum(count) * 100)

p <- ggplot(plot_data, aes(fill=metric, y=count, x=model)) + 
  geom_bar(position="fill", stat="identity") +
  geom_text(aes(label = paste0(round(percentage, 1), "%"), 
                y = cumsum(count)),
            position = position_fill(vjust = 0.5), 
            color = "white", size = 3) +
  scale_y_continuous(labels = scales::percent_format(), expand = c(0, 0)) +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1),
        legend.title = element_blank(),
        legend.position = "bottom") +
  labs(title = "Breakdown of Errors",
       subtitle = "Count of all episodes and experiments.",
       x = "Model", 
       y = "Percentage")

ggsave(
  filename = "./plots/metrics/allerrors_per_model_per_experiment.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

# Heatmap: Semantics vs Syntax
plot_data <- df %>%
  filter(metric %in% c("semantics_errors", "syntax_errors" )) %>%
  mutate(metric=replace(metric, metric=="Violated Request Count", "violated_request_count")) %>%
  mutate(experiment = factor(experiment, labels=experiment_order)) %>%
  group_by(model, experiment, metric) %>%
  summarise(
    count = sum(value, na.rm = TRUE),
  )  %>% group_by(model) %>%
  mutate(percentage = count / sum(count) * 100)

p <- ggplot(subset(plot_data, metric=="syntax_errors"), aes(x = experiment, y = model, fill = percentage)) +
  geom_tile() +
  geom_text(aes(label = sprintf("%.1f%%", percentage)), color = "white", size = 4) +
  scale_fill_gradient(low = "#0079FF", high = "#FF0060") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Percentage of Syntax Errors by Model and Experiment",
       subtitle = "Count of all episodes and experiments.",
       x = "Experiment", 
       y = "Model",
       fill = "Percentage")

ggsave(
  filename = "./plots/metrics/syntaxserrors_per_model_per_experiment.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)
##########################Main Score###############################
plot_data <- df %>%
  filter(metric %in% c("Main Score")) %>%
  mutate(experiment = factor(experiment, labels=experiment_order)) %>%
  group_by(model, experiment, episode, metric) %>%
  summarise(
    value = mean(value, na.rm = TRUE),
  )

# Boxplot for each model
p <- ggplot(plot_data, aes(x = model, y = value)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, aes(color = model), size = 2) +
  labs(title = paste("Clemscore for each model"),
       subtitle = "Mean of all episodes and experiments.",
       x = "Model", 
       y = "Main Score") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Rotate x-axis labels
  
ggsave(
  filename = "./plots/metrics/main_score_per_model.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

slice1 <- plot_data %>%
  filter(experiment %in% c(experiment_order[1:5]))
slice2 <- plot_data %>%
  filter(experiment %in% c(experiment_order[6:10]))

# Boxplot for each experiment
p <- ggplot(slice2, aes(x = model, y = value)) +
  geom_boxplot(outlier.shape = NA) +
  geom_jitter(width = 0.2, aes(color = model), size = 2) +
  facet_wrap(~ experiment, ncol = 2,) + # Overlay scatter points
  labs(title = paste("Clemscore for each model"),
       subtitle = "Mean of all episodes and experiments.",
       x = "Model", 
       y = "Main Score") +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1))  # Rotate x-axis labels

ggsave(
  filename = "./plots/metrics/main_score_per_model_per_experiment#2.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)

##########################Last round###############################
plot_data <- df %>%
  filter(experiment %in% c("Exp. 4: Short Game No Reprompting")) %>%
  filter(metric %in% c("last_round")) %>%
  group_by(model) %>%
  summarise(
    value = mean(value, na.rm = TRUE),
  )


p <- ggplot(plot_data, aes(x = model, y = value, fill = model)) +
  geom_bar(stat = "identity") +
  geom_text(aes(label = sprintf("%.2f", value)), 
            position = position_fill(vjust = 0.5), color = "white", size = 3) +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Last round in Experiment 4: Short Game No Reprompting",
       subtitle = "Count for all episodes.",
       x = "Model", 
       y = "Round number") 

ggsave(
  filename = "./plots/metrics/last_round_per_model_exp#4.png",
  plot = p,
  width = 15,
  height = 10,
  dpi = 300
)
