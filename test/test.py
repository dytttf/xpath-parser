# coding:utf8
import os
import unittest


from xpathparser import XpathExpression


cur_path = os.path.dirname(__file__)


class ParserTest(unittest.TestCase):
    def test_parse(self):
        with open(os.path.join(cur_path, "xpath_example.txt"), encoding="utf8") as f:
            xpath_list = f.readlines()
        for xpath in xpath_list:
            p = XpathExpression(xpath)
            print(xpath.strip())
            print(p.nodes)
            # break
        return


if __name__ == "__main__":
    unittest.main()
