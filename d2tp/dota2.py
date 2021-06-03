from __future__ import annotations

from pathlib import PosixPath

from .custom_game import CustomGame


class Dota2:
    def __init__(self, path: str | PosixPath) -> None:
        self.path: PosixPath = PosixPath(path).resolve()
        self.content_path: PosixPath = self.path / "content"
        self.addons_content_path: PosixPath = self.content_path / "dota_addons"
        self.game_path: PosixPath = self.path / "game"
        self.addons_game_path: PosixPath = self.game_path / "dota_addons"
        self.compiler_path: PosixPath = self.game_path / "bin" / "win64" / "resourcecompiler.exe"

    def custom_game(self, name: str, src_path: str | PosixPath) -> CustomGame:
        return CustomGame(self, name, src_path)