from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class TranslationRequest(_message.Message):
    __slots__ = ["text", "fromLang", "toLang"]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    FROMLANG_FIELD_NUMBER: _ClassVar[int]
    TOLANG_FIELD_NUMBER: _ClassVar[int]
    text: str
    fromLang: str
    toLang: str
    def __init__(self, text: _Optional[str] = ..., fromLang: _Optional[str] = ..., toLang: _Optional[str] = ...) -> None: ...

class TranslationResponse(_message.Message):
    __slots__ = ["status", "text"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    status: int
    text: str
    def __init__(self, status: _Optional[int] = ..., text: _Optional[str] = ...) -> None: ...
