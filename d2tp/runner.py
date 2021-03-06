from __future__ import annotations

import subprocess
from collections.abc import Iterable
from pathlib import Path, PosixPath, PurePath, PureWindowsPath
from subprocess import CompletedProcess
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Final, overload

from .build import Build
from .game import Game
from .log import Logger

if TYPE_CHECKING:
    from proton import CompatData, Proton, Session


LOG: Final = Logger(__name__)


class Runner:  # pylint: disable=too-many-instance-attributes
    """Proton runner"""

    build: Build
    game: Game
    proton: Proton
    compatdata: CompatData
    session: Session

    def __init__(
        self,
        build: Build,
        game: Game,
    ) -> None:
        LOG.debug("creating Runner")

        self.build = build
        self.game = game
        self.proton, self.compatdata, self.session = self.build.start_session()
        self._wine_bin = PosixPath(self.proton.wine64_bin)
        self._prefix_path = Path(self.compatdata.prefix_dir)
        self._proton_game_path: PureWindowsPath | None = None

        self._prepare()

    def _prepare(self) -> None:
        LOG.debug("preparing")

        game_drive = self._prefix_path.joinpath("dosdevices", "g:")

        if not game_drive.exists():
            game_drive.parent.mkdir(parents=True, exist_ok=True)
            game_drive.symlink_to(self.game.path)

            LOG.trace("  ln -s %s %s", self.game.path, game_drive)

    @property
    def proton_game_path(self) -> PureWindowsPath:
        if self._proton_game_path is None:
            self._proton_game_path = self.wine_path(self.game.path)

        return self._proton_game_path

    @overload
    def wine_path(self, path: str | PurePath) -> PureWindowsPath:
        ...

    @overload
    def wine_path(self, path: str | PurePath, windows: bool) -> PosixPath:
        ...

    def wine_path(
        self,
        path: str | PurePath,
        windows: bool = True,
    ) -> PosixPath | PureWindowsPath:
        cmd = ["winepath"]

        if windows:
            cmd.append("-w")

        cmd.append(str(path))

        process = self.run(*cmd, capture=True)
        wine_path = process.stdout.strip()

        if windows:
            return PureWindowsPath(wine_path)

        return PosixPath(wine_path)

    def native_path(self, path: str | PureWindowsPath) -> PosixPath:
        return self.wine_path(path, windows=False)

    def game_rel_path(self, path: PosixPath) -> PosixPath:
        return path.relative_to(self.game.path)

    def run(
        self,
        *args: str,
        cwd: str | PosixPath | None = None,
        capture: bool = False,
    ) -> CompletedProcess:
        cmd = [str(self._wine_bin), *args]
        env = self.session.env

        debug_cmd(cmd, cwd=cwd, env=env)

        return subprocess.run(
            cmd,
            check=True,
            env=env,
            cwd=cwd,
            encoding="utf-8",
            capture_output=capture,
        )

    def compile(self, *args: str, force: bool = False) -> CompletedProcess:
        cmd = [
            str(self.game.compiler_path),
            "-game",
            str(self.proton_game_path.joinpath("game", "dota")),
        ]

        if force:
            cmd.append("-fshallow")

        return self.run(*cmd, *args, cwd=self.game.path)

    def compile_file(self, path: PosixPath, force: bool = False) -> CompletedProcess:
        return self.compile("-i", str(self.game_rel_path(path)), force=force)

    def compile_filelist(
        self,
        paths: Iterable[PosixPath],
        force: bool = False,
    ) -> CompletedProcess:
        with NamedTemporaryFile(mode="w+", encoding="utf-8") as f:
            f.writelines(f"{self.game_rel_path(p)}\n" for p in paths)
            f.flush()

            filelist_proton_path = self.wine_path(f.name)

            return self.compile("-filelist", str(filelist_proton_path), force=force)

    def compile_custom_game(
        self,
        name: str,
        src_path: str | PosixPath,
        force: bool = False,
    ) -> None:
        custom_game = self.game.custom_game(name, src_path)

        custom_game.setup()

        for path in custom_game.map_files:
            rel_path = path.relative_to(custom_game.src_content_path)
            self.compile_file(custom_game.content_path.joinpath(rel_path), force=force)

        asset_files = [
            custom_game.content_path.joinpath(path.relative_to(custom_game.src_content_path))
            for path in custom_game.asset_files
        ]

        self.compile_filelist(asset_files, force=force)


def debug_cmd(
    cmd: list[str],
    cwd: str | PosixPath | None = None,
    env: dict[str, str] | None = None,  # pylint: disable=unused-argument
) -> None:
    LOG.debug("running %r", cmd)
    LOG.debug("  cwd=%s", cwd)
    LOG.trace("  env=%r", env)
