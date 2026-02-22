# =========================================================
# FULL PIPELINE (ONE BLOCK) - FAST + STRONG + REPORT READY
# Dataset: Acoustic Features.csv
# Task: 4-class classification (Happy/Sad/Angry/Relax)
#
# Evaluation:
# - Holdout (80/20 stratified)  [optional for report]
# - Three-way split (60/20/20 stratified) [main]
# - 5-fold CV (full data) [stability]
#
# Feature Selection:
# - LASSO (multinomial glmnet) -> selected features list + top-20 plot
#
# Outputs saved to OUTDIR:
# - Figures: correlation matrix, LASSO top-20, RF importance, (XGB importance if OK)
# - Tables: model comparison tables, missing values table
# - Models: finalized workflows + best fitted models (.rds)
# - Confusion matrices + predictions (csv)
# =========================================================

library(tidymodels)
library(readr)
library(dplyr)
library(ggplot2)
library(vip)
library(tibble)
library(tidyr)
library(glmnet)

set.seed(123)

# ---------- 1) Output directory ----------
OUTDIR <- "artifacts_report"
dir.create(OUTDIR, showWarnings = FALSE)
cat("OUTDIR:", normalizePath(OUTDIR), "\n")

# ---------- 2) Load Data ----------
DATA_PATH <- "Acoustic Features.csv"
data <- read_csv(DATA_PATH, show_col_types = FALSE) %>%
  mutate(Class = as.factor(Class))

cat("\nDATA SHAPE:", nrow(data), "x", ncol(data), "\n")
cat("\nCLASS DISTRIBUTION:\n")
print(table(data$Class))

# ---------- 3) Missing value table ----------
na_counts <- sapply(data, function(x) sum(is.na(x)))
write_csv(
  tibble(column = names(na_counts), na_count = as.integer(na_counts)) %>% arrange(desc(na_count)),
  file.path(OUTDIR, "TABLE_missing_values.csv")
)

# =========================================================
# FIGURE 1: Correlation Heatmap (predictors only)
# =========================================================
X <- data %>% select(-Class)
cor_mat <- suppressWarnings(cor(X, use = "pairwise.complete.obs"))

cor_df <- as.data.frame(as.table(cor_mat))
colnames(cor_df) <- c("Var1", "Var2", "Correlation")

p_cor <- ggplot(cor_df, aes(Var1, Var2, fill = Correlation)) +
  geom_tile() +
  theme_minimal(base_size = 10) +
  theme(
    axis.text.x = element_text(angle = 90, vjust = 0.5, hjust = 1),
    axis.title = element_blank()
  ) +
  labs(title = "Correlation Matrix (Acoustic Features)")

ggsave(
  filename = file.path(OUTDIR, "FIG_correlation_matrix.png"),
  plot = p_cor, width = 10, height = 8, dpi = 200
)

# ---------- 4) Preprocessing Recipe----------
make_recipe <- function(train_df){
  recipe(Class ~ ., data = train_df) %>%
    step_nzv(all_predictors()) %>%
    step_impute_median(all_numeric_predictors()) %>%
    step_normalize(all_numeric_predictors())
}

# ---------- 5) Metrics (macro reporting helper) ----------
calc_metrics <- function(pred_df){
  tibble(
    accuracy  = accuracy(pred_df, truth = Class, estimate = .pred_class)$.estimate,
    precision = precision(pred_df, truth = Class, estimate = .pred_class, estimator="macro")$.estimate,
    recall    = recall(pred_df, truth = Class, estimate = .pred_class, estimator="macro")$.estimate,
    f1_macro  = f_meas(pred_df, truth = Class, estimate = .pred_class, estimator="macro")$.estimate
  )
}

# ---------- 6) Models (>=5, fast + strong) ----------
# (1) Elastic Net Multinomial Logistic Regression
m_log <- multinom_reg(penalty = tune(), mixture = tune()) %>%
  set_engine("glmnet") %>% set_mode("classification")

# (2) Linear SVM
m_svm <- svm_linear(cost = tune()) %>%
  set_engine("LiblineaR") %>% set_mode("classification")

# (3) Random Forest
m_rf <- rand_forest(
  trees = tune(),
  mtry = tune(),
  min_n = tune()
) %>%
  set_engine("ranger", importance = "impurity", num.threads = 1) %>%
  set_mode("classification")

# (4) LDA
m_lda <- discrim_linear() %>%
  set_engine("MASS") %>% set_mode("classification")

# (5) XGBoost (stabilized: trees fixed)
m_xgb <- boost_tree(
  trees = 300,               # fixed to avoid 401 vs 400 bug
  tree_depth = tune(),
  learn_rate = tune(),
  min_n = tune()
) %>%
  set_engine("xgboost", verbosity = 0, nthread = 1) %>%
  set_mode("classification")

wf_of <- function(rec, model) workflow() %>% add_recipe(rec) %>% add_model(model)

# ---------- 7) Small Grids (FAST tuning) ----------
grid_log <- tidyr::crossing(
  penalty = 10^seq(-4, 0, length.out = 5),
  mixture = c(0, 0.5, 1)
)
grid_svm <- tibble(cost = 2^seq(-3, 3, by = 1))
grid_rf  <- tidyr::crossing(
  trees = c(300),
  mtry  = c(10, 20),
  min_n = c(5, 10)
)
# XGB grid (trees fixed)
grid_xgb <- tidyr::crossing(
  tree_depth = c(3, 6),
  learn_rate = c(0.05, 0.1),
  min_n      = c(5, 10)
)

metrics_set <- metric_set(accuracy, precision, recall, f_meas)
ctrl_grid   <- control_grid(save_pred = TRUE, verbose = FALSE, allow_par = FALSE)
ctrl_resamp <- control_resamples(save_pred = TRUE, verbose = FALSE)

# ---------- 8) Helpers ----------
tune_and_finalize <- function(wf, folds, grid, metric_name="f_meas"){
  res <- tune_grid(
    wf,
    resamples = folds,
    grid = grid,
    metrics = metrics_set,
    control = ctrl_grid
  )
  best <- select_best(res, metric = metric_name)
  list(
    finalized = finalize_workflow(wf, best),
    best_params = best,
    tuning_results = res
  )
}

eval_fit_predict <- function(wf_final, train_df, test_df){
  fit_obj <- fit(wf_final, data = train_df)
  pred <- predict(fit_obj, test_df) %>% bind_cols(test_df %>% select(Class))
  list(
    fit = fit_obj,
    pred = pred,
    metrics = calc_metrics(pred),
    cm = conf_mat(pred, truth = Class, estimate = .pred_class)
  )
}

save_confusion_csv <- function(cm_obj, filename){
  cm_tbl <- as_tibble(cm_obj$table)
  write_csv(cm_tbl, filename)
}

# =========================================================
# MAIN SPLIT: THREE-WAY (60/20/20 stratified)  
# =========================================================
cat("\n================ THREE-WAY (60/20/20) ================\n")

split1 <- initial_split(data, prop = 0.60, strata = Class)
train_t <- training(split1)
temp_t  <- testing(split1)

split2 <- initial_split(temp_t, prop = 0.50, strata = Class)
val_t  <- training(split2)
test_t <- testing(split2)

write_csv(
  tibble(split="ThreeWay_60_20_20",
         train_n=nrow(train_t), val_n=nrow(val_t), test_n=nrow(test_t)),
  file.path(OUTDIR, "INFO_splits_threeway.csv")
)

# =========================================================
# FEATURE SELECTION (LASSO) on TRAIN ONLY (no leakage)
# - Outputs:
#   - FEATURE_SELECTION_LASSO_selected_features.csv
#   - FIG_feature_selection_lasso_top20.png
# =========================================================
cat("\n================ FEATURE SELECTION (LASSO) ================\n")

rec_fs  <- make_recipe(train_t)
prep_fs <- prep(rec_fs, training = train_t, retain = TRUE)
train_fs <- bake(prep_fs, new_data = train_t)

X_mat <- train_fs %>% select(-Class) %>% as.matrix()
y_vec <- train_fs$Class

set.seed(123)
cvfit <- cv.glmnet(
  x = X_mat,
  y = y_vec,
  family = "multinomial",
  alpha = 1,                 # LASSO
  nfolds = 5,
  type.multinomial = "grouped"
)

best_lambda <- cvfit$lambda.min
cat("Best lambda (LASSO):", best_lambda, "\n")

coef_list <- coef(cvfit, s = "lambda.min")

selected <- unique(unlist(lapply(coef_list, function(m){
  rn <- rownames(m)
  nz <- which(as.numeric(m) != 0)
  rn[nz]
})))
selected <- setdiff(selected, "(Intercept)")

cat("Selected features count:", length(selected), "\n")
write_csv(
  tibble(selected_feature = selected),
  file.path(OUTDIR, "FEATURE_SELECTION_LASSO_selected_features.csv")
)

# Top-20 plot by mean |coef| across classes
coef_df <- bind_rows(lapply(names(coef_list), function(cls){
  m <- coef_list[[cls]]
  tibble(feature = rownames(m), coef = as.numeric(m), class = cls)
})) %>%
  filter(feature != "(Intercept)") %>%
  group_by(feature) %>%
  summarise(score = mean(abs(coef)), .groups="drop") %>%
  arrange(desc(score)) %>%
  slice(1:min(20, n()))

p_fs <- ggplot(coef_df, aes(x = reorder(feature, score), y = score)) +
  geom_col() +
  coord_flip() +
  theme_minimal() +
  labs(title = "Feature Selection (LASSO): Top-20 by mean |coefficient|",
       x = "Feature", y = "Mean |Coefficient| across classes")

ggsave(
  filename = file.path(OUTDIR, "FIG_feature_selection_lasso_top20.png"),
  plot = p_fs, width = 9, height = 6, dpi = 200
)

# =========================================================
# MODELING (Train) + CV Tuning (Train only) + VAL selection
# =========================================================
cat("\n================ MODELING + TUNING (TRAIN CV) ================\n")

rec_t <- make_recipe(train_t)
folds_t <- vfold_cv(train_t, v = 5, strata = Class)

wf_log_t <- wf_of(rec_t, m_log)
wf_svm_t <- wf_of(rec_t, m_svm)
wf_rf_t  <- wf_of(rec_t, m_rf)
wf_lda_t <- wf_of(rec_t, m_lda)
wf_xgb_t <- wf_of(rec_t, m_xgb)

# Tune & finalize
tuned_log_t <- tune_and_finalize(wf_log_t, folds_t, grid_log)
tuned_svm_t <- tune_and_finalize(wf_svm_t, folds_t, grid_svm)
tuned_rf_t  <- tune_and_finalize(wf_rf_t,  folds_t, grid_rf)

final_log_t <- tuned_log_t$finalized
final_svm_t <- tuned_svm_t$finalized
final_rf_t  <- tuned_rf_t$finalized
final_lda_t <- wf_lda_t

# XGBoost may fail on some systems -> keep pipeline alive
final_xgb_t <- NULL
tuned_xgb_t <- NULL
xgb_ok <- TRUE
tryCatch({
  tuned_xgb_t <- tune_and_finalize(wf_xgb_t, folds_t, grid_xgb)
  final_xgb_t <- tuned_xgb_t$finalized
}, error = function(e){
  xgb_ok <<- FALSE
  cat("\n[XGBOOST DISABLED] Error during tuning:\n")
  message(e)
})

# Save finalized workflows (three-way)
saveRDS(final_log_t, file.path(OUTDIR, "wf_threeway_elasticnet_logreg_finalized.rds"))
saveRDS(final_svm_t, file.path(OUTDIR, "wf_threeway_linear_svm_finalized.rds"))
saveRDS(final_rf_t,  file.path(OUTDIR, "wf_threeway_randomforest_finalized.rds"))
saveRDS(final_lda_t, file.path(OUTDIR, "wf_threeway_lda_finalized.rds"))

write_csv(tuned_log_t$best_params, file.path(OUTDIR, "BESTPARAM_threeway_logreg.csv"))
write_csv(tuned_svm_t$best_params, file.path(OUTDIR, "BESTPARAM_threeway_svm.csv"))
write_csv(tuned_rf_t$best_params,  file.path(OUTDIR, "BESTPARAM_threeway_rf.csv"))

if(xgb_ok){
  saveRDS(final_xgb_t, file.path(OUTDIR, "wf_threeway_xgboost_finalized.rds"))
  write_csv(tuned_xgb_t$best_params, file.path(OUTDIR, "BESTPARAM_threeway_xgb.csv"))
}

# ---- Validation evaluation for model selection
eval_on_val <- function(wf_final){
  fit_obj <- fit(wf_final, data = train_t)
  pred <- predict(fit_obj, val_t) %>% bind_cols(val_t %>% select(Class))
  calc_metrics(pred)
}

val_tab <- bind_rows(
  eval_on_val(final_log_t) %>% mutate(model="ElasticNet_LogReg", eval="ThreeWay_VAL"),
  eval_on_val(final_svm_t) %>% mutate(model="Linear_SVM",        eval="ThreeWay_VAL"),
  eval_on_val(final_rf_t)  %>% mutate(model="RandomForest",      eval="ThreeWay_VAL"),
  eval_on_val(final_lda_t) %>% mutate(model="LDA",               eval="ThreeWay_VAL")
)

if(xgb_ok){
  val_tab <- bind_rows(
    val_tab,
    eval_on_val(final_xgb_t) %>% mutate(model="XGBoost", eval="ThreeWay_VAL")
  )
}

val_tab <- val_tab %>% arrange(desc(f1_macro))
print(val_tab)
write_csv(val_tab, file.path(OUTDIR, "TABLE_threeway_validation_model_select.csv"))

best_three_model <- val_tab$model[1]
cat("\nBEST MODEL (by VAL macro-F1):", best_three_model, "\n")

final_best_three <- switch(best_three_model,
                           "ElasticNet_LogReg" = final_log_t,
                           "Linear_SVM"        = final_svm_t,
                           "RandomForest"      = final_rf_t,
                           "LDA"               = final_lda_t,
                           "XGBoost"           = final_xgb_t
)

# ---- Retrain on TRAIN+VAL, evaluate on TEST
trainval_t <- bind_rows(train_t, val_t)
out_three_test <- eval_fit_predict(final_best_three, trainval_t, test_t)

tab_three_test <- out_three_test$metrics %>%
  mutate(model = best_three_model, eval="ThreeWay_TEST")

print(tab_three_test)
write_csv(tab_three_test, file.path(OUTDIR, "TABLE_threeway_test_bestmodel.csv"))

cat("\nThree-way Confusion Matrix (BEST):\n")
print(out_three_test$cm)

# Save best model + confusion + predictions
saveRDS(final_best_three, file.path(OUTDIR, paste0("wf_threeway_best_finalized_", best_three_model, ".rds")))
saveRDS(out_three_test$fit, file.path(OUTDIR, paste0("BEST_THREEWAY_fit_", best_three_model, ".rds")))
save_confusion_csv(out_three_test$cm, file.path(OUTDIR, paste0("BEST_THREEWAY_confusion_", best_three_model, ".csv")))
write_csv(out_three_test$pred, file.path(OUTDIR, paste0("BEST_THREEWAY_predictions_", best_three_model, ".csv")))

# =========================================================
# HOLDOUT (80/20)  <-- 
# =========================================================
cat("\n================ HOLDOUT (80/20) ================\n")

split_hold <- initial_split(data, prop = 0.80, strata = Class)
train_h <- training(split_hold)
test_h  <- testing(split_hold)

write_csv(
  tibble(split="Holdout_80_20", train_n=nrow(train_h), test_n=nrow(test_h)),
  file.path(OUTDIR, "INFO_splits_holdout.csv")
)

rec_h <- make_recipe(train_h)
folds_h <- vfold_cv(train_h, v = 5, strata = Class)

wf_log_h <- wf_of(rec_h, m_log)
wf_svm_h <- wf_of(rec_h, m_svm)
wf_rf_h  <- wf_of(rec_h, m_rf)
wf_lda_h <- wf_of(rec_h, m_lda)
wf_xgb_h <- wf_of(rec_h, m_xgb)

tuned_log_h <- tune_and_finalize(wf_log_h, folds_h, grid_log)
tuned_svm_h <- tune_and_finalize(wf_svm_h, folds_h, grid_svm)
tuned_rf_h  <- tune_and_finalize(wf_rf_h,  folds_h, grid_rf)

final_log_h <- tuned_log_h$finalized
final_svm_h <- tuned_svm_h$finalized
final_rf_h  <- tuned_rf_h$finalized
final_lda_h <- wf_lda_h

final_xgb_h <- NULL
tuned_xgb_h <- NULL
xgb_ok_h <- TRUE
tryCatch({
  tuned_xgb_h <- tune_and_finalize(wf_xgb_h, folds_h, grid_xgb)
  final_xgb_h <- tuned_xgb_h$finalized
}, error = function(e){
  xgb_ok_h <<- FALSE
  cat("\n[XGBOOST DISABLED - HOLDOUT] Error during tuning:\n")
  message(e)
})

# Save finalized workflows (holdout)
saveRDS(final_log_h, file.path(OUTDIR, "wf_holdout_elasticnet_logreg_finalized.rds"))
saveRDS(final_svm_h, file.path(OUTDIR, "wf_holdout_linear_svm_finalized.rds"))
saveRDS(final_rf_h,  file.path(OUTDIR, "wf_holdout_randomforest_finalized.rds"))
saveRDS(final_lda_h, file.path(OUTDIR, "wf_holdout_lda_finalized.rds"))
write_csv(tuned_log_h$best_params, file.path(OUTDIR, "BESTPARAM_holdout_logreg.csv"))
write_csv(tuned_svm_h$best_params, file.path(OUTDIR, "BESTPARAM_holdout_svm.csv"))
write_csv(tuned_rf_h$best_params,  file.path(OUTDIR, "BESTPARAM_holdout_rf.csv"))

if(xgb_ok_h){
  saveRDS(final_xgb_h, file.path(OUTDIR, "wf_holdout_xgboost_finalized.rds"))
  write_csv(tuned_xgb_h$best_params, file.path(OUTDIR, "BESTPARAM_holdout_xgb.csv"))
}

# Evaluate on holdout test
out_log_h <- eval_fit_predict(final_log_h, train_h, test_h)
out_svm_h <- eval_fit_predict(final_svm_h, train_h, test_h)
out_rf_h  <- eval_fit_predict(final_rf_h,  train_h, test_h)
out_lda_h <- eval_fit_predict(final_lda_h, train_h, test_h)

tab_hold <- bind_rows(
  out_log_h$metrics %>% mutate(model="ElasticNet_LogReg", eval="Holdout_80_20"),
  out_svm_h$metrics %>% mutate(model="Linear_SVM",        eval="Holdout_80_20"),
  out_rf_h$metrics  %>% mutate(model="RandomForest",      eval="Holdout_80_20"),
  out_lda_h$metrics %>% mutate(model="LDA",               eval="Holdout_80_20")
)

if(xgb_ok_h){
  out_xgb_h <- eval_fit_predict(final_xgb_h, train_h, test_h)
  tab_hold <- bind_rows(
    tab_hold,
    out_xgb_h$metrics %>% mutate(model="XGBoost", eval="Holdout_80_20")
  )
}

tab_hold <- tab_hold %>% arrange(desc(f1_macro))
print(tab_hold)
write_csv(tab_hold, file.path(OUTDIR, "TABLE_holdout_model_comparison.csv"))

best_hold_model <- tab_hold$model[1]
cat("\nBEST HOLDOUT MODEL:", best_hold_model, "\n")

best_out_hold <- switch(best_hold_model,
                        "ElasticNet_LogReg" = out_log_h,
                        "Linear_SVM"        = out_svm_h,
                        "RandomForest"      = out_rf_h,
                        "LDA"               = out_lda_h,
                        "XGBoost"           = if(xgb_ok_h) out_xgb_h else out_rf_h
)

saveRDS(best_out_hold$fit, file.path(OUTDIR, paste0("BEST_HOLDOUT_fit_", best_hold_model, ".rds")))
save_confusion_csv(best_out_hold$cm, file.path(OUTDIR, paste0("BEST_HOLDOUT_confusion_", best_hold_model, ".csv")))
write_csv(best_out_hold$pred, file.path(OUTDIR, paste0("BEST_HOLDOUT_predictions_", best_hold_model, ".csv")))

# =========================================================
# CV 5-fold (FULL DATA)  <-- stability check
# =========================================================
cat("\n================ 5-FOLD CV (FULL DATA) ================\n")

folds_full <- vfold_cv(data, v = 5, strata = Class)
rec_full <- make_recipe(data)

wf_log_full <- wf_of(rec_full, m_log)
wf_svm_full <- wf_of(rec_full, m_svm)
wf_rf_full  <- wf_of(rec_full, m_rf)
wf_lda_full <- wf_of(rec_full, m_lda)
wf_xgb_full <- wf_of(rec_full, m_xgb)

tuned_log_full <- tune_and_finalize(wf_log_full, folds_full, grid_log)
tuned_svm_full <- tune_and_finalize(wf_svm_full, folds_full, grid_svm)
tuned_rf_full  <- tune_and_finalize(wf_rf_full,  folds_full, grid_rf)

final_log_full <- tuned_log_full$finalized
final_svm_full <- tuned_svm_full$finalized
final_rf_full  <- tuned_rf_full$finalized
final_lda_full <- wf_lda_full

final_xgb_full <- NULL
tuned_xgb_full <- NULL
xgb_ok_full <- TRUE
tryCatch({
  tuned_xgb_full <- tune_and_finalize(wf_xgb_full, folds_full, grid_xgb)
  final_xgb_full <- tuned_xgb_full$finalized
}, error = function(e){
  xgb_ok_full <<- FALSE
  cat("\n[XGBOOST DISABLED - CV FULL] Error during tuning:\n")
  message(e)
})

saveRDS(final_log_full, file.path(OUTDIR, "wf_cv_elasticnet_logreg_finalized.rds"))
saveRDS(final_svm_full, file.path(OUTDIR, "wf_cv_linear_svm_finalized.rds"))
saveRDS(final_rf_full,  file.path(OUTDIR, "wf_cv_randomforest_finalized.rds"))
saveRDS(final_lda_full, file.path(OUTDIR, "wf_cv_lda_finalized.rds"))

fit_cv_and_summarize <- function(wf_final, folds){
  res <- fit_resamples(
    wf_final,
    resamples = folds,
    metrics = metrics_set,
    control = ctrl_resamp
  )
  collect_metrics(res) %>%
    select(.metric, mean) %>%
    pivot_wider(names_from = .metric, values_from = mean)
}

cv_tab <- bind_rows(
  fit_cv_and_summarize(final_log_full, folds_full) %>% mutate(model="ElasticNet_LogReg", eval="CV_5fold"),
  fit_cv_and_summarize(final_svm_full, folds_full) %>% mutate(model="Linear_SVM",        eval="CV_5fold"),
  fit_cv_and_summarize(final_rf_full,  folds_full) %>% mutate(model="RandomForest",      eval="CV_5fold"),
  fit_cv_and_summarize(final_lda_full, folds_full) %>% mutate(model="LDA",               eval="CV_5fold")
)

if(xgb_ok_full){
  saveRDS(final_xgb_full, file.path(OUTDIR, "wf_cv_xgboost_finalized.rds"))
  cv_tab <- bind_rows(
    cv_tab,
    fit_cv_and_summarize(final_xgb_full, folds_full) %>% mutate(model="XGBoost", eval="CV_5fold")
  )
}

print(cv_tab)
write_csv(cv_tab, file.path(OUTDIR, "TABLE_cv5fold_model_comparison.csv"))

# =========================================================
# FINAL: Combine All Tables
# =========================================================
all_tables <- bind_rows(
  tab_hold,
  tab_three_test,
  cv_tab
)

write_csv(all_tables, file.path(OUTDIR, "TABLE_model_comparison_all_evals.csv"))
cat("\nSaved: TABLE_model_comparison_all_evals.csv\n")

# =========================================================
# FEATURE IMPORTANCE FIGURES (RESULTS SUPPORT)
# - RF importance always
# - XGB importance if available and xgboost installed OK
# =========================================================
cat("\n================ FEATURE IMPORTANCE (RF / XGB) ================\n")

# Random Forest importance (from holdout best RF fit object out_rf_h)
rf_fit <- extract_fit_parsnip(out_rf_h$fit)$fit
png(file.path(OUTDIR, "FIG_rf_importance_top20.png"), width=1000, height=700)
print(vip::vip(rf_fit, num_features = 20) + ggtitle("Random Forest Feature Importance (Top 20)"))
dev.off()

# XGB importance if holdout xgb succeeded
if(exists("out_xgb_h") && xgb_ok_h){
  xgb_fit <- extract_fit_parsnip(out_xgb_h$fit)$fit
  imp_xgb <- xgboost::xgb.importance(model = xgb_fit)
  png(file.path(OUTDIR, "FIG_xgb_importance_top20.png"), width=1000, height=700)
  xgboost::xgb.plot.importance(
    imp_xgb[1:min(20, nrow(imp_xgb)), ],
    rel_to_first = TRUE,
    xlab = "Relative Importance"
  )
  dev.off()
  cat("Saved: FIG_xgb_importance_top20.png\n")
} else {
  cat("XGBoost importance skipped (xgb not available or failed).\n")
}

cat("\nDONE. Check folder:", normalizePath(OUTDIR), "\n")
cat("Key outputs:\n",
    "- FIG_correlation_matrix.png\n",
    "- FIG_feature_selection_lasso_top20.png\n",
    "- FEATURE_SELECTION_LASSO_selected_features.csv\n",
    "- FIG_rf_importance_top20.png\n",
    "- TABLE_model_comparison_all_evals.csv\n")