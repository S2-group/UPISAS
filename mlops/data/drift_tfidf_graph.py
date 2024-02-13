import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

# Load datasets
enron1_df = pd.read_csv('./mlops/data/enron1.csv')
enron2_df = pd.read_csv('./mlops/data/enron2.csv')
enron3_df = pd.read_csv('./mlops/data/enron3.csv')
enron4_df = pd.read_csv('./mlops/data/enron4.csv')
enron5_df = pd.read_csv('./mlops/data/enron5.csv')
enron6_df = pd.read_csv('./mlops/data/enron6.csv')

combined_text = pd.concat([enron1_df['body'], enron2_df['body'], enron3_df['body'], enron4_df['body'], enron5_df['body'], enron6_df['body']])

# Initialize TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(stop_words='english')

# Fit the vectorizer on the combined dataset to compute global IDF values
tfidf_vectorizer.fit(combined_text)

# Transform each dataset separately to get TF-IDF scores
tfidf_enron1 = tfidf_vectorizer.transform(enron1_df['body'])
tfidf_enron2 = tfidf_vectorizer.transform(enron2_df['body'])
tfidf_enron3 = tfidf_vectorizer.transform(enron3_df['body'])
tfidf_enron4 = tfidf_vectorizer.transform(enron4_df['body'])
tfidf_enron5 = tfidf_vectorizer.transform(enron5_df['body'])
tfidf_enron6 = tfidf_vectorizer.transform(enron6_df['body'])

# Calculate average TF-IDF scores for each dataset
avg_tfidf_enron1 = np.array(tfidf_enron1.sum(axis=0) / tfidf_enron1.getnnz(axis=0)).flatten()
avg_tfidf_enron2 = np.array(tfidf_enron2.sum(axis=0) / tfidf_enron2.getnnz(axis=0)).flatten()
avg_tfidf_enron3 = np.array(tfidf_enron3.sum(axis=0) / tfidf_enron3.getnnz(axis=0)).flatten()
avg_tfidf_enron4 = np.array(tfidf_enron4.sum(axis=0) / tfidf_enron4.getnnz(axis=0)).flatten()
avg_tfidf_enron5 = np.array(tfidf_enron5.sum(axis=0) / tfidf_enron5.getnnz(axis=0)).flatten()
avg_tfidf_enron6 = np.array(tfidf_enron6.sum(axis=0) / tfidf_enron6.getnnz(axis=0)).flatten()

# Create a DataFrame for visualization
words = tfidf_vectorizer.get_feature_names_out()
df_avg_tfidf = pd.DataFrame({'Word': words, 'Enron1': avg_tfidf_enron1, 'Enron2': avg_tfidf_enron2, 'Enron3': avg_tfidf_enron3, 'Enron4': avg_tfidf_enron4, 'Enron5': avg_tfidf_enron5, 'Enron6': avg_tfidf_enron6})

# For visualization, let's focus on the top N words by average TF-IDF score in Enron1
N = 50
top_n_words = df_avg_tfidf.sort_values(by='Enron1', ascending=False).head(N)['Word']

# Plotting
plt.figure(figsize=(12, 8))
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron1', label='Enron 1', shade=True)
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron2', label='Enron 2', shade=True)
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron3', label='Enron 3', shade=True)
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron4', label='Enron 4', shade=True)
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron5', label='Enron 5', shade=True)
sns.kdeplot(data=df_avg_tfidf[df_avg_tfidf['Word'].isin(top_n_words)], x='Enron6', label='Enron 6', shade=True)
plt.xlabel('Average TF-IDF Score')
plt.ylabel('Density')
plt.title('Distribution of Average TF-IDF Scores for Top Words')
plt.legend()
plt.savefig('./mlops/data/enron-tfidf-distributions-all.png')
