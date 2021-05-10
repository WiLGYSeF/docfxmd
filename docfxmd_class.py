import functools
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
        items = data.get('items')

        type_order = build_index([
            TYPE_CLASS,
            TYPE_CONSTRUCTOR,
            TYPE_FIELD,
            TYPE_PROPERTY,
            TYPE_METHOD,
        ])

        def cmp(a, b): #pylint: disable=invalid-name
            atype = type_order.get(a['type'].lower(), 9999)
            btype = type_order.get(b['type'].lower(), 9999)

            if atype != btype:
                return atype - btype
            return 1 if a['id'] >= b['id'] else -1

        items.sort(key=functools.cmp_to_key(cmp))

        type_headers = set()

        for item in items:
            print(json.dumps(item, indent=4))

            item_mdlist = []

            item_md = ItemMd(item)

            uid = item['uid']
            item_type = item['type'].lower()
            name = item['name']

            if item_type not in type_headers:
                if item_type == TYPE_CLASS:
                    item_mdlist.append('# Class %s' % text_to_md(name))
                elif item_type == TYPE_CONSTRUCTOR:
                    item_mdlist.append('## Constructors')
                elif item_type == TYPE_FIELD:
                    item_mdlist.append('## **Fields**')
                elif item_type == TYPE_PROPERTY:
                    item_mdlist.append('## **Properties**')
                elif item_type == TYPE_METHOD:
                    item_mdlist.append('## **Methods**')
                item_mdlist.append('')
                type_headers.add(item_type)

            if item_type in (TYPE_CONSTRUCTOR, TYPE_FIELD, TYPE_PROPERTY, TYPE_METHOD):
                item_mdlist.append('### ' + text_to_md(item['name']))
                item_mdlist.append('')

            item_mdlist.append(item_md.markdown())
            markdown.append(item_mdlist)

        result = ''
        for item in markdown:
            result += '\n'.join(item) + '\n'
        return result

def build_index(arr):
    index = {}
    count = 0
    for val in arr:
        index[val] = count
        count += 1
    return index
