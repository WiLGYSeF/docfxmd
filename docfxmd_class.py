import json
import os

from item_md import ItemMd
from convert import html_to_md, text_to_md, text_to_md_table


TYPE_NAMESPACE = 'namespace'
TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'


class DocfxMd:
    def __init__(self, root, **kwargs):
        self.root = root

        self.link_extensions = kwargs.get('link_extensions', True)

    def docfx_to_md(self, data):
        if not isinstance(data, dict) or 'items' not in data:
            return None

        markdown = []
        items = sorted(map(lambda x: ItemMd(self, x), data.get('items')))

        type_headers = set()

        for item in items:
            #print(json.dumps(item.item, indent=4))

            item_mdlist = []

            if item.type == TYPE_NAMESPACE:
                item_mdlist.append(self.namespace_md(data))
            else:
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

    def namespace_md(self, namespace):
        item = namespace['items'][0]
        result = '# Namespace %s\n\n' % text_to_md(item['name'])
        references = namespace['references']
        for ref in references:
            name = ref['uid']

            try:
                # TODO: fix
                import yaml
                with open(os.path.join(self.root, name + '.yml'), 'r', encoding='utf-8') as file:
                    obj = yaml.load(file, Loader=yaml.Loader)
            except:
                obj = None

            result += '### [%s](%s)\n\n'% (name, name + '.md')

            if obj is not None:
                class_item = None
                for item in obj['items']:
                    if item['type'].lower() == TYPE_CLASS:
                        class_item = item
                        break

                if class_item is not None:
                    result += class_item.get('summary', '') + '\n'
        return result

    def get_link(self, fname):
        path = os.path.join(self.root, fname + '.yml')
        if not os.path.isfile(path):
            return None
        if self.link_extensions:
            return fname + '.md'
        return fname
