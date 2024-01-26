from flask import Flask, request, jsonify
from training import preprocess, get_model, get_vectorizer
import os

PREDICTION_VALUES = ['ham', 'spam']

def boolean_env(name, default=False):
    """Returns the boolean value of an environment variable."""
    value = os.environ.get(name, default)
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        raise ValueError(f"Invalid value for {name} environment variable. Must be True or False.")

app = Flask(__name__)

# Load the model and vectorizer
model_version = os.environ.get('MODEL_VERSION', 'latest')
vectorizer_version = os.environ.get('VECTORIZER_VERSION', 'latest')
model_path = os.path.join(os.path.dirname(__file__), 'models', f"model@{model_version}.joblib")
vectorizer_path = os.path.join(os.path.dirname(__file__), 'models', f"vectorizer@{vectorizer_version}.joblib")

if os.path.exists(model_path) and os.path.exists(vectorizer_path):
    model = get_model(version=model_version)
    vectorizer = get_vectorizer(version=vectorizer_version)
else:
    raise FileNotFoundError("Model and vectorizer file not found.")

@app.route('/predict', methods=['POST'])
def predict():
    # Validate request body contains 'body' field
    data = request.get_json()
    if not data or 'body' not in data:
        return jsonify({"error": "Please provide an email for prediction"}), 400

    # Preprocess and vectorize the email
    email = preprocess(data['body'])
    vectorized_email = vectorizer.transform([email])

    # Predict and return the result
    prediction = model.predict(vectorized_email)
    confidence = model.predict_proba(vectorized_email).max()
    return jsonify({
        "prediction": PREDICTION_VALUES[int(prediction[0])],
        "confidence": float(confidence)
        })

if __name__ == '__main__':
    app.run(debug=boolean_env('DEBUG'))
