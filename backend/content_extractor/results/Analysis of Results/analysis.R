library(tidyverse)
library(dplyr)
library(ggplot2)
#install.packages("tidyverse")
library(xtable)
library(tidyverse)
library(ggplot2)
library(gridExtra)
#install.packages("reshape")
library(reshape)
library(psych)
#install.packages("ggridges")
library(ggridges)

##########################CONFIG EVALUATION###########################

df_eval <- read.csv('data/csv/evaluation.csv')

df_eval <- df_eval %>%
  filter(F1_Score != 1, F1_Score>0, Accuracy >0)

df_expand <- read.csv('data/csv/dataset_list.csv', na.strings = NA)
df_expand <- df_expand[1:8]
colnames(df_expand)[1] <- "Filename"

df <- merge(df_eval, df_expand, by="Filename")

df <- read.csv('data/csv/final_df.csv', sep = ";", dec =",", header = TRUE)

df$Config <- as.factor(df$Config)
df$OCR_module <- as.factor(df$OCR_module)
df$LLM_model <- as.factor(df$LLM_model)
df$image_quality <- as.factor(df$image_quality)
df$watermark_present <- as.factor(df$watermark_present)
df$image_source <- as.factor(df$image_source)
df$color_mode <- as.factor(df$color_mode)
df$content_type <- as.factor(df$content_type)
df$language <- as.factor(df$language)
df$Filename <- as.factor(df$Filename)
df$rotation <- ifelse(df$rotation_angle!=0, "yes", "no")
df$rotation <- as.factor(df$rotation)

df$Skew_Correction <- as.factor(df$Skew_Correction)
df$Binarization <- as.factor(df$Binarization)
df$Noise_Removal <- as.factor(df$Noise_Removal)

summary(df)

##########################CONFIG LIST###########################

df_config <- read.csv('data/txt/list_config.txt', header = FALSE, na.strings = NA)
colnames(df_config) <- c("Config", "Binarization", "Skew_Correction", "Noise_Removal")

df_config$Config <- as.factor(df_config$Config)
df_config$Binarization <- as.factor(df_config$Binarization)
df_config$Skew_Correction <- as.factor(df_config$Skew_Correction)
df_config$Noise_Removal <- as.factor(df_config$Noise_Removal)

summary(df_config)

df <- merge(df, df_config, by="Config")

##########################CONFIG PRE###########################

df_preprocessing <- read.csv('data/txt/preprocessing_log.txt', header = FALSE, sep = "-", na.strings = NA)

df_preprocessing$Config <- gsub(".*config(\\d+)\\.tiff $", "\\1", df_preprocessing$V1)
df_preprocessing$Pre_Time <- gsub(".*: (\\S+).*", "\\1", df_preprocessing$V2)
df_preprocessing$Filename <- gsub(".*?/(example\\d+)_config.*", "\\1", df_preprocessing$V1)
df_preprocessing <- df_preprocessing[5:length(colnames(df_preprocessing))]

df_preprocessing$Config <- as.factor(df_preprocessing$Config)
df_preprocessing$Filename <- as.factor(df_preprocessing$Filename)
df_preprocessing$Pre_Time <- as.numeric(df_preprocessing$Pre_Time)

df_preprocessing$Pre_Time <- ifelse(is.na(df_preprocessing$Pre_Time), 0, df_preprocessing$Pre_Time)
summary(df_preprocessing)

df <- merge(df, df_preprocessing, by=c("Config", "Filename"))

##########################CONFIG OCR###########################

lines <- readLines('data/txt/ocr_results_log.txt')
extract_info <- function(line) {
  config_number <- gsub(".*example(\\d+)_config(\\d+)\\.tiff.*", "\\2", line)
  ocr_module <- gsub(".*OCR:\\s*(\\S+)\\s*-.*", "\\1", line)
  filename <- gsub(".*example(\\d+)_config(\\d+)\\.tiff.*", "example\\1", line)
  ocr_time <- gsub(".*Time needed: (\\d+)*", "\\1", line) 
  ocr_time <- gsub(" -.*", "", ocr_time)
  return(c(config_number, ocr_module, filename, ocr_time))
}

df_ocr <- list()

x <- 0
for (line in lines) {
  x <- x + 1
  extracted_info <- extract_info(line)
  df_ocr <- rbind(df_ocr, extracted_info)
  print(x)
}

df_ocr <- as.data.frame(df_ocr)

colnames(df_ocr) <- c("Config", "OCR_module", "Filename", "OCR_Time")

df_ocr$Config <- as.numeric(df_ocr$Config)
df_ocr$OCR_module <- as.character(df_ocr$OCR_module)
df_ocr$Filename <- as.character(df_ocr$Filename)
df_ocr$OCR_Time <- as.numeric(df_ocr$OCR_Time)

df_ocr$Config <- as.factor(df_ocr$Config)
df_ocr$Filename <- as.factor(df_ocr$Filename)
df_ocr$OCR_module <- as.factor(df_ocr$OCR_module)

summary(df_ocr)

df <- merge(df, df_ocr, by=c("Config", "Filename", "OCR_module"))

# write.csv(df_ocr, "data/csv/ocr.csv", row.names = FALSE)

##########################CONFIG OCR 2###########################

df_ocr <- read.csv('data/csv/ocr.csv', header = TRUE, sep = ",", na.strings = NA)

df_ocr$Config <- as.factor(df_ocr$Config)
df_ocr$Filename <- as.factor(df_ocr$Filename)
df_ocr$OCR_module <- as.factor(df_ocr$OCR_module)

summary(df_ocr)

df <- merge(df, df_ocr, by=c("Config", "Filename", "OCR_module"))

##########################CONFIG POST###########################

file_list <- list.files(path = "./data/txt/", pattern = "^postprocessing_.*\\.txt$", full.names = TRUE)

df_postprocessing <- do.call(rbind, lapply(file_list, function(file) read.csv(file, header = FALSE, sep = "-", na.strings = NA)))

df_postprocessing$Config <- gsub(".*config(\\d+)\\.tiff $", "\\1", df_postprocessing$V1)
df_postprocessing$Post_Time <- gsub(".*: (\\S+).*", "\\1", df_postprocessing$V5)
df_postprocessing$Filename <- gsub(".*?/(example\\d+)_config.*", "\\1", df_postprocessing$V1)
df_postprocessing$OCR_module <- gsub(".*OCR: (\\S+).*", "\\1", df_postprocessing$V2)
df_postprocessing$LLM_model <- gsub(".*LLM: (\\S+).*", "\\1", df_postprocessing$V3)
df_postprocessing <- df_postprocessing[6:length(colnames(df_postprocessing))]

df_postprocessing$Config <- as.factor(df_postprocessing$Config)
df_postprocessing$Filename <- as.factor(df_postprocessing$Filename)
df_postprocessing$OCR_module <- as.factor(df_postprocessing$OCR_module)
df_postprocessing <- subset(df_postprocessing, LLM_model != "Mistral7B")
df_postprocessing$LLM_model <- as.factor(df_postprocessing$LLM_model)
df_postprocessing$Post_Time <- as.numeric(df_postprocessing$Post_Time)

levels(df$LLM_model) <- c("Gemma2", "Llama3", "Mistral", "Phi3", "Qwen2")

df <- merge(df, df_postprocessing, by=c("Config", "Filename", "OCR_module", "LLM_model" ))

####################SAVE###################

df$Time <- df$OCR_Time + df$Pre_Time + df$Post_Time 
write.table(df, file = "data/csv/final_df.csv", row.names = FALSE, dec = ",", sep = ";", quote = FALSE, col.names = TRUE)

####################BALANCE###################
create_balance_report <- function(data, variable) {
  if (!variable %in% names(data)) {
    warning(paste("Variable", variable, "not found in the dataset. Skipping."))
    return(NULL)
  }
  
  balance_report <- data %>%
    group_by(!!sym(variable)) %>%
    summarise(n = n()) %>%
    mutate(percentage = n / sum(n) * 100) %>%
    arrange(desc(n))
  
  return(balance_report)
}

plot_balance <- function(data, variable) {
  # Check if "n" column exists, otherwise count occurrences of each level in 'variable'
  if(!"n" %in% colnames(data)) {
    data <- data %>%
      group_by(!!sym(variable)) %>%
      summarize(n = n())
  }
  
  # Calculate mean of 'n'
  mean_n <- mean(data$n)
  
  ggplot(data, aes(x = reorder(!!sym(variable), -n), y = n)) +
    geom_bar(stat = "identity", fill = "steelblue") +
    geom_hline(yintercept = mean_n, linetype = "dashed", color = "red", size = 1) + # Add mean line
    theme_bw() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
    labs(title = paste("Balance of", variable),
         x = variable,
         y = "Count")
  
}

balance_plots <- lapply(cat_vars, function(var) plot_balance(df, var))

grid.arrange(grobs = balance_plots, ncol = 2)

# Analyze numeric variables
numeric_vars <- c("Accuracy", "F1_Score", "Pre_Time", "OCR_Time", "Post_Time", "Time")

numeric_summary <- df %>%
  select(all_of(numeric_vars)) %>%
  summary()

print(numeric_summary)

cor_matrix <- cor(df[, numeric_vars])
print(cor_matrix)

# Add row and column names
rownames(cor_matrix) <- c("Accuracy", "F1_Score", "Pre_Time", "OCR_Time", "Post_Time", "Time")
colnames(cor_matrix) <- c("Accuracy", "F1_Score", "Pre_Time", "OCR_Time", "Post_Time", "Time")

# Melt the correlation matrix for ggplot
cor_matrix_melted <- melt(cor_matrix)

# Plot the correlation heatmap
ggplot(data = cor_matrix_melted, aes(X1, X2, fill = value)) + 
  geom_tile() +
  scale_fill_gradient2(low = "blue", high = "red", mid = "white", 
                       midpoint = 0, limit = c(-1, 1), space = "Lab", 
                       name="Correlation") +
  theme_minimal() + 
  theme(axis.text.x = element_text(angle = 45, vjust = 1, size = 10, hjust = 1),
        axis.text.y = element_text(size = 10)) +
  coord_fixed() +
  labs(title = "Correlation Heatmap of Numeric Variables",
       x = "Variables", 
       y = "Variables")

####################GENERAL###################

print(xtable(head(general, n=10)), include.rownames=FALSE)

summary(df)

general <- df %>%
  group_by(Config, OCR_module, LLM_model) %>%
  summarise(
    Accuracy = harmonic.mean(Accuracy, na.rm = TRUE),
    F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
    Time = harmonic.mean(Time, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  arrange(desc(F1_Score), desc(Accuracy), desc(Time))

general <- df %>%
  group_by(Config, OCR_module, LLM_model) %>%
  summarise(
    Accuracy = mean(Accuracy, na.rm = TRUE),
    F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
    Time = harmonic.mean(Time, na.rm = TRUE),
    Score = F1_Score / Time,  # Example composite scoring
    .groups = "drop"
  ) %>%
  arrange(desc(Score))

head(general, n=10)

mean(head(general$Time, n=10))

# Consider also without Configs -> Phi+Tesseract not that bad, as less errors than Gemma2+Tesseract


####################Quality###################
for (i in seq(1,length(unique(df$image_quality)), by=1)) {
  print(unique(df$image_quality)[i])
  
  output <- df %>%
    filter(image_quality == unique(df$image_quality)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
      Time = harmonic.mean(Time, na.rm = TRUE),
      Tradeoff = F1_Score / Time,  # Example composite scoring
      .groups = "drop"
    ) %>% arrange(desc(F1_Score), desc(Time))
  print(xtable(head(output, n=10)), include.rownames=FALSE)
  print(mean(head(output$Accuracy, n=10)))
  print(mean(head(output$F1_Score, n=10)))
  print(mean(head(output$Time, n=10)))
}

####################Source###################
for (i in seq(1,length(unique(df$image_source)), by=1)) {
  print(unique(df$image_source)[i])
  
  output <- df %>%
    filter(image_source == unique(df$image_source)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      #Precision = mean(Precision, na.rm = TRUE),
      #Recall = mean(Recall, na.rm = TRUE),
      F1_Score = mean(F1_Score, na.rm = TRUE),
      .groups = "drop"
    ) %>% arrange(desc(F1_Score))
  print(head(output, n=10))
  print(mean(output$F1_Score))
  print(mean(output$Accuracy))
  print(mean(output$F1_Score))
}

####################Color###################
for (i in seq(1,length(unique(df$color_mode)), by=1)) {
  print(unique(df$color_mode)[i])
  
  output <- df %>%
    filter(color_mode == unique(df$color_mode)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      #Precision = mean(Precision, na.rm = TRUE),
      #Recall = mean(Recall, na.rm = TRUE),
      F1_Score = mean(F1_Score, na.rm = TRUE),
      .groups = "drop"
    ) %>% arrange(desc(F1_Score))
  print(head(output, n=10))
}

####################Content###################
for (i in seq(1,length(unique(df$content_type)), by=1)) {
  print(unique(df$content_type)[i])
  
  output <- df %>%
    filter(content_type == unique(df$content_type)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
      Time = harmonic.mean(Time, na.rm = TRUE),
      Tradeoff = F1_Score / Time,  # Example composite scoring
      .groups = "drop"
    ) %>% arrange(desc(F1_Score), desc(Time))
  print(xtable(head(output, n=10)), include.rownames=FALSE)
  print(mean(head(output$Accuracy, n=10)))
  print(mean(head(output$F1_Score, n=10)))
  print(mean(head(output$Time, n=10)))
}

####################Language###################
for (i in seq(1,length(unique(df$language)), by=1)) {
  print(unique(df$language)[i])
  
  output <- df %>%
    filter(language == unique(df$language)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      #Precision = mean(Precision, na.rm = TRUE),
      #Recall = mean(Recall, na.rm = TRUE),
      F1_Score = mean(F1_Score, na.rm = TRUE),
      .groups = "drop"
    ) %>% arrange(desc(F1_Score))
  print(head(output, n=10))
}

####################Rotation angle###################
for (i in seq(1,length(unique(df$rotation)), by=1)) {
  print(unique(df$rotation)[i])
  
  output <- df %>%
    filter(rotation == unique(df$rotation)[i]) %>%
    group_by(Config, OCR_module, LLM_model) %>%
    summarise(
      Accuracy = mean(Accuracy, na.rm = TRUE),
      F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
      Time = harmonic.mean(Time, na.rm = TRUE),
      Tradeoff = F1_Score / Time,  # Example composite scoring
      .groups = "drop"
    ) %>% arrange(desc(F1_Score), desc(Time))
  print(xtable(head(output, n=10)), include.rownames=FALSE)
  print(mean(head(output$Accuracy, n=10)))
  print(mean(head(output$F1_Score, n=10)))
  print(mean(head(output$Time, n=10)))
}
####################Boxplots###################
summary_df <- df %>%
  group_by(Binarization, Noise_Removal, Skew_Correction)%>%
  summarise(
    Accuracy = harmonic.mean(Accuracy, na.rm = TRUE),
    F1_Score = harmonic.mean(F1_Score, na.rm = TRUE),
    .groups = "drop"
  )

ggplot(summary_df, aes(x = F1_Score, y = Binarization, fill = Binarization)) +
  geom_density_ridges(alpha = 0.6, scale = 1, 
                      quantile_lines = T, quantiles = 2) +
  scale_fill_viridis_d() +
  labs(title = "KDE of F1-Score by Binarization",
       x = "F1-Score",
       y = "Binarization Method") +
  theme_minimal()

ggplot(summary_df, aes(x = F1_Score, y = Noise_Removal, fill = Noise_Removal)) +
  geom_density_ridges(alpha = 0.6, scale = 1, 
                      quantile_lines = T, quantiles = 2) +
  scale_fill_viridis_d() +
  labs(title = "KDE of F1-Score by Noise_Removal",
       x = "F1-Score",
       y = "Binarization Method") +
  theme_minimal()

# Plot for F1 Score by Skew_Correction
ggplot(summary_df, aes(x = F1_Score, y = Skew_Correction, fill = Skew_Correction)) +
  geom_density_ridges(alpha = 0.6, scale = 1, 
                      quantile_lines = T, quantiles = 2) +
  scale_fill_viridis_d() +
  labs(title = "KDE of F1 Score by Noise Removal",
       x = "F1 Score",
       y = "Noise Removal Method") +
  theme_minimal()

best_results <- summary_df %>%
  filter(Accuracy > mean(Accuracy), F1_Score > mean(F1_Score))

pca_best <- best_results %>%
  mutate(across(c(F1_Score, Accuracy), scale)) %>% # Standardize numeric columns
  drop_na() %>%
  select(F1_Score, Accuracy) %>%
  prcomp(center = TRUE, scale. = TRUE)

# Display PCA summary
summary(pca_best)

# Create PCA DataFrame
pca_best_df <- as.data.frame(pca_best$x) %>%
  mutate(Binarization = best_results$Binarization,
         Noise_Removal = best_results$Noise_Removal,
         Skew_Correction = best_results$Skew_Correction)

# Plot PCA Results
ggplot(pca_best_df, aes(x = PC1, y = PC2, color = Noise_Removal, shape = Skew_Correction)) +
  geom_point(size = 3, alpha = 0.6) +
  labs(title = "PCA of Best Configuration Performance",
       x = "Principal Component 1",
       y = "Principal Component 2") +
  theme_minimal() +
  theme(legend.position = "right")



screeplot(pca_results, main = "Scree Plot", col = "blue", pch = 16)

####################Boxplots2###################

summary_df <- df %>%
  group_by(Config, Binarization, Noise_Removal, Skew_Correction) %>%
  summarise(
    F1_Score = mean(F1_Score, na.rm = TRUE),
    Accuracy = mean(Accuracy, na.rm = TRUE),
    n = n(),
    .groups = "drop"
  )

ggplot(summary_df, aes(x = F1_Score, y = Accuracy, size = n)) +
  geom_point(alpha = 0.6, color = "blue") +
  scale_size_continuous(range = c(1, 10), name = "Count of Configurations") +
  theme_minimal() +
  labs(
    title = "Performance of Configurations",
    x = "F1 Score",
    y = "Accuracy"
  ) +
  geom_text(aes(label = Config), vjust = 1.5, hjust = 1.5, size = 3) # Adds labels to points

ggplot(df, aes(x = OCR_module, y = F1_Score, fill = LLM_model)) +
  geom_boxplot() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Distribution of F1 Scores by OCR Module and LLM Model",
       x = "OCR Module", y = "F1 Score", fill = "LLM Model")

ggplot(df, aes(x = OCR_module, y = Accuracy, fill = LLM_model)) +
  geom_boxplot() +
  theme_bw() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Distribution of Accuracy Scores by OCR Module and LLM Model",
       x = "OCR Module", y = "Accuracy Score", fill = "LLM Model")

plot_df <- df %>%
  group_by(OCR_module, LLM_model) %>%
  summarise(Avg_F1_Score = mean(F1_Score, na.rm = TRUE), .groups = "drop")

ggplot(plot_df, aes(x = OCR_module, y = LLM_model, fill = Avg_F1_Score)) +
  geom_tile() +
  scale_fill_viridis_c() +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1)) +
  labs(title = "Average F1 Scores by OCR Module and LLM Model",
       x = "OCR Module", y = "LLM Model", fill = "Avg F1 Score")

ggplot(df, aes(x = F1_Score, fill = LLM_model)) +
  geom_density(alpha = 0.7) +
  facet_wrap(~ OCR_module) +
  theme_minimal() +
  labs(title = "Distribution of F1 Scores by OCR Module and LLM Model",
       x = "F1 Score", y = "Density", fill = "LLM Model")

####################ANOVA###################
#### Quality
anova_result <- aov(F1_Score ~ image_quality, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # medium quality leads to slightly better F1 scores (in general)

# Isolating TesseractOCR as not CNRR
cnn <- c("PaddleOCR", "KerasOCR", "docTR")
resnet <- c("EasyOCR")
lstm <- c("TesseractOCR")

test <- df %>%
  filter(OCR_module %in% lstm)
anova_result <- aov(F1_Score ~ image_quality, data = test)
summary(anova_result)
TukeyHSD(anova_result)

#### Source
anova_result <- aov(F1_Score ~ OCR_module, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # scan < foto < digital (probably because how models were trained)

test <- df %>%
  filter(LLM_model %in% c("Mistral"))
anova_result <- aov(F1_Score ~ LLM_model, data = test)
summary(anova_result)
TukeyHSD(anova_result)


# Isolating TesseractOCR as not CNRR
cnn <- c("PaddleOCR", "KerasOCR", "docTR")
resnet <- c("EasyOCR")
lstm <- c("TesseractOCR")

test <- df %>%
  filter(OCR_module %in% cnn)
anova_result <- aov(F1_Score ~ rotation, data = test)
summary(anova_result)
TukeyHSD(anova_result)

#### Color
anova_result <- aov(F1_Score ~ color_mode, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # color < b/w

# Isolating TesseractOCR as not CNRR
print(TukeyHSD(aov(F1_Score ~ color_mode, data = test))) 
print(TukeyHSD(aov(F1_Score ~ color_mode, data = test2))) 
# No main difference.

#### Content
anova_result <- aov(Time ~ Noise_Removal, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # Tabular > Number; Text > Number; Text (no numbers) > Number
# So number recognition still not good. Organized data (tabular) without text is preferred.

cnn <- c("PaddleOCR", "KerasOCR", "docTR")
resnet <- c("EasyOCR")
lstm <- c("TesseractOCR")

test <- df %>%
  filter(OCR_module %in% cnn)
anova_result <- aov(F1_Score ~ rotation, data = test)
summary(anova_result)
TukeyHSD(anova_result)


# Isolating TesseractOCR as not CNRR
print(TukeyHSD(aov(F1_Score ~ content_type, data = test))) 
print(TukeyHSD(aov(F1_Score ~ content_type, data = test2))) 
# In CNN: Text < Tabular, Text (no number) < Tabular. Tabular is preferred: overfitting!

#### Language
anova_result <- aov(F1_Score ~ language, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # SPA of course worse than ENG

# Isolating TesseractOCR as not CNRR
print(TukeyHSD(aov(F1_Score ~ language, data = test))) 
print(TukeyHSD(aov(F1_Score ~ language, data = test2))) 
# In CNN: better in SPA

#### Rotation
unique(df$rotation_angle) <- as.factor(df$rotation_angle)
anova_result <- aov(F1_Score ~ rotation_angle, data = df)
summary(anova_result)
tukey_result <- TukeyHSD(anova_result)
print(tukey_result) # Rotation always does worse than 0 rotation. 
# However, bigger rotations do better than smaller ones.
# TODO: Check examples and comment on it.

# Isolating TesseractOCR as not CNRR
print(TukeyHSD(aov(F1_Score ~ rotation_angle, data = test))) 
print(TukeyHSD(aov(F1_Score ~ rotation_angle, data = test2))) 
# CNN manages rotations better than LSTM

####################Regression models###################
## Experiments characteristics
df$image_quality <- as.factor(df$image_quality)
df$image_source <- as.factor(df$image_source)
df$content_type <- as.factor(df$content_type)
df$rotation_angle <- as.factor(df$rotation_angle)
colnames(df)
# Fit a linear model with F1 (Metric4) as the dependent variable
lm_model <- lm(F1_Score ~  image_quality + image_source + content_type + rotation_angle, data = df)
summary(lm_model)
#levels(df$image_quality)
#df$image_quality <- relevel(df$image_quality, ref = "medium")

## OCR and Models
df$OCR_module <- as.factor(df$OCR_module)
df$LLM_model <- as.factor(df$LLM_model)
df$Config <- as.factor(df$Config)
lm_model <- lm(F1_Score ~  OCR_module + LLM_model + image_quality + content_type + rotation + Binarization + Skew_Correction + Noise_Removal + Time, data = df) # Best is Tesseract + Mistral
# PaddleOCR cannot be included in analysis
summary(lm_model)
df$LLM_model <- relevel(df$LLM_model, ref = "Gemma2-9B")
df$OCR_module <- relevel(df$OCR_module, ref = "TesseractOCR")
df$Config <- relevel(df$Config, ref = "120")

df$OCR_module <- relevel(df$OCR_module, ref = "TesseractOCR")
levels(filtered_df$OCR_module)

filtered_df <- df %>%
  filter(
    OCR_module %in% c("PaddleOCR", "docTR", "TesseractOCR"),
    LLM_model %in% c("Gemma2", "Mistral"),
    Binarization %in% c(" None", " adaptive_mean", " adaptive_gaussian", "otsu"),
    Skew_Correction %in% c(" None", " hough_transform"),
    Noise_Removal %in% c(" None", " gaussian_filter", " frequency_filter", " mean_filter"),
    )

lm_model <- lm(F1_Score ~ OCR_module + LLM_model + image_quality + content_type + rotation + Binarization + Skew_Correction + Noise_Removal, data = filtered_df)
summary(lm_model)
# Regression shows that Paddle&Tesseract (without Config) have biggest influence, also Mistral
# How do we explain difference top10 and this info? See Boxplot.
# However, Boxplot shows that errors can be much aggravated, while Phi3 is not the case
# In our use case, maybe that combination is better

# Even sou, Tesseract+Gemma2 best combination

# With Config, Mistral is alternative. Which Config would also be alternative?
# However, not so significant.
# In our case: if data is not understood, in next try, we can change to Mistral+Tesseract+24
# Next: Phi3 + Tesseract + 70

####################Random forest###################
# Check non-linear relationship and most important factors
