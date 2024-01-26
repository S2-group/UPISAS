import os
import joblib

def get_versions():
    """Returns a list of all the available model versions."""
    versions = []
    for file in os.listdir("models"):
        if file.endswith(".joblib"):
            versions.append(file.split("@")[1].split(".")[0])
    return versions

def get_latest_version():
    """Returns the latest semver version of the model."""
    versions = get_versions()
    return max(versions)

def get_model(version='latest'):
    """Returns the model with the specified version."""
    if version is None:
        version = get_latest_version()
    return joblib.load(f"models/model@{version}.joblib")

def get_vectorizer(version='latest'):
    """Returns the vectorizer with the specified version."""
    if version is None:
        version = get_latest_version()
    return joblib.load(f"models/vectorizer@{version}.joblib")