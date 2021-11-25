class SportBlurbsError(Exception):
    pass


class MultipleDocumentsError(SportBlurbsError):
    def __init__(self, database_name, collection_name, filter):
        msg = f"Multiple documents for filter '{filter}' were found in '{database_name}.{collection_name}.'"
        super().__init__(msg)


class KeyNotFoundError(SportBlurbsError):
    def __init__(self, key, document):
        super().__init__(f"Key '{key}' is not found in document '{document}'.")
