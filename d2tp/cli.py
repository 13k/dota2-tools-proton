from __future__ import annotations

import argparse
import sys
from pathlib import Path, PosixPath
from typing import Final, NoReturn

from appdirs import AppDirs

from . import APP_NAME
from . import LOG as APP_LOG
from . import __version__
from .build import PROTON_MIN_VERSION, Build
from .game import Game
from .log import Level, Logger
from .runner import Runner

LOG: Final = Logger(__name__)

COMMANDS: Final[dict[str, str]] = {
    "run": "Run a command within Proton's environment",
    "compile": "Run the Dota 2 Workshop Tools resource compiler",
    "compile_custom_game": "Compile a custom game using the resource compiler",
    "protonpath": "Converts a native path to Proton path",
    "nativepath": "Converts a Proton path to native path",
}

APP_DIRS: Final = AppDirs(appname=APP_NAME)

DEFAULT_BUILD_PATH: Final = Path(APP_DIRS.user_cache_dir).joinpath("build")
DEFAULT_PREFIX_PATH: Final = Path(APP_DIRS.user_cache_dir).joinpath("prefix")


def epilog() -> str:
    max_cmd_len = max([len(cmd) for cmd in COMMANDS])
    width = max_cmd_len + 4
    lines = [f"  {cmd:{width}}{cmd_help}" for cmd, cmd_help in COMMANDS.items()]
    help_text = "\n".join(lines)

    return f"commands:\n{help_text}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Run tools from Dota 2's Workshop Tools using Proton",
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.add_argument(
        "--steam-path",
        "-s",
        type=str,
        required=True,
        dest="steam_path",
        help="Steam path",
        metavar="PATH",
    )

    parser.add_argument(
        "--proton-path",
        "-p",
        type=str,
        dest="proton_path",
        help="Proton path",
        metavar="PATH",
    )

    parser.add_argument(
        "--game-path",
        "-g",
        type=str,
        required=True,
        dest="game_path",
        help="Dota 2 path",
        metavar="PATH",
    )

    parser.add_argument(
        "--build-path",
        "-b",
        type=str,
        dest="build_path",
        default=str(DEFAULT_BUILD_PATH),
        help="Build path [default: %(default)s]",
        metavar="PATH",
    )

    parser.add_argument(
        "--prefix-path",
        "-w",
        type=str,
        dest="prefix_path",
        default=str(DEFAULT_PREFIX_PATH),
        help="Wine prefix path [default: %(default)s]",
        metavar="PATH",
    )

    parser.add_argument(
        "--force",
        "-f",
        action="store_true",
        dest="force",
        default=False,
        help="Force resource compilation [default: %(default)s]",
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="count",
        dest="verbosity",
        default=0,
        help="Be verbose (can be given multiple times to increase verbosity)",
    )

    parser.add_argument("cmd", type=str, help="Command")
    parser.add_argument("cmd_args", type=str, nargs="*", help="Command arguments")

    return parser.parse_args()


def resolve_proton_path(steam_path, value=None):
    if value is None:
        min_version = f"{PROTON_MIN_VERSION.major}.{PROTON_MIN_VERSION.minor}"
        return steam_path.joinpath("steamapps", "common", f"Proton {min_version}")

    return PosixPath(value).resolve()


def validate_path(path: Path) -> None:
    if not path.exists():
        raise ValueError(f"Path {path} not found")


def main() -> NoReturn:
    """d2tp entrypoint"""

    args = parse_args()

    if args.cmd not in COMMANDS:
        LOG.error("Invalid command %s", args.cmd)
        sys.exit(1)

    if args.verbosity >= 3:
        APP_LOG.setLevel(Level.TRACE)
    elif args.verbosity == 2:
        APP_LOG.setLevel(Level.DEBUG)
    elif args.verbosity == 1:
        APP_LOG.setLevel(Level.INFO)

    steam_path = PosixPath(args.steam_path).resolve()
    proton_path = resolve_proton_path(steam_path, args.proton_path)
    game_path = PosixPath(args.game_path).resolve()
    build_path = PosixPath(args.build_path).resolve()
    prefix_path = PosixPath(args.prefix_path).resolve()

    validate_path(steam_path)
    validate_path(proton_path)
    validate_path(game_path)

    build = Build(
        steam_path=steam_path,
        proton_path=proton_path,
        build_path=build_path,
        prefix_path=prefix_path,
    )

    game = Game(path=game_path)
    runner = Runner(build=build, game=game)

    if args.cmd == "run":
        runner.run(*args.cmd_args)
    elif args.cmd == "compile":
        runner.compile(*args.cmd_args, force=args.force)
    elif args.cmd == "compile_custom_game":
        name, src_path = args.cmd_args
        runner.compile_custom_game(name, src_path, force=args.force)
    elif args.cmd == "protonpath":
        print(runner.wine_path(args.cmd_args[0]))
    elif args.cmd == "nativepath":
        print(runner.native_path(args.cmd_args[0]).resolve())

    sys.exit(0)
