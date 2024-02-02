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

# Calculate a simple feature: average word length in each email
def avg_word_length(text):
    words = text.split()
    if len(words) == 0:
        return 0
    return sum(len(word) for word in words) / len(words)

enron1_df['avg_word_length'] = enron1_df['body'].apply(avg_word_length)
enron2_df['avg_word_length'] = enron2_df['body'].apply(avg_word_length)
enron3_df['avg_word_length'] = enron3_df['body'].apply(avg_word_length)
enron4_df['avg_word_length'] = enron4_df['body'].apply(avg_word_length)
enron5_df['avg_word_length'] = enron5_df['body'].apply(avg_word_length)
enron6_df['avg_word_length'] = enron6_df['body'].apply(avg_word_length)

# Plotting the distributions
plt.figure(figsize=(10, 6))
sns.kdeplot(enron1_df['avg_word_length'], label='Enron 1', shade=True)
sns.kdeplot(enron2_df['avg_word_length'], label='Enron 2', shade=True)
sns.kdeplot(enron3_df['avg_word_length'], label='Enron 3', shade=True)
sns.kdeplot(enron4_df['avg_word_length'], label='Enron 4', shade=True)
sns.kdeplot(enron5_df['avg_word_length'], label='Enron 5', shade=True)
sns.kdeplot(enron6_df['avg_word_length'], label='Enron 6', shade=True)
plt.xlabel('Average Word Length')
plt.ylabel('Density')
plt.title('Distribution of Average Word Length Between Datasets')
plt.legend()

plt.savefig('./mlops/data/enron-all-distributions.png')
