import json

from item_md import ItemMd
from convert import html_to_md, text_to_md, text_to_md_table


TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'


class DocfxMd:
    def __init__(self):
        pass

    def docfx_to_md(self, data):
        if not isinstance(data, dict) or 'items' not in data:
            return None

        markdown = []
        items = sorted(map(lambda x: ItemMd(x), data.get('items')))

        type_headers = set()

        for item in items:
            print(json.dumps(item.item, indent=4))

            item_mdlist = []

            if item.type not in type_headers:
                if item.type == TYPE_CLASS:
                    item_mdlist.append('# Class %s' % text_to_md(item.name))
                elif item.type == TYPE_CONSTRUCTOR:
                    item_mdlist.append('## Constructors')
                elif item.type == TYPE_FIELD:
                    item_mdlist.append('## **Fields**')
                elif item.type == TYPE_PROPERTY:
                    item_mdlist.append('## **Properties**')
                elif item.type == TYPE_METHOD:
                    item_mdlist.append('## **Methods**')
                item_mdlist.append('')
                type_headers.add(item.type)

            if item.type in (TYPE_CONSTRUCTOR, TYPE_FIELD, TYPE_PROPERTY, TYPE_METHOD):
                item_mdlist.append('### ' + text_to_md(item.name))
                item_mdlist.append('')

            item_mdlist.append(item.markdown())
            markdown.append(item_mdlist)

        result = ''
        for item in markdown:
            result += '\n'.join(item) + '\n'
        return result
