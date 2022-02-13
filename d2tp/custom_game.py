from __future__ import annotations

from collections.abc import Generator
from pathlib import PosixPath
from typing import TYPE_CHECKING, TypedDict

import vdf

if TYPE_CHECKING:
    from .dota2 import Dota2

ERRF_INVALID_ADDONINFO_FILE = "Invalid addoninfo file {file}: missing addon name key {name}"


class CustomGame:  # pylint: disable=too-many-instance-attributes
    def __init__(self, game: Dota2, name: str, src_path: str | PosixPath) -> None:
        self.game: Dota2 = game
        self.name: str = name
        self.src_path: PosixPath = PosixPath(src_path).resolve()
        self.src_content_path: PosixPath = self.src_path.joinpath("content")
        self.src_game_path: PosixPath = self.src_path.joinpath("game")
        self.addoninfo_file: PosixPath = self.src_game_path.joinpath("addoninfo.txt")
        self.content_path: PosixPath = self.game.addons_content_path.joinpath(self.name)
        self.game_path: PosixPath = self.game.addons_game_path.joinpath(self.name)
        self._addoninfo: AddonInfo | None = None
        self._maps_glob: str = str(PosixPath("**", "*.vmap"))
        self._assets_glob: str = str(PosixPath("**", "*"))

    @property
    def addoninfo(self) -> AddonInfo:
        if self._addoninfo is not None:
            return self._addoninfo

        data = self.addoninfo_file.read_text(encoding="utf-8")
        addoninfo_kv = vdf.loads(data)

        if self.name not in addoninfo_kv:
            raise ValueError(
                ERRF_INVALID_ADDONINFO_FILE.format(file=self.addoninfo_file, name=self.name)
            )

        self._addoninfo = addon_info(addoninfo_kv[self.name])

        return self._addoninfo

    @property
    def map_files(self) -> Generator[PosixPath, None, None]:
        for path in self.src_content_path.glob(self._maps_glob):
            if path.is_dir():
                continue

            yield path

    @property
    def asset_files(self) -> Generator[PosixPath, None, None]:
        for path in self.src_content_path.glob(self._assets_glob):
            if path.is_dir():
                continue

            if not path.match(self._maps_glob):
                yield path

    def setup(self) -> None:
        if self.content_path.exists():
            if self.content_path.is_symlink():
                self.content_path.unlink()
            else:
                raise ValueError(
                    "Custom game directory already exists in dota's 'content' directory"
                )

        if self.game_path.exists():
            if self.game_path.is_symlink():
                self.game_path.unlink()
            else:
                raise ValueError(
                    "Custom game directory already exists in dota's 'game' directory"
                )

        self.content_path.symlink_to(self.src_content_path)
        self.game_path.symlink_to(self.src_game_path)


class AddonInfo(TypedDict):
    maps: dict[str, AddonInfoMap]
    is_playable: bool
    team_count: int


def addon_info(custom_game_kv: dict) -> AddonInfo:
    map_names = custom_game_kv["maps"].split(" ")

    return dict(
        maps=addon_info_maps(custom_game_kv, map_names),
        is_playable=custom_game_kv.get("IsPlayable", "1") == "1",
        team_count=int(custom_game_kv.get("TeamCount", "2")),
    )


class AddonInfoMap(TypedDict, total=False):
    max_players: int


def addon_info_maps(custom_game_kv: dict, map_names: list[str]) -> dict[str, AddonInfoMap]:
    return {map_name: addon_info_map(custom_game_kv.get(map_name)) for map_name in map_names}


def addon_info_map(map_info_kv: dict | None) -> AddonInfoMap:
    if map_info_kv is None:
        return {}

    map_info: AddonInfoMap = {}

    if "MaxPlayers" in map_info_kv:
        map_info["max_players"] = int(map_info_kv["MaxPlayers"])

    return map_info
