from __future__ import annotations

import argparse
import sys
from pathlib import Path, PosixPath
from typing import Final, NoReturn

from appdirs import AppDirs

from . import APP_NAME, __version__
from .build import Build
from .dota2 import Dota2
from .runner import Runner

COMMANDS: Final[dict[str, str]] = {
    "run": "Run a command within Proton's environment",
    "compile": "Run the Dota 2 Workshop Tools resource compiler",
    "compile_custom_game": "Compile a custom game using the resource compiler",
    "protonpath": "Converts a native path to Proton path",
    "nativepath": "Converts a Proton path to native path",
}

APP_DIRS = AppDirs(appname=APP_NAME)

DEFAULT_BUILD_PATH: Final[Path] = Path(APP_DIRS.user_cache_dir) / "build"
DEFAULT_WINE_PREFIX_PATH: Final[Path] = Path(APP_DIRS.user_cache_dir) / "prefix"


def log(*args: str) -> None:
    print(*args, file=sys.stderr, flush=True)


def commands_help() -> str:
    max_cmd_len = max([len(cmd) for cmd in COMMANDS])
    lines = [
        "  {}{}".format(cmd.ljust(max_cmd_len + 4), cmd_help)
        for cmd, cmd_help in COMMANDS.items()
    ]

    return "commands:\n{}".format("\n".join(lines))


def epilog() -> str:
    return commands_help()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog=APP_NAME,
        description="Run tools from Dota 2's Workshop Tools using Proton",
        epilog=epilog(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    parser.add_argument(
        "--proton",
        "-p",
        type=str,
        required=True,
        dest="proton_path",
        help="Proton path",
        metavar="PATH",
    )

    parser.add_argument(
        "--game",
        "-g",
        type=str,
        required=True,
        dest="game_path",
        help="Dota 2 path",
        metavar="PATH",
    )

    parser.add_argument(
        "--build",
        "-b",
        type=str,
        dest="build_path",
        default=str(DEFAULT_BUILD_PATH),
        help="Build path [default: %(default)s]",
        metavar="PATH",
    )

    parser.add_argument(
        "--prefix",
        "-w",
        type=str,
        dest="prefix_path",
        default=str(DEFAULT_WINE_PREFIX_PATH),
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
        "--debug",
        "-D",
        action="store_true",
        dest="debug",
        default=False,
        help="Enable debugging [default: %(default)s]",
    )

    parser.add_argument("cmd", type=str, help="Command")
    parser.add_argument("cmd_args", type=str, nargs="*", help="Command arguments")

    return parser.parse_args()


def main() -> NoReturn:
    """d2tp entrypoint"""

    args = parse_args()

    if args.cmd not in COMMANDS:
        log(f"Invalid command {args.cmd}")
        sys.exit(1)

    proton_path = Path(args.proton_path).resolve()
    game_path = PosixPath(args.game_path).resolve()
    build_path = Path(args.build_path).resolve()
    prefix_path = Path(args.prefix_path).resolve()

    build = Build(
        proton_path=proton_path,
        build_path=build_path,
        prefix_path=prefix_path,
    )

    dota2 = Dota2(game_path)
    runner = Runner(build=build, game=dota2, debug=args.debug)

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
