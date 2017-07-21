class Argo(object):

    def __init__(self, theArgo):
        self._argo = theArgo

    @property
    def argo(self):
        return self._argo

    @property
    def name(self):
        return self.argo['name'] if self.argo else None

    @property
    def type(self):
        return self.argo['type'] if self.argo else None

    @property
    def default(self):
        return self.argo['default'] if self.argo else None


if __name__ == '__main__':
    pass
