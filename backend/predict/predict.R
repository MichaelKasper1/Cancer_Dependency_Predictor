# Load necessary libraries
library(glmnet)

# Read the input data
expr_scaled <- read.csv("predict/input.csv", row.names = 1)
# make the gene column into the rownames and delete gene column
rownames(expr_scaled) <- expr_scaled$gene
expr_scaled <- expr_scaled[, -1]

# Define models (this should be pre-loaded or created in your R environment)
# For demonstration purposes, we assume a dummy model is available
model_dir <- "predict/models"
model_files <- list.files(model_dir, full.names = TRUE)
models <- lapply(model_files, readRDS)


# Define the prediction function
predict_models <- function(models, expr_scaled) {
  predictions <- lapply(models, function(model) {
    predict(model, newx = t(as.matrix(expr_scaled)), s = "lambda.min")
  })
  predictions_df <- do.call(cbind, predictions)
  colnames(predictions_df) <- gsub("_model.rds", "", basename(model_files))
  rownames(predictions_df) <- colnames(expr_scaled)
  return(predictions_df)
}

# Make predictions
predictions_df <- predict_models(models, expr_scaled)

# Write the predictions to a CSV file
write.csv(predictions_df, file = "predict/predictions.csv", row.names = TRUE)

#####################

# this script is a big bottleneck in the pipeline. For the example data:
# 18 seconds to load the models
# 34 seconds to make predictions