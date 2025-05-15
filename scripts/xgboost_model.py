import pandas as pd
import numpy as np
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv("data/engineered_sessions.csv")

df = df[df["converted"].isin([0, 1])]

# Keep only top countries and sources to reduce dimensionality
top_n = 10
top_countries = df["country"].value_counts().nlargest(top_n).index
top_sources = df["source"].value_counts().nlargest(top_n).index
df["country"] = df["country"].where(df["country"].isin(top_countries), "Other")
df["source"] = df["source"].where(df["source"].isin(top_sources), "Other")

# Define features and target
features = [
    "devicecategory", "source", "country",
    "pageviews", "timeonsite",
    "is_bounce", "session_bin",
    "pageviews_per_minute", "device_source_combo",
    "high_value_region"
]
df_model = df[features + ["converted"]].dropna()

# Prepare column names
categorical_cols = ["devicecategory", "source", "country", "session_bin", "device_source_combo"]
numerical_cols = ["pageviews", "timeonsite", "is_bounce", "pageviews_per_minute", "high_value_region"]

# Preprocessing
preprocessor = ColumnTransformer(transformers=[
    ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols),
    ('num', StandardScaler(), numerical_cols)
])

# Define pipeline
pipeline = Pipeline(steps=[
    ('preprocessor', preprocessor),
    ('model', XGBClassifier(
        eval_metric="logloss",
        n_estimators=100,
        max_depth=4,
        learning_rate=0.1,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42
    ))
])

# Prepare data
X = df_model[categorical_cols + numerical_cols]
y = df_model["converted"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

# Fit the full pipeline
pipeline.fit(X_train, y_train)

# Show top 15 feature importances
import matplotlib.pyplot as plt

importances = pipeline.named_steps['model'].feature_importances_
encoded_cat_names = pipeline.named_steps['preprocessor'].named_transformers_['cat'].get_feature_names_out(categorical_cols)
all_feature_names = np.concatenate([encoded_cat_names, numerical_cols])

importance_df = pd.DataFrame({
    "feature": all_feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

top_features = importance_df.head(15)

plt.figure(figsize=(10, 6))
plt.barh(top_features["feature"][::-1], top_features["importance"][::-1])
plt.xlabel("Feature Importance")
plt.title("Top 15 Feature Importances (XGBoost)")
plt.tight_layout()
plt.grid(axis='x')
plt.show()

# Predict and evaluate
y_pred = pipeline.predict(X_test)
y_proba = pipeline.predict_proba(X_test)[:, 1]

# Print report
print("Classification Report:")
print(classification_report(y_test, y_pred))
try:
    auc = roc_auc_score(y_test, y_proba)
    print(f"AUC Score: {auc:.4f}")
except ValueError as e:
    print("AUC Score could not be computed:", e)

# Threshold tuning
from sklearn.metrics import precision_recall_curve, f1_score

precision, recall, thresholds = precision_recall_curve(y_test, y_proba)
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-10)
best_index = np.argmax(f1_scores)
best_threshold = thresholds[best_index]
best_f1 = f1_scores[best_index]
y_pred_tuned = (y_proba >= best_threshold).astype(int)

print("Threshold-Tuned Classification Report:")
print(classification_report(y_test, y_pred_tuned))
print(f"Best Threshold: {best_threshold:.4f}")
print(f"Best F1 Score: {best_f1:.4f}")

from sklearn.metrics import precision_score
import seaborn as sns

# Precision@K (Top 10% of predictions by confidence)
k = int(0.10 * len(y_test))
top_k_indices = np.argsort(y_proba)[-k:]
precision_at_k = precision_score(y_test.iloc[top_k_indices], y_pred[top_k_indices])
print(f"Precision@Top10%: {precision_at_k:.4f}")

# Lift Chart
df_lift = pd.DataFrame({
    "y_true": y_test,
    "y_score": y_proba
}).sort_values("y_score", ascending=False).reset_index(drop=True)
df_lift["bucket"] = pd.qcut(df_lift.index, 10, labels=False)

lift_table = df_lift.groupby("bucket").agg({
    "y_true": ["sum", "count"]
}).reset_index()
lift_table.columns = ["bucket", "conversions", "total"]
lift_table["conversion_rate"] = lift_table["conversions"] / lift_table["total"]
baseline_rate = df_lift["y_true"].mean()
lift_table["lift"] = lift_table["conversion_rate"] / baseline_rate

# Plot Lift Chart
plt.figure(figsize=(8, 5))
sns.lineplot(data=lift_table, x="bucket", y="lift", marker="o")
plt.axhline(1.0, linestyle="--", color="gray")
plt.title("Lift Chart (Decile Buckets)")
plt.xlabel("Decile (0 = Top Scoring)")
plt.ylabel("Lift over Baseline")
plt.grid(True)
plt.tight_layout()
plt.show()

# SHAP interpretability
import shap

explainer = shap.Explainer(pipeline.named_steps['model'], pipeline.named_steps['preprocessor'].transform(X_train))
shap_values = explainer(pipeline.named_steps['preprocessor'].transform(X_test))

# SHAP summary plot
shap.summary_plot(shap_values, features=pipeline.named_steps['preprocessor'].transform(X_test), feature_names=all_feature_names)

# Export high-conversion-likelihood predictions
output_df = X_test.copy()
output_df = output_df.reset_index()
# Check and add if the original dataframe contains these columns
if "user_id" in df.columns and "session_id" in df.columns:
    df_ids = df[["user_id", "session_id"]].reset_index(drop=True)
    output_df = output_df.merge(df_ids, left_on="index", right_index=True, how="left")
else:
    output_df["user_id"] = np.nan
    output_df["session_id"] = np.nan
output_df["p_conversion"] = y_proba
output_df["converted"] = y_test.values
output_df["top_10pct_flag"] = 0
output_df.loc[top_k_indices, "top_10pct_flag"] = 1

# Save full prediction results
output_df.to_csv("outputs/session_predictions.csv", index=False)

# Save top 10% of sessions by conversion probability
top_k = int(0.10 * len(output_df))
top_sessions = output_df.nlargest(top_k, "p_conversion")
top_sessions.to_csv("outputs/top_10pct_sessions.csv", index=False)
print(f"Saved top {top_k} high-probability sessions to outputs/top_10pct_sessions.csv")