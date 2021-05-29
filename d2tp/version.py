from __future__ import annotations

from pathlib import Path
from typing import Any, Final, NamedTuple, Type, TypeVar

ProtonVersionT = TypeVar("ProtonVersionT", bound="ProtonVersion")

ERRF_INVALID_VERSION_FILE: Final = "Invalid proton version file {file}"
ERRF_INVALID_VERSION_STRING: Final = "Invalid proton version string in file {file}: {version!r}"


class ProtonVersion(NamedTuple):
    """Proton version"""

    major: int
    minor: int
    prefix: int

    @classmethod
    def parse(cls: Type[ProtonVersionT], value: str | Any) -> ProtonVersionT | None:
        if not isinstance(value, str):
            return None

        if "-" not in value:
            return None

        if "." not in value:
            return None

        proton, prefix = value.split("-", 1)
        major, minor = proton.split(".", 1)

        return cls(int(major), int(minor), int(prefix))

    @classmethod
    def parse_file(cls: Type[ProtonVersionT], file: Path) -> ProtonVersionT:
        lines = file.read_text(encoding="utf-8").splitlines()

        if len(lines) != 1:
            raise ValueError(ERRF_INVALID_VERSION_FILE.format(file=file))

        _, vstr = lines[0].split(" ", 1)
        version = cls.parse(vstr.removeprefix("proton-"))

        if version is None:
            raise ValueError(ERRF_INVALID_VERSION_STRING.format(file=file, version=lines[0]))

        return version

    def __str__(self) -> str:
        # pylint: disable=missing-format-attribute
        return "{0.major}.{0.minor}-{0.prefix}".format(self)
        # pylint: enable=missing-format-attribute
