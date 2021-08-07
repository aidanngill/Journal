import argparse

from . import modules
from .format import content
from .session import Session


def find_all_modules():
    return [m for m in modules.__all__ if issubclass(m, Session)]


if __name__ == "__main__":
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

    parser.add_argument("functions", nargs="*")

    args = parser.parse_args()

    mods = find_all_modules()

    if args.list_modules:
        print(", ".join([m.__name__ for m in mods]))
        quit(0)

    func = getattr(modules, args.module)

    if not func:
        print("[x] given module does not exist.")
        quit(1)

    client = func()
    client.set_authorization(args.auth)

    if args.list_functions:
        print(f"{args.module}: {', '.join(func.functions)}")
        quit(0)

    for function in args.functions:
        if not function in client.functions:
            print(f"[x] invalid function `{function}` was provided.")
            quit(1)

    print(
        content(
            [getattr(client, function)(args.user) for function in args.functions],
            args.user,
        )
    )
