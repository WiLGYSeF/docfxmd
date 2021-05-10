import functools
import json
import re


TAG_CODE = 'code'

TAG_REGEX = re.compile(r'<(/?)([A-Za-z]+)>')

TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'

LANG_CS = 'cs'
LANG_VB = 'vb'
LANG = LANG_CS


class DocfxMd:
    def __init__(self):
        pass

    def type_str(self, string):
        if string.startswith('Global.'):
            string = string[7:]
        return string.replace('{', '&lt;').replace('}', '&gt;')

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

            item_md = []

            uid = item['uid']
            item_type = item['type'].lower()
            name = item['name']

            if item_type not in type_headers:
                if item_type == TYPE_CLASS:
                    item_md.append('# Class %s' % text_to_md(name))
                elif item_type == TYPE_CONSTRUCTOR:
                    item_md.append('## Constructors')
                elif item_type == TYPE_FIELD:
                    item_md.append('## **Fields**')
                elif item_type == TYPE_PROPERTY:
                    item_md.append('## **Properties**')
                elif item_type == TYPE_METHOD:
                    item_md.append('## **Methods**')
                item_md.append('')
                type_headers.add(item_type)

            if item_type in (TYPE_CONSTRUCTOR, TYPE_FIELD, TYPE_PROPERTY, TYPE_METHOD):
                item_md.append('### ' + text_to_md(item['name']))
                item_md.append('')

            summary = item.get('summary')
            if summary is not None:
                item_md.append(html_to_md(summary))
                item_md.append('')

            inherit_depth = 0

            inheritance = item.get('inheritance')
            if inheritance is not None:
                item_md.append('Inheritance:')
                for inherit in inheritance:
                    item_md.append('%s- %s' % ('  ' * inherit_depth, text_to_md(inherit)))
                    inherit_depth += 2
                item_md.append('%s- %s' % ('  ' * inherit_depth, text_to_md(item['name'])))
                item_md.append('')

            derived_classes = item.get('derivedClasses')
            if derived_classes is not None:
                if inherit_depth != 0:
                    inherit_depth += 2

                for classname in derived_classes:
                    item_md.append('%s- %s' % ('  ' * inherit_depth, text_to_md(classname)))
                item_md.append('')

            inherited_members = item.get('inheritedMembers')
            if inherited_members is not None:
                item_md.append('Inherited Members:')
                for member in inherited_members:
                    item_md.append('- ' + text_to_md(member))
                item_md.append('')

            if item_type == TYPE_CLASS:
                namespace = item.get('namespace')
                if namespace is not None:
                    item_md.append('Namespace: ' + text_to_md(namespace))
                    item_md.append('')

                assemblies = item.get('assemblies')
                if assemblies is not None:
                    item_md.append('Assembly:')
                    for asm in assemblies:
                        item_md.append('- ' + text_to_md(asm))
                    item_md.append('')

            syntax = item.get('syntax')
            if syntax is not None:
                if item_type == TYPE_CLASS:
                    item_md.append('Syntax')
                else:
                    item_md.append('Declaration')

                if LANG == LANG_CS:
                    content_key = 'content'
                    lang = 'csharp'
                elif LANG == LANG_VB:
                    content_key = 'content.vb'
                    lang = ''

                item_md.append('```' + lang)
                item_md.append(syntax[content_key])
                item_md.append('```')

                parameters = syntax.get('parameters')
                if parameters is not None and len(parameters) != 0:
                    has_description = any(map(lambda x: 'description' in x, parameters))
                    item_md.append('Parameters')
                    item_md.append('')
                    if has_description:
                        item_md.append('| Type | Name | Description |')
                        item_md.append('|---|---|---|')
                        for param in parameters:
                            item_md.append('| %s | *%s* | %s |' % (
                                self.type_str(param['type']),
                                text_to_md(param['id']),
                                html_to_md(text_to_md_table(param.get('description', ''))),
                            ))
                    else:
                        item_md.append('| Type | Name |')
                        item_md.append('|---|---|')
                        for param in parameters:
                            item_md.append('| %s | *%s* |' % (
                                self.type_str(param['type']),
                                text_to_md(param['id']),
                            ))
                    item_md.append('')

                return_result = syntax.get('return')
                if return_result is not None:
                    if item_type == TYPE_FIELD:
                        item_md.append('Field Value')
                    elif item_type == TYPE_PROPERTY:
                        item_md.append('Property Value')
                    else:
                        item_md.append('Returns')
                    item_md.append('')

                    if 'description' in return_result:
                        item_md.append('| Type | Description |')
                        item_md.append('|---|---|')
                        item_md.append('| %s | %s |' % (
                            self.type_str(return_result['type']),
                            html_to_md(text_to_md_table(return_result['description'])),
                        ))
                    else:
                        item_md.append('| Type |')
                        item_md.append('|---|')
                        item_md.append('| %s |' % self.type_str(return_result['type']))
                    item_md.append('')

            remarks = item.get('remarks')
            if remarks is not None:
                item_md.append('Remarks')
                item_md.append('')
                item_md.append(html_to_md(remarks))
                item_md.append('')

            item_md.append('')
            markdown.append(item_md)

        result = ''
        for item in markdown:
            result += '\n'.join(item) + '\n'
        return result

def text_to_md(data):
    # TODO: better escapes
    result = data
    result = result.replace('_', r'\_')
    result = result.replace('*', r'\*')
    return result

def text_to_md_table(data):
    return text_to_md(data).strip().replace('\n', '<br/>').replace('|', r'\|')

def html_to_md(data):
    result = ''
    open_tags = []
    last = 0

    for match in TAG_REGEX.finditer(data):
        if match[1] == '':
            prev_tag = open_tags[-1].lower() if len(open_tags) != 0 else None
            tag = match[2].lower()

            if prev_tag == TAG_CODE:
                result += '`%s`' % data[last:match.start()]
            else:
                result += text_to_md(data[last:match.start()])
            last = match.end()
            open_tags.append(match[2])
        else:
            prev_tag = open_tags.pop().lower()
            tag = match[2].lower()
            if prev_tag != tag:
                raise ValueError()

            prev_tag = open_tags[-1].lower() if len(open_tags) != 0 else None
            tag = match[2].lower()

            if tag == TAG_CODE:
                result += '`%s`' % data[last:match.start()]
            else:
                result += text_to_md(data[last:match.start()])
            last = match.end()

    result += text_to_md(data[last:])
    return result

def build_index(arr):
    index = {}
    count = 0
    for val in arr:
        index[val] = count
        count += 1
    return index
