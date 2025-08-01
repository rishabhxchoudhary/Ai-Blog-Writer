"""
This type stub file was generated by pyright.
"""

__all__ = ('PostgresError', 'FatalPostgresError', 'UnknownPostgresError', 'InterfaceError', 'InterfaceWarning', 'PostgresLogMessage', 'ClientConfigurationError', 'InternalClientError', 'OutdatedSchemaCacheError', 'ProtocolError', 'UnsupportedClientFeatureError', 'TargetServerAttributeNotMatched', 'UnsupportedServerFeatureError')
class PostgresMessageMeta(type):
    _message_map = ...
    _field_map = ...
    def __new__(mcls, name, bases, dct): # -> Self:
        ...
    
    @classmethod
    def get_message_class_for_sqlstate(mcls, code):
        ...
    


class PostgresMessage(metaclass=PostgresMessageMeta):
    def as_dict(self): # -> dict[Any, Any]:
        ...
    


class PostgresError(PostgresMessage, Exception):
    """Base class for all Postgres errors."""
    def __str__(self) -> str:
        ...
    
    @classmethod
    def new(cls, fields, query=...): # -> Any:
        ...
    


class FatalPostgresError(PostgresError):
    """A fatal error that should result in server disconnection."""
    ...


class UnknownPostgresError(FatalPostgresError):
    """An error with an unknown SQLSTATE code."""
    ...


class InterfaceMessage:
    def __init__(self, *, detail=..., hint=...) -> None:
        ...
    
    def __str__(self) -> str:
        ...
    


class InterfaceError(InterfaceMessage, Exception):
    """An error caused by improper use of asyncpg API."""
    def __init__(self, msg, *, detail=..., hint=...) -> None:
        ...
    
    def with_msg(self, msg): # -> Self:
        ...
    


class ClientConfigurationError(InterfaceError, ValueError):
    """An error caused by improper client configuration."""
    ...


class DataError(InterfaceError, ValueError):
    """An error caused by invalid query input."""
    ...


class UnsupportedClientFeatureError(InterfaceError):
    """Requested feature is unsupported by asyncpg."""
    ...


class UnsupportedServerFeatureError(InterfaceError):
    """Requested feature is unsupported by PostgreSQL server."""
    ...


class InterfaceWarning(InterfaceMessage, UserWarning):
    """A warning caused by an improper use of asyncpg API."""
    def __init__(self, msg, *, detail=..., hint=...) -> None:
        ...
    


class InternalClientError(Exception):
    """All unexpected errors not classified otherwise."""
    ...


class ProtocolError(InternalClientError):
    """Unexpected condition in the handling of PostgreSQL protocol input."""
    ...


class TargetServerAttributeNotMatched(InternalClientError):
    """Could not find a host that satisfies the target attribute requirement"""
    ...


class OutdatedSchemaCacheError(InternalClientError):
    """A value decoding error caused by a schema change before row fetching."""
    def __init__(self, msg, *, schema=..., data_type=..., position=...) -> None:
        ...
    


class PostgresLogMessage(PostgresMessage):
    """A base class for non-error server messages."""
    def __str__(self) -> str:
        ...
    
    def __setattr__(self, name, val):
        ...
    
    @classmethod
    def new(cls, fields, query=...): # -> BaseException | PostgresWarning | Warning | PostgresLogMessage | Any:
        ...
    


