import pandas as pd
from xgboost import XGBClassifier
import joblib

# load dataset
data = pd.read_csv("dataset.csv")

X = data[['T']]
y = data['Y']

# fix label values
y = y.replace({3:2})

# train model
model = XGBClassifier(use_label_encoder=False, eval_metric='mlogloss')
model.fit(X, y)

# save model
joblib.dump(model, "model.pkl")

print("Model Trained and Saved Successfully")