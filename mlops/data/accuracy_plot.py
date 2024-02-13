import pandas as pd
import matplotlib.pyplot as plt

# Load the CSV files into pandas dataframes
df1 = pd.read_csv('./mlops/experiments/mlops/run_0/results.csv')
df2 = pd.read_csv('./mlops/experiments/mlops/run_1/results.csv')

# Optionally, if you need to distinguish between the two datasets in the combined plot
df1['source'] = 'No Retraining'
df2['source'] = 'Retraining'

# Add a 'number_of_emails' column based on the index + 1 (assuming email count starts at 1)
df1['number_of_emails'] = df1.index + 1
df2['number_of_emails'] = df2.index + 1

# Combine the dataframes
combined_df = pd.concat([df1, df2])

# Plotting
fig, ax = plt.subplots()
for label, df in combined_df.groupby('source'):
    ax.plot(df['number_of_emails'], df['model_acc'], label=label)

# To mark the change in 'model_version' from v0 to v1 and 'from_dataset' from enron1 to enron2,
# we find the first occurrence of these changes in the combined dataframe.
model_version_change = combined_df[combined_df['model_version'] == 'v1']['number_of_emails'].min()
from_dataset_change = combined_df[combined_df['from_dataset'] == 'enron2']['number_of_emails'].min()

plt.axvline(x=model_version_change, color='k', linestyle='--', lw=2, label='v0 to v1 change')
plt.axvline(x=from_dataset_change, color='r', linestyle='--', lw=2, label='enron1 to enron2 change')

plt.legend()
plt.xlabel('Number of Emails')
plt.ylabel('Model Accuracy')
plt.title('Model Accuracy as a Function of Number of Emails')
plt.xlim(0, 140)  # Assuming you still want to limit the x-axis to 140
plt.savefig('two-run-accuracy-plot.png')
