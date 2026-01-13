from assassyn.frontend import *

class CQueT(DType):
    '''Cyclic queue'''

    def __init__(self, dep: int, tp: DType):
        self._cap = 1 << dep
        self._dep = dep
        super().__init__(tp.bits() * self._cap + self._dep * 2)
        self._tp = tp
        self._sz = 0

    @property
    def cap(self):
        '''The capacity of the queue'''
        return self._cap

class CQue:
    def __init__(self, dep: int, tp: DType):
        super().__init__()
        self.dtype = CQueT(dep, tp)
        self.q = RegArray(self.dtype, self.dtype.cap)

    def __getitem__(self, idx: Value):
        pass

