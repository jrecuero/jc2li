from commands import Cli
# import os
# from importlib import import_module
import loggerator


if __name__ == '__main__':
    logger = loggerator.getLoggerator('cli')
    logger.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    logger.info("---------------", "RED")

    # directory = 'extended'
    # files = [f[:-3] for f in os.listdir(directory) if ('.py' == f[-3:])]
    # for f in files:
    #     mod = import_module('{}.{}'.format(directory, f))
    #     if getattr(mod, 'TO_EXTEND', None):
    #         Cli.extends(mod.TO_EXTEND)

    cli = Cli()
    try:
        cli.cmdloop('CLI> ')
    except KeyboardInterrupt:
        print("")
        pass
