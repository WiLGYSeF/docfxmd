from convert import replace_strings, html_to_md, text_to_md, newline_to_br
import name_parser


TYPE_NAMESPACE = 'namespace'
TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'
TYPE_ENUM = 'enum'

def build_index(arr):
    index = {}
    for val in arr:
        index[val] = len(index)
    return index

TYPE_ORDER = build_index([
    TYPE_NAMESPACE,
    TYPE_CLASS,
    TYPE_CONSTRUCTOR,
    TYPE_FIELD,
    TYPE_PROPERTY,
    TYPE_METHOD,
    TYPE_ENUM,
])

LANG_CS = 'cs'
LANG_VB = 'vb'
LANG = LANG_CS


class ItemMd:
    def __init__(self, docfx_md, item):
        self.docfx_md = docfx_md
        self.item = item

        self.uid = item['uid']
        self.id = item['id'] #pylint: disable=invalid-name
        self.name = item['name']
        self.type = item['type'].lower()

        self.type_order = TYPE_ORDER.get(self.type, 9999)

    def ident_str(self, ident, **kwargs):
        is_member = kwargs.get('is_member', False)

        if is_member:
            member = ident[-1]
            ident = ident[:-1]

        # TODO: fix

        result = ''
        for segment in ident:
            result += segment[0]
            container = segment[1]
            if container is not None:
                link = self.docfx_md.get_link(result)
                if link is not None:
                    result = '[%s](%s)' % (self.escape_ident(result), link)

                surround, idlist = container
                result += surround[0]
                result += ', '.join(map(lambda x: self.ident_str(x, **kwargs), idlist))
                result += surround[1]
            result += '.'
        result = result[:-1]

        link = self.docfx_md.get_link(result)
        if is_member:
            member_str = self.ident_str([member])
            result += '.' + member_str
            if link is not None:
                link += '#' + self.escape_fragment(member_str)

        if link is not None:
            return '[%s](%s)' % (self.escape_ident(result), link)
        return result

    def escape_ident(self, string):
        if string.startswith('Global.'):
            string = string[7:]
        else:
            namespace = self.item['namespace']
            namespace_dot = namespace + '.'
            if string.startswith(namespace_dot):
                string = string[len(namespace_dot):]
        return text_to_md(replace_strings(string, {
            '<': '&lt;',
            '>': '&gt;',
            '{': '&lt;',
            '}': '&gt;',
        }))

    def escape_fragment(self, frag):
        return replace_strings(frag.lower(), {
            ' ': '-',
            '.': '',
            ',': '',
            '(': '',
            ')': '',
        })

    def obj_str(self, string, **kwargs):
        name = self.escape_ident(string)

        try:
            identifier = name_parser.parse(string)
            if identifier is None:
                return name
            return self.ident_str(identifier[0], **kwargs)
        except ValueError:
            pass

        return name

    def markdown(self):
        md_list = []

        md_list.append(self.summary())
        md_list.append(self.inheritance())
        md_list.append(self.inherited_members())
        if self.type == TYPE_CLASS:
            md_list.append(self.namespace())
            md_list.append(self.assemblies())
        md_list.append(self.syntax())
        md_list.append(self.remarks())

        return '\n'.join(filter(lambda x: x is not None, md_list))

    def __gt__(self, other):
        return self._cmp(other) > 0

    def __le__(self, other):
        return self._cmp(other) < 0

    def __eq__(self, other):
        return self._cmp(other) == 0

    def _cmp(self, other):
        if self.type_order != other.type_order:
            return self.type_order - other.type_order
        if self.id > other.id:
            return 1
        if self.id < other.id:
            return -1
        return 0

    # --------

    def assemblies(self):
        assemblies = self.item.get('assemblies')
        if assemblies is None:
            return None
        return '**Assembly**: %s\n' % text_to_md(','.join(assemblies))

    def inheritance(self):
        result = ''
        inherit_depth = 0

        inheritance = self.item.get('inheritance')
        if inheritance is not None:
            result += 'Inheritance\n'
            for inherit in inheritance:
                result += '%s- %s\n' % ('  ' * inherit_depth, self.obj_str(inherit))
                inherit_depth += 2
            result += '%s- %s\n' % ('  ' * inherit_depth, text_to_md(self.item['name']))

        derived_classes = self.item.get('derivedClasses')
        if derived_classes is not None:
            if inherit_depth != 0:
                inherit_depth += 2
            for classname in derived_classes:
                result += '%s- %s\n' % ('  ' * inherit_depth, self.obj_str(classname))
            result += '\n'

        return result if len(result) != 0 else None

    def inherited_members(self):
        inherited_members = self.item.get('inheritedMembers')
        if inherited_members is None:
            return None

        result = 'Inherited Members\n'
        for member in inherited_members:
            result += '- ' + self.obj_str(member, is_member=True) + '\n'
        return result + '\n'

    def namespace(self):
        namespace = self.item.get('namespace')
        if namespace is None:
            return None

        return '**Namespace**: %s\n' % self.obj_str(namespace)

    def parameters(self):
        if 'syntax' not in self.item:
            return None

        parameters = self.item['syntax'].get('parameters')
        if parameters is None or len(parameters) == 0:
            return None

        result = 'Parameters\n'
        has_description = any(map(lambda x: 'description' in x, parameters))

        if has_description:
            result += '\n| Type | Name | Description |\n'
            result += '|---|---|---|\n'
            for param in parameters:
                result += '| %s | *%s* | %s |\n' % (
                    self.obj_str(param['type']),
                    text_to_md(param['id']),
                    newline_to_br(html_to_md(param.get('description', ''))),
                )
        else:
            result += '\n| Type | Name |\n'
            result += '|---|---|\n'
            for param in parameters:
                result += '| %s | *%s* |\n' % (
                    self.obj_str(param['type']),
                    text_to_md(param['id']),
                )

        return result + '\n'

    def remarks(self):
        remarks = self.item.get('remarks')
        if remarks is None:
            return None
        return 'Remarks\n\n%s\n' % html_to_md(remarks)

    def return_(self):
        if 'syntax' not in self.item:
            return None

        return_result = self.item['syntax'].get('return')
        if return_result is None:
            return None

        result = ''
        if self.type == TYPE_FIELD:
            result += 'Field Value\n'
        elif self.type == TYPE_PROPERTY:
            result += 'Property Value\n'
        else:
            result += 'Returns\n'

        if 'description' in return_result:
            result += '\n| Type | Description |\n'
            result += '|---|---|\n'
            result += '| %s | %s |\n' % (
                self.obj_str(return_result['type']),
                newline_to_br(html_to_md(return_result['description'])),
            )
        else:
            result += '\n| Type |\n'
            result += '|---|\n'
            result += '| %s |\n' % self.obj_str(return_result['type'])

        return result

    def summary(self):
        summary = self.item.get('summary')
        if summary is None:
            return None

        return html_to_md(summary) + '\n'

    def syntax(self):
        syntax = self.item.get('syntax')
        if syntax is None:
            return None

        result = ''

        if LANG == LANG_CS:
            content_key = 'content'
            lang = 'csharp'
        elif LANG == LANG_VB:
            content_key = 'content.vb'
            lang = ''

        if self.type == TYPE_CLASS:
            result += 'Syntax\n'
        else:
            result += 'Declaration\n'

        result += '\n```%s\n' % lang
        result += syntax[content_key]
        result += '\n```\n\n'

        parameters = self.parameters()
        if parameters is not None:
            result += parameters

        return_result = self.return_()
        if return_result is not None:
            result += return_result

        return result + '\n'
