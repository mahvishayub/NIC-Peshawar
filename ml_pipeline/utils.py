import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score


# =====================================================
# COLUMN CLEANING (CRITICAL)
# =====================================================
def clean_columns(df):
    df = df.copy()
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.replace("\n", "", regex=False)
        .str.replace("  ", " ", regex=False)
    )
    return df


# =====================================================
# BUSINESS LOGIC — PERFORMANCE LABEL
# =====================================================
def create_performance_label(row):
    if row["Graduation"] != "Graduated":
        return "Low"

    if row["Revenue"] >= 30000000 and row["TotalJobs"] >= 10:
        return "High"

    return "Medium"


# =====================================================
# DATA PREPARATION
# =====================================================
def prepare_ml_data(df):
    """
    Cleans and prepares Startupwise data for ML
    """

    df = clean_columns(df)

    # Normalize Graduation column
    df["Graduation_Flag"] = df["Graduation"].apply(
        lambda x: 1 if str(x).strip().lower() == "graduated" else 0
    )

    # Ensure numeric columns
    numeric_cols = [
        "DirectJobs",
        "IndirectJobs",
        "TotalJobs",
        "Revenue",
        "Investment (In USD)"
    ]

    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # Feature definitions
    categorical_features = [
        "Cohort",
        "Vertical",
        "Technology",
        "Gender"
    ]

    # 🔧 CRITICAL FIX: enforce uniform string type
    for col in categorical_features:
        df[col] = df[col].astype(str).str.strip()

    features = categorical_features + numeric_cols

    df = df.dropna(subset=features + ["Graduation_Flag"])

    X = df[features]
    y = df["Graduation_Flag"]

    return X, y, df


# =====================================================
# TRAIN ML MODEL
# =====================================================
def train_graduation_model(df, model_path="models/graduation_model.pkl"):

    X, y, df_clean = prepare_ml_data(df)

    categorical_features = X.select_dtypes(include="object").columns.tolist()
    numeric_features = X.select_dtypes(exclude="object").columns.tolist()

    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features)
        ]
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model)
        ]
    )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    pipeline.fit(X_train, y_train)

    accuracy = accuracy_score(y_test, pipeline.predict(X_test))

    joblib.dump(pipeline, model_path)

    return pipeline, accuracy, df_clean


# =====================================================
# PREDICTION
# =====================================================
def generate_predictions(df, model_path="models/graduation_model.pkl"):

    df = clean_columns(df)

    pipeline = joblib.load(model_path)

    X, _, df_clean = prepare_ml_data(df)

    probabilities = pipeline.predict_proba(X)[:, 1]

    df_clean["Graduation_Probability"] = probabilities

    df_clean["Risk_Band"] = df_clean["Graduation_Probability"].apply(
        lambda p: "High" if p >= 0.7 else "Medium" if p >= 0.4 else "Low"
    )

    return df_clean
