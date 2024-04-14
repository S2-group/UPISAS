import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load datasets
enron1_df = pd.read_csv('./mlops/data/enron1.csv')
enron2_df = pd.read_csv('./mlops/data/enron2.csv')
enron3_df = pd.read_csv('./mlops/data/enron3.csv')
enron4_df = pd.read_csv('./mlops/data/enron4.csv')
enron5_df = pd.read_csv('./mlops/data/enron5.csv')
enron6_df = pd.read_csv('./mlops/data/enron6.csv')

# Function to calculate unique word count
def unique_word_count(text):
    words = text.split()  # Split text into words
    unique_words = set(words)  # Convert list of words into a set to remove duplicates
    return len(unique_words)

# Calculate unique word count for each email
enron1_df['unique_word_count'] = enron1_df['body'].apply(unique_word_count)
enron2_df['unique_word_count'] = enron2_df['body'].apply(unique_word_count)
enron3_df['unique_word_count'] = enron3_df['body'].apply(unique_word_count)
enron4_df['unique_word_count'] = enron4_df['body'].apply(unique_word_count)
enron5_df['unique_word_count'] = enron5_df['body'].apply(unique_word_count)
enron6_df['unique_word_count'] = enron6_df['body'].apply(unique_word_count)

# Plotting the distributions
plt.figure(figsize=(10, 6))
sns.kdeplot(enron1_df['unique_word_count'], label='Enron 1', shade=True)
sns.kdeplot(enron2_df['unique_word_count'], label='Enron 2', shade=True)
sns.kdeplot(enron3_df['unique_word_count'], label='Enron 3', shade=True)
sns.kdeplot(enron4_df['unique_word_count'], label='Enron 4', shade=True)
sns.kdeplot(enron5_df['unique_word_count'], label='Enron 5', shade=True)
sns.kdeplot(enron6_df['unique_word_count'], label='Enron 6', shade=True)
plt.xlabel('Unique Word Count')
plt.ylabel('Density')
plt.title('Distribution of Unique Word Count Between Datasets')
plt.legend()
plt.savefig('./mlops/data/enron-unique-word-count-distributions-all.png')
