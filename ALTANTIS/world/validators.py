from typing import Container, Type, TypeVar


class Validator:
    def __call__(self, val) -> bool:
        raise NotImplemented()


class NopValidator(Validator):
    def __call__(self, val) -> bool:
        return True


class BlankValidator(Validator):
    def __call__(self, val) -> bool:
        return val == "" or val is None


class TypeValidator(Validator):
    def __init__(self, type_: Type):
        self.type = type_

    def __call__(self, val) -> bool:
        return isinstance(val, self.type)


class LenValidator(Validator):
    def __init__(self, min_: int, max_: int):
        self.min = min_
        self.max = max_

    def __call__(self, val) -> bool:
        return self.min <= len(val) < self.max


class RangeValidator(Validator):
    # I've not added typing as min_ and max_ can be any comparable type to val,
    # and I can't get it to use the same generic T over both functions...
    def __init__(self, min_, max_):
        self.min = min_
        self.max = max_

    def __call__(self, val) -> bool:
        return self.min <= val < self.max


class InValidator(Validator):
    def __init__(self, valid: Container):
        self.valid = valid

    def __call__(self, val) -> bool:
        return val in self.valid


class BothValidator(Validator):
    def __init__(self, val1: Validator, val2: Validator):
        self.val1 = val1
        self.val2 = val2

    def __call__(self, val) -> bool:
        return self.val1(val) and self.val2(val)
