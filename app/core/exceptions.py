from dataclasses import dataclass


@dataclass(frozen=True)
class AppError(Exception):
    message: str


class CustomerNotFoundError(AppError):
    pass


class DuplicateEmailError(AppError):
    pass
