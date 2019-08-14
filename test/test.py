# coding:utf8
import unittest


from xpathparser import XpathExpression


class ParserTest(unittest.TestCase):
    def test_parse(self):
        with open("xpath_example.txt", encoding="utf8") as f:
            xpath_list = f.readlines()
        for xpath in xpath_list:
            p = XpathExpression(xpath)
            print(p.nodes)
        return


if __name__ == "__main__":
    unittest.main()
