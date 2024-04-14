import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt

# Load datasets
enron1_df = pd.read_csv('./mlops/data/enron1.csv')
enron2_df = pd.read_csv('./mlops/data/enron2.csv')
enron3_df = pd.read_csv('./mlops/data/enron3.csv')
enron4_df = pd.read_csv('./mlops/data/enron4.csv')
enron5_df = pd.read_csv('./mlops/data/enron5.csv')
enron6_df = pd.read_csv('./mlops/data/enron6.csv')

# Combine the text data from both datasets for vectorization
combined_text = pd.concat([enron1_df['body'], enron2_df['body'], enron3_df['body'], enron4_df['body'], enron5_df['body'], enron6_df['body']])

# Initialize CountVectorizer
vectorizer = CountVectorizer(stop_words='english')

# Fit and transform the combined text data
word_counts = vectorizer.fit_transform(combined_text)

# Split the combined word counts back into individual datasets
split_index_1 = len(enron1_df)
split_index_2 = split_index_1 + len(enron2_df)
split_index_3 = split_index_2 + len(enron3_df)
split_index_4 = split_index_3 + len(enron4_df)
split_index_5 = split_index_4 + len(enron5_df)
word_counts_enron1 = word_counts[:split_index_1, :]
word_counts_enron2 = word_counts[split_index_1:split_index_2, :]
word_counts_enron3 = word_counts[split_index_2:split_index_3, :]
word_counts_enron4 = word_counts[split_index_3:split_index_4, :]
word_counts_enron5 = word_counts[split_index_4:split_index_5, :]
word_counts_enron6 = word_counts[split_index_5:, :]

# Calculate normalized word frequencies for each dataset
freqs_enron1 = word_counts_enron1.sum(axis=0) / word_counts_enron1.sum()
freqs_enron2 = word_counts_enron2.sum(axis=0) / word_counts_enron2.sum()
freqs_enron3 = word_counts_enron3.sum(axis=0) / word_counts_enron3.sum()
freqs_enron4 = word_counts_enron4.sum(axis=0) / word_counts_enron4.sum()
freqs_enron5 = word_counts_enron5.sum(axis=0) / word_counts_enron5.sum()
freqs_enron6 = word_counts_enron6.sum(axis=0) / word_counts_enron6.sum()


# Calculate the drift in word usage
drifts = np.abs(freqs_enron1 - freqs_enron2) + np.abs(freqs_enron1 - freqs_enron3) + np.abs(freqs_enron1 - freqs_enron4) + np.abs(freqs_enron1 - freqs_enron5) + np.abs(freqs_enron1 - freqs_enron6)

# Get feature names (words)
words = vectorizer.get_feature_names_out()

# Create a DataFrame for the drifts
drift_df = pd.DataFrame(drifts.T, index=words, columns=['drift'])

# Sort the DataFrame by drift to find the words with the highest drift
drift_df_sorted = drift_df.sort_values(by='drift', ascending=False)

# Plotting the top N words with the highest drift
top_n = 20
top_drift_words = drift_df_sorted.head(top_n)
plt.figure(figsize=(10, 8))
plt.barh(top_drift_words.index[::-1], top_drift_words['drift'][::-1])
plt.xlabel('Drift')
plt.ylabel('Words')
plt.title('Top Words with Highest Drift in Usage Between Datasets')
plt.savefig('./mlops/data/enron-all-drift.png')
