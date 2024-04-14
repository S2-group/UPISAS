from abc import ABC, abstractmethod
import logging
import json
import uuid

from flask import request, jsonify
import redis
from joblib import dump, load

from .versioning import get_next_version, get_latest_version


class BasedManagedModel(ABC):
    """
    An abstract class representing a generic ML model. including functionality for training, testing, and inference.
    """
    _model = None
    _data = []

    def __init__(self, 
                 model_name: "Name of the model", 
                 model_version: "Version of the model",):
        self.model_name = model_name
        self.model_version = model_version
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
    def store_data(self, data):
        """
        Stores the data in local memory.
        """
        self._data.append(data)

    def get_data(self):
        """
        Returns the data stored in local memory.
        """
        return self._data
    
    def save(self, models):
        """
        Saves the model and any other relevant objects like a vectorizer.
        This takes in a dictionary of objects to save, where the key is the name of the object and the value is the object itself.
        """
        version = get_next_version()
        for name, obj in models.items():
            self.logger.info(f"Saving {name}...")
            dump(obj, f"./mlops/models/{name}@latest.joblib")
            dump(obj, f"./mlops/models/{name}@{version}.joblib")
    
    def load(self, names, version="latest"):
        """
        Takes in an array of strings, where each string is the name of the object to load.
        Optionally, the version of the object can be specified, defaults to latest.
        Returns a dictionary of the loaded objects.
        """
        self.model_version = get_latest_version() if version == "latest" else version
        loaded_objects = {}
        for name in names:
            self.logger.info(f"Loading {name}...")
            loaded_objects[name] = load(f"./mlops/models/{name}@{version}.joblib")
        return loaded_objects
    
    @abstractmethod
    def preprocess(self, data):
        """
        Abstract method that preprocesses the data.
        """
        pass
    
    @abstractmethod
    def train(self, adaptation_options):
        """
        This method should train the model. 
        It should return a key-value dict where the key is the name of the thing to be saved, and the value is the thing itself. E.g. {"model": model, "vectorizer": vectorizer}.
        Note: this method MUST at least return the model in the "model" key field.
        """
        pass

    @abstractmethod
    def test(self, data=None):
        """
        Evaluate the model here.
        """
        pass

    @abstractmethod
    def inference(self, data=None):
        """
        Abstract method that calls the model.
        Should return two values: the prediction and the confidence.
        """
        pass

    @abstractmethod
    def adaptation_options(self):
        """
        Abstract method that returns the adaptation options.
        """
        pass
    
    @abstractmethod
    def monitor_schema(self):
        pass
    
    @abstractmethod
    def execute_schema(self):
        pass
    
    @abstractmethod
    def adaptation_options_schema(self):
        pass


class FlaskManagedModel(BasedManagedModel):
    """
    A class representing a generic ML model. including functionality for training, testing, and inference.
    """
    redis_client = None

    def __init__(self, 
                 model_name, 
                 model_version,
                 flask_app,):
        super().__init__(model_name, model_version)
        self.flask_app = flask_app
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    def setup(self):
        """
        Sets up the flask app with the necessary routes.
        """
        @self.flask_app.route('/', methods=['GET'])
        def index():
            return jsonify({
                "name": self.model_name,
                "version": self.model_version,
                "status": "running"
                })
        
        @self.flask_app.route('/monitor', methods=['GET'])
        def monitor():
            keys = self.redis_client.keys()  # Retrieve all keys
            all_data = []
            for key in keys:
                data = self.redis_client.get(key)  # Retrieve data
                all_data.append(json.loads(data))  # Convert JSON string back to dictionary
                self.redis_client.delete(key)  # Delete the record after retrieving

            return jsonify(all_data)
        
        @self.flask_app.route('/execute', methods=['PUT'])
        def execute():
            data = request.get_json()
            if not data:
                self.logger.error("No data provided.")
                data = None
            
            output = self.train(data)

            self.save(output)

            return "ok"
        
        @self.flask_app.route('/adaptation_options', methods=['GET'])
        def adaptation_options():
            return jsonify(self.adaptation_options())

        @self.flask_app.route('/inference', methods=['POST'])
        def inference():
            # Validate request body contains 'body' field
            data = request.get_json()
            if not data:
                return jsonify({"error": "Please specify data to pass to the model"}), 400

            # Run inference and store the response in redis
            response = self.inference(data)
            key = str(uuid.uuid4())
            self.redis_client.set(key, json.dumps(response))

            return jsonify(response)
        
        @self.flask_app.route('/monitor_schema', methods=['GET'])
        def monitor_schema():
            return jsonify(self.monitor_schema())
        
        @self.flask_app.route('/execute_schema', methods=['GET'])
        def execute_schema():
            return jsonify(self.execute_schema())
        
        @self.flask_app.route('/adaptation_options_schema', methods=['GET'])
        def adaptation_options_schema():
            return jsonify(self.adaptation_options_schema())
        
    def run_server(self, host="0.0.0.0", port=5000):
        """
        Runs the flask app.
        """
        self.flask_app.run(host=host, port=port)
        