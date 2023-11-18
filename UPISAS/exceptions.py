class UPISASException(Exception):
    pass


class DockerDaemonNotRunning(UPISASException):
    pass


class DockerImageNotFoundOnDockerHub(UPISASException):
    pass


class ServerNotReachable(UPISASException):
    pass


class EndpointNotReachable(UPISASException):
    pass


class IncompleteJSONSchema(UPISASException):
    pass
