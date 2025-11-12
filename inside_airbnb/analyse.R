# analyze_districts.R
# Run this script from the parent folder that contains the date folders (e.g. 2024-12-04/)

library(tidyverse)

# 1. Find all 'listings.csv' files in subfolders
csv_files <- list.files(path = ".", pattern = "listings\\.csv$", recursive = TRUE, full.names = TRUE)

# 2. Function to read a CSV and attach its date (from folder name)
read_with_date <- function(file) {
  folder_name <- basename(dirname(file))
  date <- as.Date(folder_name, format = "%Y-%m-%d")
  
  df <- read_csv(file, show_col_types = FALSE)
  df$date <- date
  return(df)
}

# 3. Combine all CSVs into one dataframe
all_data <- map_dfr(csv_files, read_with_date)

cat("Loaded", nrow(all_data), "rows from", length(csv_files), "files.\n")

# 4. Summarize: number of listings over time by district
district_summary <- all_data %>%
  group_by(date, neighbourhood) %>%
  summarise(num_listings = n(), .groups = "drop") %>%
  arrange(date, neighbourhood)

selected_districts <- c("I. kerület", "II. kerület", "V. kerület", "VI. kerület", 
                        "VII. kerület", "VIII. kerület", "IX. kerület", "XI. kerület", "XIII. kerület")

district_summary_filtered <- district_summary %>%
  filter(neighbourhood %in% selected_districts) %>%
  group_by(neighbourhood) %>%
  arrange(date) %>%
  mutate(
    num_listings_norm = 100 * num_listings / first(num_listings)
  ) %>%
  ungroup()

# Set colors: VI red, others pale
colors <- c(
  "I. kerület" = "#cccccc",
  "II. kerület" = "#bbbbbb",
  "V. kerület" = "#aaaaaa",
  "VI. kerület" = "red",
  "VII. kerület" = "#dddddd",
  "VIII. kerület" = "#eeeeee",
  "IX. kerület" = "#bbbbbb",
  "XI. kerület" = "#cccccc",
  "XIII. kerület" = "#dddddd"
)

# Plot
ggplot(district_summary_filtered, aes(x = date, y = num_listings, color = neighbourhood)) +
  geom_line(size = 1.1) +
  scale_color_manual(values = colors) +
  labs(
    title = "Change in Number of Listings Over Time by District (Budapest)",
    x = "Date",
    y = "Listings",
    color = "District"
  ) +
  theme_minimal() +
  theme(legend.position = "right") +
  scale_x_date(date_breaks = "1 month", date_labels = "%b %Y")
