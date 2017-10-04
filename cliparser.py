import pyparsing as pp


def _map_parent_type_to_op(parent_type):
    """Provide the operation type to use given the parent type for the rule.

    Rule for free-form parameters set the type to '3', parent has a rule
    type '@'.

    Rule for required parameters set the type to '1'.

    Args:
        parent_type (str) : Character with the parent type rule.

    Returns:
        str : Character with the operation type to be used.
    """
    if not parent_type:
        return '1'
    elif parent_type == '@':
        return '3'
    elif parent_type in '?+*!':
        return '4'
    else:
        return '1'


def process_tokens(tokens, withend=True, parent_type=None):
    """Function that process given tokens.

    Rule types are:

        - '1' : Required parameter. Default value shoudl be always None.

        - '2' : Constant parameter. It can be required or optional. From '<x>'
          syntax.

        - '3' : Free-for parameter from '@' syntax. Required.

        - '?' : zero or one parameters. Always optional.

        - '*' : zero or more parameters. Always optional.

        - '+' : one or more parameters. Always optional.

        - '!' : one optional parameter. Required.

    Args:
        tokens (list): list of tokens to parse.
        withend (boolean): True if last rule has to be added at the end,
        False else.

    Returns:
        list: list of dictionaries with all rules.
    """
    rules, counter = [], 0
    for tok in tokens:
        toktype = type(tok)
        op = _map_parent_type_to_op(parent_type)
        if tok == '|':
            counter = 0
            continue
        elif toktype == str:
            # rule for constant parameters set the type to '2'
            if tok.startswith('<') and tok.endswith('>'):
                rules.append({'counter': counter, 'type': '2', 'args': tok[1:-1]})
            else:
                rules.append({'counter': counter, 'type': op, 'args': tok})
        elif toktype == list and len(tok) == 1:
            rules.append({'counter': counter, 'type': op, 'args': tok[0]})
        elif toktype in [pp.ParseResults, list]:
            tok = tok.asList()[0] if toktype == pp.ParseResults else tok
            op = tok[-1]
            if type(op) == str and op in '?+*!@':
                tok.pop()
            else:
                op = '1'
            rules.append({'counter': counter, 'type': op, 'args': process_tokens(tok, False, op)})
        else:
            print('Invalid Syntax')
        counter += 1
    if withend:
        rules.append({'counter': counter, 'type': '0', 'args': None})
    return rules


def _process_syntax(tokens):
    """Function that process a syntas for the given tokens.

    Args:
        tokens (list): list of tokens to parse.

    Returns:
        tuple: pair with the commadn and a list of dictionaries with all rules.
    """
    command = tokens[0]
    rules = process_tokens(tokens[1:])
    return command, rules


def get_syntax():
    """Function that return the syntax to be used for processing.

    Returns:
        object: syntax used for parsing.
    """
    command = pp.Word(pp.alphanums + "-").setName('command')
    posarg = pp.Word(pp.alphanums + "-<>").setName('pos-arg')

    lbracket = pp.Suppress("[")
    rbracket = pp.Suppress("]")
    zeroorone_flag = "?"
    zeroormore_flag = "*"
    oneormore_flag = "+"
    only1opt_flag = "!"
    freeform_flag = "@"
    zooarg = pp.Word(pp.alphanums + "-").setName('zero-or-one-arg')
    zomarg = pp.Word(pp.alphanums + "-").setName('zero-or-more-arg')
    oomarg = pp.Word(pp.alphanums + "-").setName('one-or-more-arg')
    oooarg = pp.Word(pp.alphanums + "-<>").setName('only-one-arg')
    frearg = pp.Word(pp.alphanums + "-").setName('free-form-arg')

    zeroorone = pp.Forward()
    zeroorone.setName('zero-or-one')
    zeroorone_block = pp.ZeroOrMore(("|"  + pp.OneOrMore(zooarg | zeroorone)) | pp.OneOrMore(zeroorone))
    zeroorone << pp.Group(lbracket + pp.ZeroOrMore(zooarg) + zeroorone_block + rbracket + zeroorone_flag)

    zeroormore = pp.Forward()
    zeroormore_block = pp.ZeroOrMore(("|"  + pp.OneOrMore(zomarg | zeroormore)) | pp.OneOrMore(zeroormore))
    zeroormore << pp.Group(lbracket + pp.ZeroOrMore(zomarg) + zeroormore_block + rbracket + zeroormore_flag)
    zeroormore.setResultsName('zero-or-more')

    oneormore = pp.Forward()
    oneormore_block = pp.ZeroOrMore(("|"  + pp.OneOrMore(oomarg | oneormore)) | pp.OneOrMore(oneormore))
    oneormore << pp.Group(lbracket + pp.ZeroOrMore(oomarg) + oneormore_block + rbracket + oneormore_flag)
    oneormore.setName('one-or-more')

    only1opt = pp.Forward()
    only1opt_block = pp.ZeroOrMore(("|"  + pp.OneOrMore(oooarg | only1opt)) | pp.OneOrMore(only1opt))
    only1opt << pp.Group(lbracket + pp.ZeroOrMore(oooarg) + only1opt_block + rbracket + only1opt_flag)
    only1opt.setName('one-or-more')

    freeform = pp.Forward()
    freeform_block = pp.ZeroOrMore(("|"  + pp.OneOrMore(frearg | freeform)) | pp.OneOrMore(freeform))
    freeform << pp.Group(lbracket + pp.ZeroOrMore(frearg) + freeform_block + rbracket + freeform_flag)
    freeform.setName('zero-or-one')

    options = pp.ZeroOrMore(pp.Group(zeroorone | zeroormore | oneormore | only1opt | freeform))
    syntax = command + pp.ZeroOrMore(posarg) + options
    return (syntax + pp.stringEnd)


def process_syntax(syntax):
    """
    """
    toks = get_syntax().parseString(syntax)
    cmd, rules = _process_syntax(toks)
    return cmd, rules


if __name__ == '__main__':
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [t1|t2]? [t3|t4]* [t10]? [t5|t6]+")
    # toks = (syntax + pp.stringEnd).parseString("tenant tpos1 [tzoo1 | tzoo2 tzoo3 [ tzoo31 ]? ]? [tzom1]* [toom1]+")
    # toks = (syntax + pp.stringEnd).parseString("tenant tpos1 [tzoo1 | tzoo2 tzoo3 [tzoo31 | tzoo32 | tzoo33]? ]? [tzom1]* [toom1]+")

    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tsignature]? [talias]* [tdesc | thelp]+ [tclose]?")
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tdesc talias | tsignature | tuser [tuname | tuid]? ]?")
    # toks = (syntax + pp.stringEnd).parseString("tenant tname [tid | tuid [tlastname | tpassport]? ]? [thelp | tdesc]* [tsignature]+")
    # toks = get_syntax().parseString("tenant t1 [<t2> | t3]!")
    # toks = get_syntax().parseString("tenant t1 <t2>")
    # toks = get_syntax().parseString("tenant [t1 t2 t3]+")
    # toks = get_syntax().parseString("tenant t1 [t2]@")
    toks = get_syntax().parseString("tenant t1 [t2 | t3]*")

    print(toks)
    cmd, rules = _process_syntax(toks)
    print(cmd)
    for rule in rules:
        print(rule)
