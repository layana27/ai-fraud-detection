import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

import joblib


# 1. Read the dataset
data = pd.read_csv("fraud_data.csv")


# 2. Separate input and output
X = data[["amount", "transaction_type", "location"]]
y = data["is_fraud"]


# 3. Identify text columns
categorical_columns = ["transaction_type", "location"]


# 4. Convert text values into numbers
preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_columns
        )
    ],
    remainder="passthrough"
)


# 5. Create the machine-learning model
model = DecisionTreeClassifier(random_state=42)


# 6. Create the complete pipeline
pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# 7. Split the dataset
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)


# 8. Train the model
pipeline.fit(X_train, y_train)


# 9. Test the model
predictions = pipeline.predict(X_test)

accuracy = accuracy_score(y_test, predictions)

print("Model trained successfully!")
print("Model accuracy:", accuracy)


# 10. Save the trained model
joblib.dump(pipeline, "fraud_model.pkl")

print("Model saved as fraud_model.pkl")