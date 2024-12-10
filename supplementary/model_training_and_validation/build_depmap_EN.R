### This script is used to build elastic-net model to predict gene essentiality scores
datapath="./"
setwd(datapath)

## preprocess depmap gene essentiality data available at depmap portal
gene_effect_21Q1 = read.delim("data/Achilles_gene_effect_21Q1.csv",sep=",",header=T) ### gene effect file available at DEPMAP portal
screen_genes = sapply(strsplit(colnames(gene_effect_21Q1),"[..]"),"[[",1)[-1]
screen_cells = gene_effect_21Q1$DepMap_ID

gene_effect_21Q1 = t(as.matrix(gene_effect_21Q1[,-1]))
rownames(gene_effect_21Q1) = screen_genes
colnames(gene_effect_21Q1) = screen_cells

## get the list of models to train
cv_validated_models = read.delim("data/cv_validated_genelist.txt",header = F)$V1 
### available through the Shiu et al. nature cancer paper: https://www.nature.com/articles/s43018-021-00209-4
gene_effect_21Q1 = gene_effect_21Q1[cv_validated_models,]

## preprocess expression data
expression = read.delim("data/CCLE_expression_21Q1.csv",sep=",",header=T) ### available at DEPMAP portal
# make "X" into rownames and delete the X column
rownames(expression) <- expression$X
screen_genes = sapply(strsplit(colnames(expression),"[..]"),"[[",1)[-1]
expression = t(as.matrix(expression[,-1]))
rownames(expression) = screen_genes

# create row medians for imputations to be used in app
row_medians <- apply(expression, 1, median, na.rm = TRUE)
median_scores_df <- data.frame(Gene = rownames(expression), Median = row_medians)
write.csv(median_scores_df, file = "output_data/median_scores_depmap_EN.csv")

## process essentiality and expression data to have same cell lines
common_cells = intersect(colnames(gene_effect_21Q1),colnames(expression))

expression = expression[,common_cells]
CCLE_expr_scaled = t(scale(t(expression)))
gene_effect_21Q1 = t(gene_effect_21Q1[,common_cells])

## impute the missing values by median
median_imp = function(x)
{
  x[is.na(x)] = median(x[!is.na(x)])
  return(x)
}

gene_effect_21Q1_imp = t(apply(gene_effect_21Q1,2,median_imp))
CCLE_expr_scaled = (apply(CCLE_expr_scaled,2,median_imp))


library(parallel)
library(glmnet)

# Elastic Net Model Training with Manual Cross-Validation
# This function trains an elastic net model using manual cross-validation.
# It divides the data into folds, trains the model on the training set, 
# and evaluates it on the test set for each fold. The function returns 
# the final model and the overall predictability.

Elastic_model = function(y, x, nfolds = 10, alpha = 0.5) {
  # Divide data into folds
  folds <- sample(rep(1:nfolds, length.out = length(y))) # Randomly assign folds
  correlations <- numeric(nfolds) # Store correlations for each fold

  # Perform cross-validation
  for (fold in 1:nfolds) {
    test_idx <- which(folds == fold) # Indices for the test set
    train_idx <- setdiff(seq_along(y), test_idx) # Indices for the training set

    # Train the model on the training set
    cvfit_gene <- glmnet(t(x[, train_idx]), y[train_idx], alpha = alpha)
    cvfit <- cv.glmnet(t(x[, train_idx]), y[train_idx], alpha = alpha, nfolds = nfolds)
    best_lambda <- cvfit$lambda.min # Best lambda value from cross-validation

    # Predict on the test set
    pred_score_gene <- predict(cvfit_gene, newx = t(x[, test_idx]), s = best_lambda)
    correlations[fold] <- cor(pred_score_gene, y[test_idx]) # Calculate correlation
  }

  # Calculate overall predictability
  overall_predictability <- mean(correlations, na.rm = TRUE)

  # Train the final model on the entire dataset
  final_model <- cv.glmnet(t(x), y, alpha = alpha, nfolds = nfolds)

  # Return the final model and overall predictability
  res <- list("model" = final_model, "predictability" = overall_predictability)
  return(res)
}

# Convert training data to list for multiprocessing
para_data <- lapply(rownames(gene_effect_21Q1_imp), function(x) gene_effect_21Q1_imp[x, ])
names(para_data) <- rownames(gene_effect_21Q1_imp)

# Train models in parallel
ptm <- proc.time()
elastic_coef_all <- mclapply(
  para_data,
  function(x) Elastic_model(x, CCLE_expr_scaled),
  mc.cores = 50
)
print(proc.time() - ptm)

# Save each model to a file
model_dir <- "output/EN_models_ccle_expression_only"
dir.create(model_dir, showWarnings = FALSE)

lapply(seq_along(elastic_coef_all), function(i) {
  model_name <- paste0(model_dir, names(elastic_coef_all)[i], "_model.rds")
  saveRDS(elastic_coef_all[[i]]$model, file = model_name)
})

# Extract and save model performances
model_performances <- sapply(elastic_coef_all, function(x) x$predictability)
write.csv(model_performances, file = "output/model_performances_ccle_expression_only.csv")