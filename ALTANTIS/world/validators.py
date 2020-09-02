from typing import Container, Type, Any, Optional


class Validator:
    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        raise NotImplemented()


class NopValidator(Validator):
    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        return val


class BlankValidator(Validator):
    def __call__(self, val: Optional[Any]) -> str:
        return ""


class TypeValidator(Validator):
    def __init__(self, type_: Type):
        self.type = type_

    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        try:
            return self.type(val)
        except ValueError:
            return None


class LenValidator(Validator):
    def __init__(self, min_: int, max_: int):
        self.min = min_
        self.max = max_

    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        return val if self.min <= len(val) < self.max else None


class RangeValidator(Validator):
    def __init__(self, min_: Optional[Any], max_: Optional[Any]):
        self.min = min_
        self.max = max_

    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        return val if val is not None and self.min <= val < self.max else None


class InValidator(Validator):
    def __init__(self, valid: Container):
        self.valid = valid

    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        return val if val is not None and val in self.valid else None


class BothValidator(Validator):
    def __init__(self, inner: Validator, outer: Validator):
        self.inner = inner
        self.outer = outer

    def __call__(self, val: Optional[Any]) -> Optional[Any]:
        return self.outer(self.inner(val))
