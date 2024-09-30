# install.packages("ggplot2")
# install.packages("RColorBrewer")
# install.packages("wesanderson")
# install.packages("psych")

library(psych)   
library(RColorBrewer) # display.brewer.all()
library(tidyverse)
library(dplyr)
library(ggplot2)
library(stringr)
library(wesanderson)

##########################CONFIG###########################

df <- read.csv('raw_rounds.csv')

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
#df$experiment_order <- experiment_order[df$experiment]
df$model <- sapply(df$model, extract_model_name)
df$episode <- sapply(df$episode, extract_no_episode)
df$model <- model_mapping[df$model]
df$experiment <- experiment_mapping[df$experiment]

summary(df)
head(df)

##########################PLOT 1###########################

generate_episode_per_experiment_plot <- function(df, model_name, experiment_name, points=FALSE) {
  plot_data <- df %>%
    filter(model == model_name,
           experiment == experiment_name) %>%
    mutate(episode = factor(episode)) 
  
  if(nrow(plot_data) == 0) {
    
    return(NULL)
  
  } else if(!(points==FALSE)) {
    slope_data <- plot_data %>%
      group_by(episode) %>%
      summarize(
        slope = if(n() > 1) {
          as.numeric(coef(glm(points ~ round, data=cur_data(), family = "gaussian"))["round"])
        } else {
          NA
        },
        p_value = if(n() > 1) {
          summary(glm(points ~ round, data=cur_data(), family = "gaussian"))$coefficients["round", "Pr(>|t|)"]
        } else {
          NA
        },
        r_squared = if(n() > 1) {
          1 - (glm(points ~ round, data=cur_data(), family = "gaussian")$deviance / glm(points ~ round, data=cur_data(), family = "gaussian")$null.deviance)
        } else {
          NA
        }
      )
    
    slope_data <- slope_data %>%
      mutate(
        formatted_p_value = sapply(p_value, function(x) {
          if (is.finite(x) && x < 0.05) {
              formatC(x, format = "e", digits = 2)
          } else if (is.finite(x)) {
              round(x, 4)
          } else {
              NA  
          }
        })
      )
    
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = points, color = "Points"), size = 1) +
      scale_color_manual(values = c("Points" = "#1e3a5f")) +
      facet_wrap(~ episode, ncol = 2, scales = "free_y") +
      geom_smooth(aes(y = points, color = "Points"), method = "glm", 
                  formula = y ~ x, se = TRUE, linetype = 6) +
      geom_text(data = slope_data %>% group_by(episode) %>% slice(1),
                aes(x= Inf,y= Inf, 
                    label = sprintf("Slope: %.2f\nP-value: %s\nR²: %.2f", 
                    slope, formatted_p_value, r_squared),
                hjust = 1, vjust = 1.2, color = "black")) +
      labs(title = paste0(model_name, ": Points per round"),
           subtitle = paste(experiment_name),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_bw() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text())
    
    return(output)
  
  } else {
    cor_data <- plot_data %>%
      group_by(episode) %>%
      summarize(
        cor = if (sum(is.finite(predictions)) >= 3 & sum(is.finite(tricks_per_player)) >= 3) {
          cor.test(predictions, tricks_per_player)$estimate
        } else {
          NA
        },
        p_value = if (sum(is.finite(predictions)) >= 3 & sum(is.finite(tricks_per_player)) >= 3) {
          cor.test(predictions, tricks_per_player)$p.value
        } else {
          NA
        }
      )
    
    cor_data <- cor_data %>%
      mutate(
        formatted_p_value = sapply(p_value, function(x) {
              if (is.finite(x) && x < 0.05) {
                formatC(x, format = "e", digits = 2)
              } else if (is.finite(x)) {
                round(x, 4)
              } else {
                NA
              }
            })
        )
    
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = predictions, color = "Predictions"), size = 1) +
      geom_line(aes(y = tricks_per_player, color = "Tricks per Player"), size = 1) +
      geom_text(data = cor_data %>% group_by(episode) %>% slice(1),
                aes(x= -Inf,y= Inf, 
                    label = sprintf("Correlation: %.4f\nP-value: %s",
                                    cor, formatted_p_value),
                    hjust = -0.1, vjust = 1.2, color = "black")) +
      scale_color_manual(
        values = c(
          "Predictions" = "#1e3a5f", 
          "Tricks per Player" = "#ff6f40"
        ),
        breaks = c("Predictions", "Tricks per Player"),
        labels = c("Predictions", "Tricks per Player")
      ) +
      facet_wrap(~ episode, ncol = 2, scales = "free_y") +
      labs(title = paste0(model_name, ": Predictions vs Tricks per round"),
           subtitle = paste(experiment_name),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_bw() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text())
    return(output)
  }
}

##########################PLOT 2###########################

generate_per_experiment_plot <- function(df, model_name, points=FALSE) {
  if (!(points==FALSE)) {
    plot_data <- df %>%
      filter(model == model_name) %>%
      mutate(experiment = factor(experiment, levels = experiment_order)) %>%
      group_by(experiment, round) %>% 
      summarize(mean_points = harmonic.mean(points),
                .groups = 'drop') %>%
      filter(is.finite(mean_points)) 
      
    
    slope_data <- plot_data %>%
      filter(!is.infinite(mean_points)) %>%
      group_by(experiment) %>% 
      summarize(
        slope = if(n() > 1) {
          as.numeric(coef(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))["round"])
        } else {
          NA
        },
        p_value = if(n() > 1) {
          summary(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))$coefficients["round", "Pr(>|t|)"]
        } else {
          NA
        },
        r_squared = if(n() > 1) {
          1 - (glm(mean_points ~ round, data=cur_data(), family = "gaussian")$deviance / glm(mean_points ~ round, data=cur_data(), family = "gaussian")$null.deviance)
        } else {
          NA
        })
        
    if(nrow(plot_data) == 0) {
      return(NULL)
    }
    
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = mean_points, color = "Points"), size = 1) +
      scale_color_manual(values = c("Points" = "#1e3a5f")) +
      geom_smooth(aes(y = mean_points, color = "Points"), method = "glm", 
                  formula = y ~ x, se = TRUE, linetype = 6) +
      geom_text(data = slope_data %>% group_by(experiment) %>% slice(1),
                aes(x= Inf,y= Inf, 
                    label = sprintf("Slope: %.2f\nP-value: %s\nR²: %.2f", 
                                    slope, formatC(p_value, format = "e", digits = 2), r_squared),
                    hjust = 1, vjust = 1.2, color = "black")) +
      facet_wrap(~ experiment, ncol = 2, scales = "free_y") +
      labs(title = paste0(model_name, ": Points per round (Harmonic mean per episode)"),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_bw() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text())
    return(output)
  } else {
    plot_data <- df %>%
      filter(model == model_name,
             predictions > 0,
             tricks_per_player > 0) %>%
      mutate(experiment = factor(experiment, levels = experiment_order)) %>%
      group_by(round, experiment) %>% 
      summarize(mean_predictions = harmonic.mean(predictions),  # Calculate harmonic mean predictions
                mean_tricks = harmonic.mean(tricks_per_player),  # Calculate harmonic mean tricks per player
                .groups = 'drop')
    
    if(nrow(plot_data) == 0) {
      return(NULL)  # Return NULL if no data for this combination
    }
    
    cor_data <- plot_data %>%
      group_by(experiment) %>%
      summarize(
        cor = if (sum(is.finite(mean_predictions)) >= 3 & sum(is.finite(mean_tricks)) >= 3) {
          cor.test(mean_predictions, mean_tricks)$estimate
        } else {
          NA
        },
        p_value = if (sum(is.finite(mean_predictions)) >= 3 & sum(is.finite(mean_tricks)) >= 3) {
          cor.test(mean_predictions, mean_tricks)$p.value
        } else {
          NA
        }
      )
    
    cor_data <- cor_data %>%
      mutate(
        formatted_p_value = sapply(p_value, function(x) {
            if (is.finite(x) && x < 0.05) {
              formatC(x, format = "e", digits = 2)
            } else if (is.finite(x)) {
              round(x, 4)
            } else {
              NA
            }
            })
      )
    
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = mean_predictions , color = "Predictions"), size = 1) +
      geom_line(aes(y = mean_tricks, color = "Tricks per Player"), size = 1) +
      geom_text(data = cor_data %>% group_by(experiment) %>% slice(1),
                aes(x= -Inf, y = Inf, 
                    label = sprintf("Correlation: %.4f\nP-value: %s", 
                                    cor, formatted_p_value),
                    hjust = -0.1, vjust = 1.2, color = "black")) +
      scale_color_manual(
        values = c(
          "Predictions" = "#1e3a5f", 
          "Tricks per Player" = "#ff6f40"
        ),
        breaks = c("Predictions", "Tricks per Player"),
        labels = c("Predictions", "Tricks per Player")
      ) +
      facet_wrap(~ experiment, ncol = 2, scales = "free_y") +
      labs(title = paste0(model_name, ": Predictions vs Tricks per round (Harmonic mean for each episode)"),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_bw() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text())
    return(output)
  }
}

##########################PLOT 3###########################

generate_per_model_plot <- function(df, points=FALSE) {
  # Add p-value decimals
  if (!(points==FALSE)) {
    plot_data <- df %>%
      group_by(model, round) %>%
      summarize(mean_points = harmonic.mean(points),
                .groups = 'drop') 
    
    if(nrow(plot_data) == 0) {
      return(NULL)  # Return NULL if no data for this combination
    }
    
    slope_data <- plot_data %>%
      group_by(model) %>%
      summarize(slope = as.numeric(coef(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))["round"]),
                p_value = summary(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))$coefficients["round", "Pr(>|t|)"],
                r_squared = 1 - (glm(mean_points ~ round, data=cur_data(), family = "gaussian")$deviance / glm(mean_points ~ round, data=cur_data(), family = "gaussian")$null.deviance))

    slope_data <- slope_data %>%
      mutate(
        formatted_p_value = sapply(p_value, function(x) {
          if (is.finite(x) && x < 0.05) {
            formatC(x, format = "e", digits = 2)
          } else if (is.finite(x)) {
            round(x, 4)
          } else {
            NA  
          }
        })
      )
    
    
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = mean_points, color = "Points"), size = 1) +
      scale_color_manual(values = c("Points" = "#1e3a5f")) +
      facet_wrap(~ model, ncol = 2, scales = "free_y") +
      geom_smooth(aes(y = mean_points, color = "Predictions"), method = "glm", 
                  formula = y ~ x, se = TRUE, linetype = 6) +
      geom_text(data = slope_data %>% group_by(model) %>% slice(1),
                aes(x= Inf,y= -Inf, 
                    label = sprintf("Slope: %.4f\nP-value: %s\nR²: %.4f", 
                                    slope, formatted_p_value, r_squared),
                    hjust = 1, vjust = 0, color = "black")) +
      labs(title = paste0("Points per round (harmonic mean for each experiment and episode)"),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_minimal() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text(face = "bold"))
    return(output)
  } else {
    plot_data <- df %>%
      group_by(model, round) %>%
      summarize(mean_predictions = harmonic.mean(predictions),
                mean_tricks = harmonic.mean(tricks_per_player),
                .groups = 'drop') 
    
    if(nrow(plot_data) == 0) {
      return(NULL)  # Return NULL if no data for this combination
    }
    
    cor_data <- plot_data %>%
      group_by(model) %>%
      summarize(cor = cor.test(mean_predictions, mean_tricks)$estimate,
                p_value = cor.test(mean_predictions, mean_tricks)$p.value)
    
    cor_data <- cor_data %>%
      mutate(
        formatted_p_value = sapply(p_value, function(x) {
          tryCatch(
            {
              if (is.finite(x) && x < 0.05) {
                # Format in scientific notation
                formatC(x, format = "e", digits = 2)
              } else if (is.finite(x)) {
                # Round normally if not significant
                round(x, 4)
              } else {
                "NA"  # Handle non-finite values
              }
            },
            error = function(cond) {
              message(conditionMessage(cond))  # Print error message
              "NA"  # Default to "NA" on error
            }
          )
        })
      )
      
    output <- ggplot(plot_data, aes(x = round)) +
      geom_line(aes(y = mean_predictions , color = "Predictions"), size = 1) +
      geom_line(aes(y = mean_tricks, color = "Tricks per Player"), size = 1) +
      geom_text(data = cor_data %>% group_by(model) %>% slice(1),
                aes(x= Inf,y= -Inf, 
                    label = sprintf("Correlation: %.4f\nP-value: %s", 
                                    cor, formatted_p_value),
                    hjust = 1, vjust = 0, size = 1, color = "black")) +
      scale_color_manual(
        values = c(
          "Predictions" = "#1e3a5f", 
          "Tricks per Player" = "#ff6f40"
        ),
        breaks = c("Predictions", "Tricks per Player"),
        labels = c("Predictions", "Tricks per Player")
      ) +
      facet_wrap(~ model, ncol = 2, scales = "free_y") +
      labs(title = paste0("Predictions vs Tricks per round (harmonic mean for each episode)"),
           x = "Round",
           y = "Value",
           color = "Metric") +
      theme_minimal() +
      theme(legend.position = "bottom",
            strip.background = element_rect(fill = "#f0f0f0"),
            strip.text = element_text(face = "bold"))
    return(output)
  }
}

##########################TODOS###########################

# 1) Calculate error rate between prediction vs tricks -> is the median std. dev. high? If not, implies same mistakes over and over again.
# 2) Considering slope + corr of 2 + 3, generate tables with info and marking if p-value is valuable for each model/experiment and model alone

##########################TESTING##########################

generate_episode_per_experiment_plot(df, "Mistral NeMo (12B)", "Exp. 2: Full Game No Special Cards", TRUE)
generate_episode_per_experiment_plot(df, "Qwen2-72B-Instruct", "0_full_game")

generate_per_experiment_plot(df, "Mistral NeMo (12B)", TRUE)
generate_per_experiment_plot(df, "Mistral NeMo (12B)")

generate_per_model_plot(df, TRUE)
generate_per_model_plot(df,)

##########################GENERATE PLOTS###########################

generate_all_combined_plots_per_episode <- function(df, output_dir = "./plots/per_episode") {
  dir.create(output_dir, showWarnings = FALSE)
  
  plot_combinations <- df %>%
    select(model, experiment) %>%
    distinct()
  
  for(i in 1:nrow(plot_combinations)) {
    model_name <- plot_combinations$model[i]
    experiment_name <- plot_combinations$experiment[i]
    experiment_number <- as.integer(str_extract(experiment_name, "\\d+"))
          
    tryCatch({
    p1 <- generate_episode_per_experiment_plot(df, model_name, experiment_name, TRUE)
    p2 <- generate_episode_per_experiment_plot(df, model_name, experiment_name)
    
    if(!is.null(p1)) {
      filename <- paste0(gsub("[^a-zA-Z0-9]", "_", model_name), "_Exp_",
                         experiment_number, "_Points.png")
      ggsave(
        filename = file.path(output_dir, filename),
        plot = p1,
        width = 15,
        height = 10,
        dpi = 300
      )
      cat("Saved plot:", filename, "\n")
      
    }
    if(!is.null(p2)) {
      filename <- paste0(gsub("[^a-zA-Z0-9]", "_", model_name), "_Exp_",
                         experiment_number, "_TVP.png")
      ggsave(
        filename = file.path(output_dir, filename),
        plot = p2,
        width = 15,
        height = 10,
        dpi = 300
      )
      cat("Saved plot:", filename, "\n")
    }
    }, error = function(e) {
      message("Error generating plots for model: ", model_name, ", experiment: ", experiment_name)
      message("Error message: ", conditionMessage(e))
    })
  }
    
} 

generate_all_combined_plots_per_experiment <- function(df, output_dir = "./plots/per_experiment") {
  dir.create(output_dir, showWarnings = FALSE)
  
  plot_combinations <- df %>%
    select(model) %>%
    distinct()
  
  for(i in 1:nrow(plot_combinations)) {
    model_name <- plot_combinations$model[i]

    tryCatch({
      p1 <- generate_per_experiment_plot(df, model_name, TRUE)
      p2 <- generate_per_experiment_plot(df, model_name)
      
      if(!is.null(p1)) {
        filename <- paste0(gsub("[^a-zA-Z0-9]", "_", model_name), 
                           "_Points.png")
        ggsave(
          filename = file.path(output_dir, filename),
          plot = p1,
          width = 15,
          height = 10,
          dpi = 300
        )
        cat("Saved plot:", filename, "\n")
        
      }
      
      if(!is.null(p2)) {
        filename <- paste0(gsub("[^a-zA-Z0-9]", "_", model_name), 
                           "_TVP.png")
        ggsave(
          filename = file.path(output_dir, filename),
          plot = p2,
          width = 15,
          height = 10,
          dpi = 300
        )
        cat("Saved plot:", filename, "\n")
      }
    }, error = function(e) {
      message("Error generating plots for model: ", model_name,)
      message("Error message: ", conditionMessage(e))
    })
  }
  
} 

# generate_all_combined_plots_per_episode(df)
# generate_all_combined_plots_per_experiment(df)

# generate_per_model_plot(df, TRUE)
# generate_per_model_plot(df,)


##########################TABLE 1###########################

get_significance_score <- function(p_value) {
  if (is.na(p_value) || p_value >= 0.05) {
    return(0)  # Not significant
  } else if (p_value < 0.001) {
    return(3)  # Highly significant
  } else if (p_value < 0.01) {
    return(2)  # Significant
  } else if (p_value < 0.05) {
    return(1)  # Marginally significant
  }}

get_r_squared_score <- function(r_squared) {
  if (is.na(r_squared)) {
    return(0)  # Not significant
  } else if (r_squared < 0.1) {
    return(1)  # Low explanatory power
  } else if (r_squared < 0.25) {
    return(2)  # Moderate explanatory power
  } else {
    return(3)  # High explanatory power
  }}

result_table <- df %>%
  mutate(experiment = factor(experiment, levels = experiment_order)) %>%
  group_by(model, experiment,  round) %>% 
  summarize(mean_points = harmonic.mean(points),
            .groups = 'drop') %>%
  filter(!is.infinite(mean_points)) %>%
  group_by(model, experiment) %>%
  summarize(
    slope = if(n() > 1) {
      as.numeric(coef(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))["round"])
    } else {
      NA
    },
    p_value = if(n() > 1) {
      summary(glm(mean_points ~ round, data=cur_data(), family = "gaussian"))$coefficients["round", "Pr(>|t|)"]
    } else {
      NA
    },
    r_squared = if(n() > 1) {
      1 - (glm(mean_points ~ round, data=cur_data(), family = "gaussian")$deviance / 
             glm(mean_points ~ round, data=cur_data(), family = "gaussian")$null.deviance)
    } else {
      NA
    },
    significance_score_p = get_significance_score(p_value),  # Add p-value significance score
    significance_score_r2 = get_r_squared_score(r_squared),  # Add R-squared significance score
    .groups = 'drop'
    ) 

result_table2 <- df %>%
  filter(predictions > 0,
         tricks_per_player > 0) %>% 
  group_by(model, experiment, round) %>% 
  summarize(mean_predictions = harmonic.mean(predictions),
            mean_tricks = harmonic.mean(tricks_per_player),
            .groups = 'drop') %>%
  group_by(model) %>%
  summarize(
    cor = if (sum(is.finite(mean_predictions)) >= 3 & sum(is.finite(mean_tricks)) >= 3) {
      cor.test(mean_predictions, mean_tricks)$estimate
    } else {
      NA
    },
    p_value = if (sum(is.finite(mean_predictions)) >= 3 & sum(is.finite(mean_tricks)) >= 3) {
      cor.test(mean_predictions, mean_tricks)$p.value
    } else {
      NA
    },
    significance_score_p = get_significance_score(p_value),
    .groups = 'drop'
  )

result_table2 
write.csv(result_table2, file = "cor_per_model_per_experiment.csv", row.names = FALSE)
