from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Final, NamedTuple, Type, TypeVar

ProtonVersionT = TypeVar("ProtonVersionT", bound="ProtonVersion")

VERSION_RE: Final = re.compile(
    r"""
    \A
    (?P<major>\d+)
    \.
    (?P<minor>\d+)
    -
    (?P<prefix_major>\d+)
    (?P<prefix_minor>\w+)?
    \Z
    """,
    re.VERBOSE,
)

ERRF_INVALID_VERSION_FILE: Final = "Invalid proton version file {file}"
ERRF_INVALID_VERSION_STRING: Final = "Invalid proton version string in file {file}: {version!r}"


class ProtonVersion(NamedTuple):
    """Proton version"""

    major: int
    minor: int
    prefix_major: int
    prefix_minor: str

    @classmethod
    def parse(cls: Type[ProtonVersionT], value: str | Any) -> ProtonVersionT | None:
        if not isinstance(value, str):
            return None

        match = VERSION_RE.match(value)

        if match is None:
            return None

        groups = match.groupdict()
        major = int(groups["major"])
        minor = int(groups["minor"])
        prefix_major = int(groups["prefix_major"])
        prefix_minor = "" if groups["prefix_minor"] is None else groups["prefix_minor"]

        return cls(
            major=major,
            minor=minor,
            prefix_major=prefix_major,
            prefix_minor=prefix_minor,
        )

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
        return "{0.major}.{0.minor}-{0.prefix_major}{0.prefix_minor}".format(self)
