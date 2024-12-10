### Background

The DeepDEP model is trained in the same way as from the original paper. Code for how to use and train DeepDEP models can be found here: https://codeocean.com/capsule/7914207/tree/v1

Elastic net models were also trained in the same way that the authors published, but since not all of the code for training all of the models was released, a few of the lines of the model training were reverse engineered, then the prediction and performance of the models were compared to ensure that methods seemed to be the same. Only the papers cv validated model list was attempted to be trained, and newly trained models that did not pass the performance threshold of 0.2 correlation were filtered from the set of models used in the app.

```{r}
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
```

This is a slight variation from the way the models are built in the code published with Shiu et. al's nature cancer paper. Although the authors do create elastic net models that are trained on only DEPMAP data, in their published code, they create, train, and execute EN models with data that is transcriptionally aligned with TCGA. Additionally, there has been some changes in the code above to correctly obtain model prediction accuracy.

Publication: https://www.nature.com/articles/s43018-024-00789-y
Code available: https://github.com/xushiabbvie/TDtool
