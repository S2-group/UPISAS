from flask import Flask, request, jsonify
import pandas as pd
import os

from .spam_model import SpamModel


PREDICTION_VALUES = ['ham', 'spam']

def boolean_env(name, default=False):
    """Returns the boolean value of an environment variable."""
    value = os.environ.get(name, default)
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        raise ValueError(f"Invalid value for {name} environment variable. Must be True or False.")

def setup():
    app = Flask(__name__)

    model = SpamModel("spam", "v0", flask_app=app)
    model.setup()

    @app.route('/update', methods=['POST'])
    def update():
        """
        This serves a very specific purpose. It is used to update the data the model loads.
        Will only be called once during an adaptation.
        """
        e1_df = pd.read_csv('./mlops/data/enron1.csv')
        e2_df = pd.read_csv('./mlops/data/enron2.csv')
        # Merge the two datasets and write to a new file
        emails_df = pd.concat([e1_df, e2_df])
        emails_df.to_csv('./mlops/data/emails.csv', index=False)
        return "Email data updated."

    @app.route('/reset', methods=['POST'])
    def reset():
        """
        This serves a very specific purpose. It is used to reset the model to its initial state.
        Will only be called during the beginning of an adaptation execution.
        """
        e1_df = pd.read_csv('./mlops/data/enron1.csv')
        e1_df.to_csv('./mlops/data/emails.csv', index=False)
        return "Email data reset."
    
    @app.route('/test', methods=['POST'])
    def test():
        """
        This serves a very specific purpose. It is used to test the model and update the accuracy value.
        """
        dataset_type = None
        output_graph = False

        body = request.get_json()
        if body:
            if 'data_type' in body:
                dataset_type = body['data_type']
            if 'output_graph' in body:
                output_graph = body['output_graph']

        data = pd.read_csv('./mlops/data/emails.csv')

        output = model.test(dataframe=data, data_type=dataset_type, output_graph=output_graph)

        return jsonify(output)

    return app

app = setup()

if __name__ == '__main__':
    app.run(debug=boolean_env('DEBUG'))
