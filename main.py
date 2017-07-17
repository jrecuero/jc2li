#import json
#from pprint import pprint


def itf():
    print 'ITF'


def node():
    print 'NODE'


# jsondata = '''{
#     "interface":
#     {
#         "label": "itf",
#         "cmd": "itf"
#     },
#     "node":
#     {
#         "label": "node",
#         "cmd": "node"
#     }
# }'''


# with open('data.json') as dfile:
#     data = json.load(dfile)
# data = json.loads(jsondata)


# pprint(data)
# for k, v in data.iteritems():
#     eval(v['cmd'])()

argsdata = {'nameid': {'id': {'type': int, 'default': 0},
                       'name': {'type': str, 'default': 'no name'}}}
