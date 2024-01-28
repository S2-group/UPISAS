import os
import re
import pandas as pd

def text_files_to_dataframe(directory):
  file_list = os.listdir(directory)
  data = []
  for file_name in file_list:
    if file_name.endswith(".txt"):
      file_path = os.path.join(directory, file_name)
      with open(file_path, "rb") as file:
        body = file.read().decode("utf-8", errors="replace")

        # Remove newlines
        body = body.replace("\n", " ")
        body = body.replace("\r", " ")

        # Remove special characters and digits
        body = re.sub(r'[^a-zA-Z\s]', '', body, re.I|re.A)

        # Remove multiple spaces
        body = re.sub(r'\s+', ' ', body)

        data.append(body)
  
  df = pd.DataFrame(data, columns=["body"])
  return df

def load_ham_and_spam(user_dir):
  ham_directory = os.path.join(user_dir, "ham")
  spam_directory = os.path.join(user_dir, "spam")

  ham_df = text_files_to_dataframe(ham_directory)
  ham_df["label"] = 0 # ham
  # For 20% of datapoints, we will mark them as "test" data
  ham_df["data_type"] = "train"
  ham_df.loc[ham_df.sample(frac=0.2).index, "data_type"] = "test"

  spam_df = text_files_to_dataframe(spam_directory)
  spam_df["label"] = 1 # spam
  spam_df["data_type"] = "train"
  spam_df.loc[spam_df.sample(frac=0.2).index, "data_type"] = "test"

  return pd.concat([ham_df, spam_df])

def load_all_user_dfs(data_dir):
  user_dfs = []
  # The folders are actually named enron1, enron2, etc.
  for user_name in os.listdir(data_dir):
    user_directory = os.path.join(data_dir, user_name)
    user_df = load_ham_and_spam(user_directory)
    user_df["dataset"] = user_name

    user_dfs.append(user_df)
  return user_dfs


def main():
  # It is expecting the dataset referenced in the paper to be in a folder called "enron-spam" in the parent directory UPISAS
  data_dir = os.path.join(os.getcwd(), "..", "enron-spam")
  user_dfs = load_all_user_dfs(data_dir)
  for df in user_dfs:
    filename = df["dataset"].iloc[0] + ".csv"
    df.to_csv(os.path.join(os.path.dirname(__file__), filename), index=False)

if __name__ == "__main__":
  main()