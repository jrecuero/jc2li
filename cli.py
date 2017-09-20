import sys
import loggerator
import argparse
import importlib


if __name__ == '__main__':
    logger = loggerator.getLoggerator('cli')
    logger.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    logger.info("---------------", "RED")

    parser = argparse.ArgumentParser(description="CLI application launcher.")
    parser.add_argument('--module', '-M', action='store', help='Module with CLI commands')
    parser.add_argument('--echo', action='store_true', help='Echo mode')
    args = parser.parse_args()

    if args.module is None:
        sys.exit(0)
    else:
        try:
            mod = importlib.import_module(args.module)
        except:
            print ('Module {0} not found'.format(args.module))
            sys.exit(0)

    cli = mod.CliCommands()
    try:
        cli.cmdloop(thePrompt='CLI> ')
    except KeyboardInterrupt:
        print("")
        pass
