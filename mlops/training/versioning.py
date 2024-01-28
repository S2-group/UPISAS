import os
import joblib

def get_versions():
    """
    Returns a list of all the available model versions, which take the form 'v1', 'v2', etc.
    """
    try:
        os.mkdir("./mlops/models")
    except FileExistsError:
        pass

    versions = []
    for file in os.listdir("./mlops/models"):
        if file.endswith(".joblib") and "model@" in file:
            versions.append(file.split("@")[1].split(".")[0])
    return versions

def get_latest_version():
    """Returns the latest semver version of the model."""
    versions = get_versions()
    return max(versions)

def get_next_version():
    """Returns the next semver version of the model."""
    versions = get_versions()
    return f"v{len(versions) - 1}" # latest is included, so no need to add 1

def get_model(version='latest'):
    """Returns the model with the specified version."""
    if version is None:
        version = get_latest_version()
    return joblib.load(f"./mlops/models/model@{version}.joblib")

def get_vectorizer(version='latest'):
    """Returns the vectorizer with the specified version."""
    if version is None:
        version = get_latest_version()
    return joblib.load(f"./mlops/models/vectorizer@{version}.joblib")