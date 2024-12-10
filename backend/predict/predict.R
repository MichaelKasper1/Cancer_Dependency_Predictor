cat('Predict.R started...\n')


args <- commandArgs(trailingOnly = TRUE)

# Check for correct number of arguments
if (length(args) < 2) {
    stop("Usage: Rscript predict.R '<input_data_json>' '<models_dir>'")
}

# Parse arguments
input_data_json <- args[1]
models_dir <- args[2]

# Load necessary libraries
library(glmnet)
library(jsonlite)

# Parse JSON input
input_data <- fromJSON(input_data_json)

# Convert the JSON data to a matrix for predictions
df <- as.matrix(as.data.frame(input_data, row.names = 1))

# Load models
model_files <- list.files(models_dir, pattern = "_model.rds", full.names = TRUE)
models <- lapply(model_files, readRDS)

# Predict using the trained models
cat("Predicting using elastic net models...\n")
start_time <- Sys.time()
predictions <- lapply(models, function(model) {
  predict(model, newx = t(df), s = "lambda.min")
})
end_time <- Sys.time()

cat("Time taken for prediction:\n")
print(end_time - start_time)

# Combine predictions into a data frame
predictions_df <- do.call(cbind, predictions)
colnames(predictions_df) <- gsub("_model.rds", "", basename(model_files))
rownames(predictions_df) <- colnames(df)

# Convert predictions to JSON and print to stdout
cat("Converting predictions to JSON...\n")
predictions_json <- toJSON(as.data.frame(predictions_df), pretty = TRUE)
cat(predictions_json)