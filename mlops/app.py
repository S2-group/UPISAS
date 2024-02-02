from flask import Flask
import os

from spam_model import SpamModel


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

    return app

app = setup()

if __name__ == '__main__':
    app.run(debug=boolean_env('DEBUG'))
