from globus_sdk import GlobusHTTPResponse


class GlobusArrayResponse(GlobusHTTPResponse):
    """
    super-simple response class for data where the top-level JSON entity is an
    Array, so __iter__ can be defined naturally on that array
    """
    def __iter__(self):
        return iter(self.data)
