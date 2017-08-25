from commands import CliCommands
# from base import Cli
import loggerator


if __name__ == '__main__':
    logger = loggerator.getLoggerator('cli')
    logger.info("CLI APPLICATION", extended=(('FG', 'BLUE'), ('BG', 'YELLOW'), ))
    logger.info("---------------", "RED")

    cli = CliCommands()
    try:
        cli.cmdloop('CLI> ')
    except KeyboardInterrupt:
        print("")
        pass
