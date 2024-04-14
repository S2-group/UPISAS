import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report, roc_curve, auc
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import re
from joblib import dump

from versioning import get_next_version

# Text preprocessing
def preprocess(body):
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

def train(emails_df):
    emails_df["processed_body"] = emails_df["body"].apply(preprocess)

    # Vectorization with bi-grams
    vectorizer = TfidfVectorizer(ngram_range=(1, 3))

    # Encode labels
    le = LabelEncoder()
    emails_df["encoded_labels"] = le.fit_transform(emails_df["label"])

    # Split dataset based on data_type
    train_df = emails_df[emails_df["data_type"] == "train"]
    test_df = emails_df[emails_df["data_type"] == "test"]

    # Split into X and y
    X_train = vectorizer.fit_transform(train_df["processed_body"])
    y_train = train_df["encoded_labels"]
    X_test = vectorizer.transform(test_df["processed_body"])
    y_test = test_df["encoded_labels"]
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Train Naive Bayes model
    model = MultinomialNB()
    model.fit(X_train, y_train)

    # Evaluate model
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    classification = classification_report(y_test, y_pred)
    print("Accuracy:", accuracy)
    print("Classification Report:", classification)

    # Save model
    dump(model, "./mlops/models/model@latest.joblib")
    dump(vectorizer, "./mlops/models/vectorizer@latest.joblib")

    # Save version of model as well
    version = get_next_version()
    dump(model, f"./mlops/models/model@{version}.joblib")
    dump(vectorizer, f"./mlops/models/vectorizer@{version}.joblib")

    # Get predicted probabilities
    y_probs = model.predict_proba(X_test)[:, 1]

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
    plt.savefig(f'./mlops/models/{version}_sensitivity_vs_specificity.png')

    return accuracy, classification


if __name__ == "__main__":
    # train initial version
    emails_df = pd.read_csv("./mlops/data/enron1.csv")
    train(emails_df)