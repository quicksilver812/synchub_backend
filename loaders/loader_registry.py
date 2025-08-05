LOADER_REGISTRY = {}

def register_loader(cls):
    instance = cls()
    LOADER_REGISTRY[instance.name()] = instance
    return cls
