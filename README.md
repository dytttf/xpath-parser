# xpath-parser
> a xpath expression parser

## Examples

```python
from xpath_parser import XpathExpression

xp1 = XpathExpression("//div[@id='list']/a")
xp2 = XpathExpression("./a/@href")
assert xp1.nodes[-1].name == xp2.nodes[0].name
```