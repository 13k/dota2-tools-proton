from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path
from typing import TYPE_CHECKING, Final

from .log import Logger
from .version import ProtonVersion

if TYPE_CHECKING:
    from proton import CompatData, Proton, Session


LOG: Final = Logger(__name__)

PROTON_MIN_VERSION: Final = ProtonVersion(7, 0, 5, "")

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


class Build:  # pylint: disable=too-many-instance-attributes
    """Proton environment builder"""

    proton: Proton | None
    compatdata: CompatData | None
    session: Session | None
    steam_path: Path
    proton_path: Path
    build_path: Path
    prefix_path: Path

    def __init__(
        self,
        steam_path: Path,
        proton_path: Path,
        build_path: Path,
        prefix_path: Path,
    ) -> None:
        self.steam_path = steam_path
        self.proton_path = proton_path

        LOG.debug("creating Build")
        LOG.debug("  steam_path = %s", self.steam_path)
        LOG.debug("  proton_path = %s", self.proton_path)

        self.proton = None
        self.compatdata = None
        self.session = None
        self._proton_version: ProtonVersion | None = None

        self._validate_version()

        LOG.debug("  found proton version = %s", self.proton_version)

        self.build_path: Path = build_path.joinpath(str(self.proton_version))
        self.prefix_path: Path = prefix_path.joinpath(str(self.proton_version))

        self._validate_files()

        LOG.debug("initialized Build")
        LOG.debug("  build_path = %s", self.build_path)
        LOG.debug("  prefix_path = %s", self.prefix_path)

    def _validate_files(self) -> None:
        for (src, _) in self.proton_files:
            LOG.trace("  checking file %s", src)
            if not src.exists():
                raise ValueError(
                    ERRF_PROTON_FILE_NOT_FOUND.format(path=self.proton_path, file=src)
                )

    def _validate_version(self) -> None:
        LOG.trace(
            "  checking version %s against minimum version %s",
            self.proton_version,
            PROTON_MIN_VERSION,
        )

        if self.proton_version < PROTON_MIN_VERSION:
            raise ValueError(
                ERRF_PROTON_MIN_VERSION.format(
                    path=self.proton_path,
                    min_version=PROTON_MIN_VERSION,
                    version=self.proton_version,
                )
            )

    def _prepare(self) -> None:
        LOG.debug("preparing build")

        steam_path_str = str(self.steam_path)
        os.environ["STEAM_COMPAT_CLIENT_INSTALL_PATH"] = steam_path_str

        LOG.trace("  $STEAM_COMPAT_CLIENT_INSTALL_PATH = %r", steam_path_str)

        self.build_path.mkdir(parents=True, exist_ok=True)

        LOG.trace("  mkdir -p %s", self.build_path)

        self.prefix_path.mkdir(parents=True, exist_ok=True)

        LOG.trace("  mkdir -p %s", self.prefix_path)

        build_pkg_file = self.build_path.joinpath("__init__.py")
        build_pkg_file.touch()

        LOG.trace("  touch %s", build_pkg_file)

        for src, dst in self.proton_files:
            if not dst.exists():
                dst.symlink_to(src)
                LOG.trace("  ln -s %s %s", src, dst)

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

            src = self.proton_path.joinpath(srcname)
            dst = self.build_path.joinpath(dstname)

            yield src, dst

    def start_session(self) -> tuple[Proton, CompatData, Session]:
        if self.proton and self.compatdata and self.session:
            return self.proton, self.compatdata, self.session

        LOG.debug("starting session")

        self._prepare()

        sys.path.insert(0, str(self.build_path))

        LOG.trace("  sys.path = %r", sys.path)

        import proton  # pylint: disable=import-outside-toplevel,import-error

        proton.g_proton = proton.Proton(str(self.build_path))
        proton.g_compatdata = proton.CompatData(str(self.prefix_path))
        proton.g_session = proton.Session()

        self.proton = proton.g_proton

        LOG.debug("  created Proton (base_path = %s)", self.build_path)

        self.compatdata = proton.g_compatdata

        LOG.debug("  created CompatData (base_path = %s)", self.prefix_path)

        self.session = proton.g_session

        LOG.debug("  created Session")

        if self.proton.need_tarball_extraction():
            LOG.debug("  extracting proton tarball")

            self.proton.extract_tarball()

        LOG.debug("  initializing wine")

        self.session.init_wine()

        if self.proton.missing_default_prefix():
            LOG.debug("  creating default prefix")

            self.proton.make_default_prefix()

        LOG.debug("  initializing session")

        self.session.init_session(True)

        return self.proton, self.compatdata, self.session
