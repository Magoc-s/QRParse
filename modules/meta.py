from multiprocessing import Lock


class McSingleton(type):
    """
    Singleton metaclass for managing the AssetLoadPhaseLogger singleton. Do not attempt to directly instantiate,
    reference or otherwise use this class. Its function is autonomous.
    """
    _instances = {}

    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]
