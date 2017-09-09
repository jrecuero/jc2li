import run

commands = ['start']

cli = run.RunCli()
for cmd in commands:
    cb = cli.getCmdCb(cmd)
    print('calling {0} result is {1}'.format(cmd, cb('')))
