import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score, classification_report
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
from joblib import dump

# Example dataset
emails = ["your free lottery ticket", "meeting request", ...]  # Add your email texts
labels = [1, 0, ...]  # 1 for spam, 0 for not spam

# Text preprocessing
def preprocess(text):
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    words = text.split()
    words = [WordNetLemmatizer().lemmatize(word) for word in words if word not in stopwords.words('english')]
    return ' '.join(words)

emails = [preprocess(email) for email in emails]

# Vectorization with bi-grams
vectorizer = TfidfVectorizer(ngram_range=(1, 2))
X = vectorizer.fit_transform(emails)
y = np.array(labels)

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train Naive Bayes model
model = MultinomialNB()
model.fit(X_train, y_train)

# Evaluate model
y_pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

# Save model
dump(model, "model@latest.joblib")
dump(vectorizer, "vectorizer@latest.joblib")

# Predict new emails
# def predict_email(new_email):
#     processed_email = preprocess(new_email)
#     vectorized_email = vectorizer.transform([processed_email])
#     return model.predict(vectorized_email)[0]

# Example usage
# print(predict_email("Congratulations, you've won a free cruise!"))
