from __future__ import annotations

import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .version import ProtonVersion

if TYPE_CHECKING:
    from proton import CompatData, Proton, Session  # pylint: disable=import-error

PROTON_MIN_VERSION: Final[ProtonVersion] = ProtonVersion(6, 3, 2)

PROTON_FILES: Final[list[tuple[str, str | None]]] = [
    ("filelock.py", None),
    ("proton", "proton.py"),
    ("proton_dist.tar", None),
    ("version", None),
]

ERRF_PROTON_FILE_NOT_FOUND = "Invalid proton path {path}: file {file} does not exist"
ERRF_PROTON_MIN_VERSION = (
    "Invalid proton path {path}: "
    "required minimum version is {min_version}, path has version {version}"
)


class Build:
    """Proton environment builder"""

    def __init__(self, proton_path: Path, build_path: Path, prefix_path: Path) -> None:
        self.proton_path: Path = proton_path
        self.proton: Proton | None = None
        self.compatdata: CompatData | None = None
        self.session: Session | None = None
        self._proton_version: ProtonVersion | None = None

        self._validate_version()

        self.build_path: Path = build_path / str(self.proton_version)
        self.prefix_path: Path = prefix_path / str(self.proton_version)

        self._validate_files()

    def _validate_files(self) -> None:
        for (src, _) in self.proton_files:
            if not src.exists():
                raise ValueError(
                    ERRF_PROTON_FILE_NOT_FOUND.format(path=self.proton_path, file=src)
                )

    def _validate_version(self) -> None:
        if self.proton_version < PROTON_MIN_VERSION:
            raise ValueError(
                ERRF_PROTON_MIN_VERSION.format(
                    path=self.proton_path,
                    min_version=PROTON_MIN_VERSION,
                    version=self.proton_version,
                )
            )

    def _prepare(self) -> None:
        self.build_path.mkdir(parents=True, exist_ok=True)
        self.prefix_path.mkdir(parents=True, exist_ok=True)

        self.build_path.joinpath("__init__.py").touch()

        for src, dst in self.proton_files:
            if not dst.exists():
                dst.symlink_to(src)

    @property
    def proton_version(self) -> ProtonVersion:
        if self._proton_version is None:
            file = self.proton_path.joinpath("version")
            self._proton_version = ProtonVersion.parse_file(file)

        return self._proton_version

    @property
    def proton_files(self) -> Generator[tuple[Path, Path], None, None]:
        for srcname, dstname in PROTON_FILES:
            if dstname is None:
                dstname = srcname

            src = self.proton_path / srcname
            dst = self.build_path / dstname

            yield src, dst

    def start_session(self) -> tuple[Proton, CompatData, Session]:
        if self.proton and self.compatdata and self.session:
            return self.proton, self.compatdata, self.session

        self._prepare()

        sys.path.insert(0, str(self.build_path))

        import proton  # pylint: disable=import-outside-toplevel,import-error

        proton.g_proton = proton.Proton(str(self.build_path))
        proton.g_compatdata = proton.CompatData(str(self.prefix_path))
        proton.g_session = proton.Session()

        self.proton = proton.g_proton
        self.compatdata = proton.g_compatdata
        self.session = proton.g_session

        if self.proton.need_tarball_extraction():
            self.proton.extract_tarball()

        self.session.init_wine()

        if self.proton.missing_default_prefix():
            self.proton.make_default_prefix()

        self.session.init_session()

        return self.proton, self.compatdata, self.session
