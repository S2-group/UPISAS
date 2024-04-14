import pandas as pd
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re
import hashlib

from mcyclops.training.managed_model import FlaskManagedModel

class SpamModel(FlaskManagedModel):
    _model = None
    _vectorizer = None

    _accuracy = None
    _classification_report = None
    _recall = None

    def __init__(self, model_name, model_version, flask_app):
        super().__init__(model_name, model_version, flask_app)
        self._data = []

    def preprocess(self, body):
        # Remove newlines
        body = body.replace("\n", " ")
        body = body.replace("\r", " ")

        # Remove special characters and digits
        body = re.sub(r'[^a-zA-Z\s]', '', body, re.I|re.A)

        # Remove multiple spaces
        body = re.sub(r'\s+', ' ', body)

        body = body.lower()
        body = ''.join([char for char in body if char not in string.punctuation])
        words = body.split()
        words = [WordNetLemmatizer().lemmatize(word) for word in words if word not in stopwords.words('english')]
        return ' '.join(words)
    
    def train(self, adaptation_options=None):
        data_path = "./mlops/data/emails.csv"

        if adaptation_options is not None and "data_path" in adaptation_options:
            data_path = adaptation_options["data_path"]

        if (
            adaptation_options is not None 
            and "retrain" in adaptation_options 
            and not adaptation_options["retrain"]):
            raise ValueError("Model is not set to retrain.")
        
        # Load data
        emails_df = pd.read_csv(data_path)

        emails_df["processed_body"] = emails_df["body"].apply(self.preprocess)

        # Vectorization with bi-grams
        ngrams = (1, 1) 
        if adaptation_options is not None and "ngram" in adaptation_options:
            ngrams = (1, adaptation_options["ngram"])
        self._vectorizer = TfidfVectorizer(ngram_range=ngrams)

        # Encode labels
        le = LabelEncoder()
        emails_df["encoded_labels"] = le.fit_transform(emails_df["label"])

        # Split dataset based on data_type
        train_df = emails_df[emails_df["data_type"] == "train"]
        test_df = emails_df[emails_df["data_type"] == "test"]

        # Split into X and y
        X_train = self._vectorizer.fit_transform(train_df["processed_body"])
        y_train = train_df["encoded_labels"]
        X_test = self._vectorizer.transform(test_df["processed_body"])
        y_test = test_df["encoded_labels"]

        # Train Naive Bayes model
        self._model = MultinomialNB()
        self._model.fit(X_train, y_train)

        # Evaluate model
        y_pred = self._model.predict(X_test)
        self._accuracy = accuracy_score(y_test, y_pred)
        self._classification_report = classification_report(y_test, y_pred)
        self.logger.info("Accuracy:", self._accuracy)
        self.logger.info("Classification Report:", self._classification_report)

        # Save accuracy to a text file
        with open(f"./mlops/data/{self.model_version}_accuracy.txt", "w") as f:
            f.write(str(self._accuracy))

        return {
            "model": self._model,
            "vectorizer": self._vectorizer
        }
    
    def test(self, dataframe=None, data_type=None, output_graph=False):
        """
        dataframe is the pd.DataFrame to test on.
        data_type is the subset of data to test on, e.g. "train" or "test".
        """
        if dataframe is None:
            raise ValueError("Data must be provided for testing.")
        
        if self._model is None or self._vectorizer is None:
            loaded = self.load(["model", "vectorizer"])
            self._model = loaded["model"]
            self._vectorizer = loaded["vectorizer"]
        
        emails_df = dataframe
        emails_df["processed_body"] = emails_df["body"].apply(self.preprocess)

        # Encode labels
        le = LabelEncoder()
        emails_df["encoded_labels"] = le.fit_transform(emails_df["label"])

        test_df = emails_df
        if data_type is not None:
            test_df = emails_df[emails_df["data_type"] == data_type]
        
        X_test = self._vectorizer.transform(test_df["processed_body"])
        y_test = test_df["encoded_labels"]

        # Evaluate model
        y_pred = self._model.predict(X_test)
        self._accuracy = accuracy_score(y_test, y_pred)
        self._classification_report = classification_report(y_test, y_pred)
        self.logger.info("Accuracy:", self._accuracy)
        self.logger.info("Classification Report:", self._classification_report)

        self._recall = self._classification_report.split("\n")[3].split()[3]

        # Save accuracy to a text file
        with open(f"./mlops/data/{self.model_version}_accuracy.txt", "w") as f:
            f.write(str(self._accuracy))

        if output_graph:
            self.logger.info("Outputting graph...")
            
            # Get predicted probabilities
            y_probs = self._model.predict_proba(X_test)[:, 1]

            # Calculate ROC curve
            fpr, tpr, thresholds = roc_curve(y_test, y_probs)

            # Calculate AUC (Area under the ROC Curve)
            roc_auc = auc(fpr, tpr)

            # Plotting the ROC Curve
            plt.figure()
            plt.plot(fpr, tpr, color='darkorange', lw=2, label='ROC curve (area = %0.2f)' % roc_auc)
            plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
            plt.xlim([0.0, 1.0])
            plt.ylim([0.0, 1.05])
            plt.xlabel('False Positive Rate')
            plt.ylabel('True Positive Rate')
            plt.title('Receiver Operating Characteristic (ROC) Curve')
            plt.legend(loc="lower right")
            plt.savefig(
                f"""./mlops/data/{
                    self.model_version
                }_sensitivity_vs_specificity_{
                    emails_df["dataset"].iloc[0]
                }_{data_type}.png"""
            )

        return {
            "accuracy": self._accuracy,
            "classification_report": self._classification_report
        }
    
    def inference(self, data=None):
        if data is None:
            raise ValueError("Data must be provided for inference.")
        
        # attempt to load the latest model, this keeps the workers up to date after a retrain
        loaded = self.load(["model", "vectorizer"])
        self._model = loaded["model"]
        self._vectorizer = loaded["vectorizer"]

        # Get the latest accuracy
        try:
            with open(f"./mlops/data/{self.model_version}_accuracy.txt", "r") as f:
                self._accuracy = float(f.read())
        except Exception as e:
            self.logger.error(f"Error reading accuracy, defaulting to v0: {e}")
            with open(f"./mlops/data/v0_accuracy.txt", "r") as f:
                self._accuracy = float(f.read())
        
        # Incoming data matches the shape of the training data: 
        # {"body": "some email body", "label": 0, "data_type": "train", "dataset": "enron1"}
        email = self.preprocess(data["body"])
        vectorized_email = self._vectorizer.transform([email])
        prediction = self._model.predict(vectorized_email)
        confidence = self._model.predict_proba(vectorized_email).max()

        return {
            "ngram": 1,
            "data_hash": self._get_training_data_hash(),
            "accuracy": float(self._accuracy),
            "prediction": int(prediction[0]),
            "confidence": float(confidence),
            "actual_label": data["label"],
            "model_version": self.model_version,
            "from_dataset": data["dataset"]
        }
    
    def _get_training_data_hash(self):
        hash_object = hashlib.sha256()
        emails_df = pd.read_csv("./mlops/data/emails.csv")
        hash_object.update(emails_df.to_string().encode('utf-8'))
        return hash_object.hexdigest()
    
    def monitor_schema(self):
        return {
            "type": "object",
            "properties": {
                "ngram": {"type": "integer"},
                "data_hash": {"type": "string"},
                "accuracy": {"type": "number"},
                "prediction": {"type": "number"},
                "confidence": {"type": "number"},
                "actual_label": {"type": "integer"},
                "model_version": {"type": "string"},
                "from_dataset": {"type": "string"}
            }
        }

    def execute_schema(self):
        return {
            "type": "object",
            "properties": {
                "ngram": {"type": "integer"},
                "retrain": {"type": "boolean"},
                "data_path": {"type": "string"},
            }
        }
    
    def adaptation_options_schema(self):
        return {
            "type": "object",
            "properties": {
                "ngram": {"type": "integer"},
            }
        }
    
    def adaptation_options(self):
        return {
            "ngram": self._vectorizer.ngram_range[1]
        }