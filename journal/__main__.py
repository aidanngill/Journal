import argparse
import logging

from . import format
from . import modules
from .session import Session

log = logging.getLogger(__name__)

logging.basicConfig(
    format="[%(asctime)s] [%(name)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


def find_all_modules():
    return [m for m in modules.__all__ if issubclass(m, Session)]


def fetch_args():
    parser = argparse.ArgumentParser(description="generate listography entries.")

    # Will simply list possible options then quit.
    parser.add_argument(
        "--list-modules",
        action="store_true",
        default=False,
        help="list all available modules.",
    )
    parser.add_argument(
        "--list-functions",
        action="store_true",
        default=False,
        help="list all available functions for a specific module.",
    )

    # Configuration/authorization elements.
    parser.add_argument(
        "-m", "--module", type=str, help="the module to generate data for."
    )
    parser.add_argument("-u", "--user", type=str, help="the user to generate data for.")
    parser.add_argument(
        "-a",
        "--auth",
        type=str,
        help="authorization token to use for the given module.",
    )
    parser.add_argument(
        "-f",
        "--file",
        type=str,
        help="where to save the output to (will supress stdout).",
    )

    parser.add_argument("functions", nargs="*")

    return parser.parse_args()


def main():
    args = fetch_args()
    mods = find_all_modules()

    if args.list_modules:
        return log.info(", ".join([m.__name__ for m in mods]))

    if not args.module:
        return log.fatal("A module was not provided.")

    func = getattr(modules, args.module)

    if not func:
        return log.fatal("Given module does not exist.")

    client = func()

    if client.needs_authorization and not args.auth:
        return log.fatal("Authentication is necessary for this module.")

    client.set_authorization(args.auth)

    if args.list_functions:
        return log.info(f"{args.module}: {', '.join(func.functions)}")

    functions = [f for f in args.functions if f in client.functions]

    if len(functions) < 1:
        return log.fatal("Invalid functions were given.")

    results = [getattr(client, function)(args.user) for function in functions]
    content = format.content(results, args.user)

    if args.file is not None:
        with open(args.file, "w+", encoding="utf-8") as file:
            file.write(content)
    else:
        print(content)

if __name__ == "__main__":
    main()
