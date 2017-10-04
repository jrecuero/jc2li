import sys
import loggerator
import argparse
import importlib


if __name__ == '__main__':
    MODULE = 'cli'
    logger = loggerator.getLoggerator(MODULE)
    logger.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    logger.info("---------------", "RED")

    parser = argparse.ArgumentParser(description="CLI application launcher.")
    parser.add_argument('--module', '-M', action='store', help='Module with CLI commands')
    parser.add_argument('--echo', action='store_true', help='Echo mode')
    parser.add_argument('--exception', action='store_true', help='Exception mode')
    args = parser.parse_args()

    if args.module is None:
        sys.exit(0)
    else:
        if args.exception:
            mod = importlib.import_module(args.module)
        else:
            try:
                mod = importlib.import_module(args.module)
            except:
                print('Module {0} not found'.format(args.module))
                sys.exit(0)

    try:
        cli = getattr(mod, mod.MODULE)()
    except AttributeError:
        print("Module {0} don't have MODULE attribute".format(args.module))
        sys.exit(0)
    try:
        cli_kwargs = {'prompt': 'CLI> '}
        cli_kwargs.update(getattr(mod, mod.MODULE_KWARGS))
    except AttributeError:
        pass
    cli.run(**cli_kwargs)
