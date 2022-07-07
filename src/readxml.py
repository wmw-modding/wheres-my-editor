import lxml
from lxml import etree

with open('game/wmw/assets/Objects/shower_head.hs') as file:
    xml = etree.parse(file)

root = xml.getroot()

print(root[1][0][0].get('test'))
