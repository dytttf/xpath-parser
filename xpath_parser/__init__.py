# coding:utf8
"""
Xpath Expression parser
"""
import re


class InValidXpath(ValueError):
    pass


# regex pattern
function_pattern = re.compile("^(?P<name>[a-zA-Z\-]+)\(")
axis_pattern = re.compile("^(?P<name>[a-zA-Z\-]+)::")
attribute_pattern = re.compile("^@(?P<name>.*)$")


def parse_groups(expression: str, flag: str = "()") -> list:
    """
    >>> parse_groups("(1)(2)")
    [(0, 2), (3, 5)]
    >>> parse_groups("((1)(2))")
    [(0, 7), (1, 3), (4, 6)]
    >>> parse_groups("'1'2'3'", flag="''")
    [(0, 2), (4, 6)]

    :param expression:
    :param flag:
    :return:
    """
    brackets = []
    _brackets = []
    # TODO  support """1'2'34"5"6'7'7"""
    if flag[0] == flag[1]:
        for _idx, s in enumerate(expression):
            if s == flag[0] and not _brackets:
                _brackets.append(_idx)
            elif s == flag[0]:
                brackets.append((_brackets.pop(-1), _idx))
    else:
        for _idx, s in enumerate(expression):
            if s == flag[0]:
                _brackets.append(_idx)
            elif s == flag[1]:
                brackets.append((_brackets.pop(-1), _idx))
    brackets.sort(key=lambda x: x[0])
    return brackets


# TODO typing
class XpathNode(object):
    """
    >>> node = XpathNode("/text()")
    >>> node.name
    'text'

    """

    def __init__(self, expression):
        """
        :param expression:
        """
        self._expression = expression
        #
        self._parse_result = self.parse(self._expression)
        self.name = self._parse_result["name"]
        self.type = self._parse_result["type"]
        self.attrs = self._parse_result["attrs"]
        self.ignore_position = self._parse_result["attrs"]

    def __repr__(self):
        """
        >>> print(XpathNode("/text()"))
        <XpathNode(function): /text() >

        :return:
        """
        return "<XpathNode({}): {} >".format(self.type, self._expression)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def parse(cls, expression: str) -> dict:
        """
        >>> XpathNode.parse("/text()")["name"]
        'text'
        >>> XpathNode.parse("/text()")["type"]
        'function'
        >>> XpathNode.parse("/div[@id='abc']")["name"]
        'div'
        >>> XpathNode.parse("/div[@id='abc']")["type"]
        'element'
        >>> XpathNode.parse("//div[@id='abc']")["ignore_position"]
        True
        >>> XpathNode.parse("/div[@id='abc']")["ignore_position"]
        False
        >>> XpathNode.parse("/child::*")["name"]
        'child'
        >>> XpathNode.parse("/child::*")["type"]
        'axis'
        >>> XpathNode.parse("/@href")["name"]
        'href'
        >>> XpathNode.parse("/@href")["type"]
        'attr'
        >>> XpathNode.parse("/..")["type"]
        'relative'

        :param expression:
        :return:
            {
                "name": "node name",
                "type": "function or element or axis or attr",
                "attrs": "list of @...",
                "ignore_position": True or False,
            }

        """
        _expression = expression.strip().lstrip(".").rstrip("/")
        if not _expression.startswith("/"):
            raise InValidXpath(expression)
        #
        node_type = ""
        name = ""
        attrs = []
        ignore_position = _expression.startswith("//")
        #
        _expression = _expression.strip("/")

        # detect type
        m = function_pattern.search(_expression)
        if m:
            node_type = "function"
            name = m.groupdict()["name"]

        if not node_type:
            m = axis_pattern.search(_expression)
            if m:
                node_type = "axis"
                name = m.groupdict()["name"]
        if not node_type:
            m = attribute_pattern.search(_expression)
            if m:
                node_type = "attr"
                name = m.groupdict()["name"]
        if not node_type:
            if _expression == "..":
                node_type = "relative"
                name = ""
        if not node_type:
            node_type = "element"
            attrs = _expression.replace("]", "").split("[")
            name = attrs[0]
            attrs = attrs[1:]

        result = {
            "name": name,
            "type": node_type,
            "attrs": attrs,
            "ignore_position": ignore_position,
        }
        return result


class XpathExpression(object):
    def __init__(self, expression, index=0):
        """
        >>> parser = XpathExpression("//div[@class='content']/p")
        >>> parser.nodes
        [<XpathNode(element): //div[@class='content'] >, <XpathNode(element): /p >]


        :param expression:
        """
        self._expression = expression
        self.index = index
        self.nodes = [
            XpathNode(node) if isinstance(node, str) else node
            for node in self.parse(self._expression)
        ]

    def __repr__(self):
        return "<XpathExpression: {} >".format(self._expression)

    def __str__(self):
        return self.__repr__()

    @classmethod
    def normalize(cls, expression: str) -> str:
        """
        >>> XpathExpression.normalize("((//svg)[2]//text)/text()")
        '(//svg)[2]//text/text()'
        >>> XpathExpression.normalize("//div/a[position() > 1]")
        '//div/a[position()>1]'
        >>> XpathExpression.normalize("//div/a[@class='abc 123']")
        "//div/a[@class='abc 123']"

        normalzed xpath expression
        :param expression:
        :return:
        """
        expression_length = len(expression)
        # remove useless ()
        brackets = parse_groups(expression)
        removed_char_idxs = []
        for start, end in brackets:
            if start + 1 == end or expression[start + 1] != "/":
                # ignore function
                continue
            if end == expression_length - 1 or expression[end + 1] != "[":
                removed_char_idxs.extend([start, end])
                continue
        # remove useless space
        if " " in expression:
            # TODO fix ' and "
            if "'" in expression:
                quote_groups = parse_groups(expression, flag="''")
            elif '"' in expression:
                quote_groups = parse_groups(expression, flag='""')
            else:
                quote_groups = []
            no_quote_indexs = set(range(len(expression)))
            for quote_group in quote_groups:
                no_quote_indexs -= set(range(*quote_group))
            for _idx, char in enumerate(expression):
                if char == " " and _idx in no_quote_indexs:
                    removed_char_idxs.append(_idx)
        expression = "".join(
            [x for _idx, x in enumerate(expression) if _idx not in removed_char_idxs]
        )
        return expression.strip()

    @classmethod
    def parse(cls, expression: str) -> list:
        """
        >>> XpathExpression.parse("//div[@class='content']/p")
        ["//div[@class='content']", '/p']

        :param expression:
        :return:
        """
        # normalize
        _expression = cls.normalize(expression)
        _expression = _expression.lstrip(".").rstrip("/")
        # check
        if not _expression.startswith(("/", "(")):
            raise InValidXpath(expression)
        nodes = []
        if "|" in _expression:
            nodes = [cls(x) for x in _expression.split("|")]
            return nodes

        # groups
        brackets = parse_groups(_expression)
        if brackets:
            _group_start, _group_end = brackets[0]
            if _group_start == 0 and _group_start + 1 != _group_end:
                if _expression[_group_end + 1] == "[":
                    _group_end = (
                        _group_end + 1 + _expression[_group_end + 1 :].find("]")
                    )
                _group_expression = _expression[_group_start : _group_end + 1]
                if _group_expression.endswith("]"):
                    _group_expression_index = int(
                        re.search("\[(\d+)\]$", _group_expression).group(1)
                    )
                else:
                    _group_expression_index = 0
                #
                first_group = parse_groups(_group_expression)[0]
                _group_expression = _group_expression[
                    first_group[0] + 1 : first_group[1]
                ]
                nodes.append(cls(_group_expression, index=_group_expression_index))
                _expression = _expression[_group_end + 1 :]
        #
        in_quote = False
        _node = []
        for _idx, _s in enumerate(_expression):
            if _s in ['"', "'"] and not in_quote:
                in_quote = True
            else:
                in_quote = False
            #
            if _s == "/" and _expression[_idx - 1] != "/" and not in_quote:
                #
                nodes.append("".join(_node))
                _node = [_s]
            else:
                _node.append(_s)
        if _node:
            nodes.append("".join(_node))
        nodes = [x for x in nodes if x]
        return nodes


if __name__ == "__main__":
    import doctest

    doctest.testmod()

    xp1 = XpathExpression("//div[@class='a']/a")
    xp2 = XpathExpression("./@href")

    print(xp1.nodes[-1]._parse_result)
    print(xp2.nodes[0]._parse_result)
