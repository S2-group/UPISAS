import pandas as pd

from mlops.spam_model import SpamModel

def main():
    model = SpamModel("spam", "v0", None)
    e1_df = pd.read_csv('./mlops/data/enron1.csv')
    e2_df = pd.read_csv('./mlops/data/enron2.csv')
    model.train(e1_df)

    # Test E1 model on E1 data
    results = model.test(e1_df, 'test', output_graph=True)
    print("Accuracy:", results["accuracy"])
    print("Classification Report:", results["classification_report"])

    # Test E1 model on E2 test data
    results = model.test(e2_df, 'test', output_graph=True)
    print("Accuracy:", results["accuracy"])
    print("Classification Report:", results["classification_report"])

    # Test E1 model on E2 train data
    results = model.test(e2_df, 'train', output_graph=True)
    print("Accuracy:", results["accuracy"])
    print("Classification Report:", results["classification_report"])

if __name__ == "__main__":
    main()