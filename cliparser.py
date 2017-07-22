import pyparsing as pp


def procTokens(tokens, withEnd=True):
    rules, counter = [], 0
    for tok in tokens:
        toktype = type(tok)
        if tok == '|':
            counter = 0
            continue
        elif toktype == str:
            rules.append({'counter': counter, 'type': '1', 'args': tok})
        elif toktype == list and len(tok) == 1:
            rules.append({'counter': counter, 'type': '1', 'args': tok[0]})
        elif toktype in [pp.ParseResults, list]:
            tok = tok.asList()[0] if toktype == pp.ParseResults else tok
            op = tok[-1]
            if type(op) == str and op in '?+*':
                tok.pop()
            else:
                op = '1'
            rules.append({'counter': counter, 'type': op, 'args': procTokens(tok, False)})
        else:
            print 'Invalid Syntax'
        counter += 1
    if withEnd:
        rules.append({'counter': counter, 'type': '0', 'args': None})
    return rules


def procSyntax(tokens):
    command = tokens[0]
    rules = procTokens(tokens[1:])
    return command, rules


def procRules(cmd, rules, line):
    index = 0
    for k, v in rules.iteritems():
        if v == '1':
            pass
        elif v == '?':
            pass
        elif v == '*':
            pass
        elif v == '+':
            pass
        elif v == '0':
            pass
        else:
            pass
        index += 1


def getSyntax():
    command = pp.Word(pp.alphanums).setName('command')
    posarg = pp.Word(pp.alphanums).setName('pos-arg')

    lbracket = pp.Suppress("[")
    rbracket = pp.Suppress("]")
    zooarg = pp.Word(pp.alphanums).setName('zero-or-one-arg')
    zomarg = pp.Word(pp.alphanums).setName('zero-or-more-arg')
    oomarg = pp.Word(pp.alphanums).setName('one-or-more-arg')

    zeroorone = pp.Forward()
    zeroorone.setName('zero-or-one')
    zeroorone << pp.Group(lbracket + pp.ZeroOrMore(zooarg) + pp.ZeroOrMore(("|"  + pp.OneOrMore(zooarg | zeroorone)) | pp.OneOrMore(zeroorone)) + rbracket + "?")

    zeroormore = pp.Forward()
    zeroormore << pp.Group(lbracket + pp.ZeroOrMore(zomarg) + pp.ZeroOrMore(("|"  + pp.OneOrMore(zomarg | zeroormore)) | pp.OneOrMore(zeroormore)) + rbracket + "*")
    zeroormore.setResultsName('zero-or-more')

    oneormore = pp.Forward()
    oneormore << pp.Group(lbracket + pp.ZeroOrMore(oomarg) + pp.ZeroOrMore(("|"  + pp.OneOrMore(oomarg | oneormore)) | pp.OneOrMore(oneormore)) + rbracket + "+")
    oneormore.setName('one-or-more')

    syntax = command + pp.ZeroOrMore(posarg) + pp.ZeroOrMore(pp.Group(zeroorone | zeroormore | oneormore))
    return (syntax + pp.stringEnd)


def processSyntax(syntax):
    toks = getSyntax().parseString(syntax)
    cmd, rules = procSyntax(toks)
    return cmd, rules


if __name__ == '__main__':
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [t1|t2]? [t3|t4]* [t10]? [t5|t6]+")
    # toks = (syntax + pp.stringEnd).parseString("tenant tpos1 [tzoo1 | tzoo2 tzoo3 [ tzoo31 ]? ]? [tzom1]* [toom1]+")
    # toks = (syntax + pp.stringEnd).parseString("tenant tpos1 [tzoo1 | tzoo2 tzoo3 [tzoo31 | tzoo32 | tzoo33]? ]? [tzom1]* [toom1]+")

    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tsignature]? [talias]* [tdesc | thelp]+ [tclose]?")
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tdesc talias | tsignature | tuser [tuname | tuid]? ]?")
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tuid [tlastname | tpassport]? ]? [thelp | tdesc]* [tsignature]+")
    toks = getSyntax().parseString("tenant t1 [t2 | t3]?")

    print toks
    cmd, rules = procSyntax(toks)
    print cmd
    for rule in rules:
        print rule
