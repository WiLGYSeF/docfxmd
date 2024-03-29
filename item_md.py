from convert import replace_strings, html_to_md, text_to_md, newline_to_br
import name_parser


TYPE_NAMESPACE = 'namespace'
TYPE_CLASS = 'class'
TYPE_STRUCT = 'struct'
TYPE_INTERFACE = 'interface'
TYPE_ENUM = 'enum'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'

def build_index(arr):
    index = {}
    for val in arr:
        index[val] = len(index)
    return index

TYPE_ORDER = build_index([
    TYPE_NAMESPACE,
    TYPE_CLASS,
    TYPE_STRUCT,
    TYPE_INTERFACE,
    TYPE_ENUM,
    TYPE_CONSTRUCTOR,
    TYPE_FIELD,
    TYPE_PROPERTY,
    TYPE_METHOD,
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

    def _ident_str(self, ident, **kwargs):
        is_member = kwargs.get('is_member', False)
        make_links = kwargs.get('make_links', True)

        if is_member:
            member = ident[-1]
            ident = ident[:-1]

        if not make_links:
            result = name_parser.tostring(
                ident,
                prepare_sub_ident=lambda x, y: self.get_ident_name(x, **kwargs)
            )
            if is_member:
                result += '.' + self.get_ident_name(member, **kwargs)
            return result

        result = name_parser.tostring(ident, include_containers=False)
        link = self.docfx_md.get_link(result)
        if link is not None:
            result = name_parser.tostring(
                ident,
                prepare_sub_ident=lambda x, y: self.get_ident_name(x, **kwargs)
            )
            if is_member:
                member_str = self._ident_str([member], make_links=False)
                result += '.' + member_str
                link += '#' + self.escape_fragment(member_str)
            return '[%s](%s)' % (text_to_md(self.get_ident_name(result, **kwargs)), link)

        args = kwargs.copy()
        args['is_member'] = False
        result = name_parser.tostring(
            ident,
            prepare_sub_ident=lambda x, y: self._ident_str(y, **args)
        )

        if is_member:
            result += '.' + self._ident_str([member], make_links=False)

        return self.get_ident_name(result, **kwargs)

    def get_ident_name(self, string, **kwargs):
        truncate_name = kwargs.get('truncate_name', True)

        string = string.replace('<', '&lt;').replace('>', '&gt;')

        if string.startswith('Global.'):
            return string[7:]

        if truncate_name:
            ns_parts = self.item['namespace'].split('.')
            string_parts = string.split('.')

            idx = 0
            while idx < min(len(string_parts), len(ns_parts)):
                if string_parts[idx] != ns_parts[idx]:
                    break
                idx += 1
            if idx != 0:
                if idx == len(string_parts):
                    idx -= 1
                string = '.'.join(string_parts[idx:])

        return string

    def escape_fragment(self, frag):
        return replace_strings(frag.lower(), {
            ' ': '-',
            '(': '',
            ')': '',
            '.': '',
            ',': '',
            '`': '-',
        })

    def ident_str(self, string, **kwargs):
        try:
            identifier = name_parser.parse(string)
            if identifier is not None:
                return self._ident_str(identifier[0], **kwargs)
        except ValueError:
            pass

        name = replace_strings(string, {
            '{': '',
            '}': '',
        })
        return text_to_md(self.get_ident_name(name, **kwargs))

    def markdown(self):
        md_list = []

        if self.is_member():
            md_list.append('### %s\n' % text_to_md(self.name))

        md_list.append(self.summary())

        if self.is_page_view():
            md_list.append(self.inheritance())
            md_list.append(self.inherited_members())
            md_list.append(self.namespace())
            md_list.append(self.assemblies())

        md_list.append(self.syntax())
        md_list.append(self.parameters())
        md_list.append(self.return_())
        md_list.append(self.remarks())

        return '\n'.join(filter(lambda x: x is not None, md_list))

    def is_member(self):
        return self.type in (
            TYPE_CONSTRUCTOR,
            TYPE_FIELD,
            TYPE_PROPERTY,
            TYPE_METHOD
        )

    def is_page_view(self):
        return self.type in (
            TYPE_CLASS,
            TYPE_STRUCT,
            TYPE_INTERFACE,
            TYPE_ENUM,
        )

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
                result += '%s- %s\n' % ('  ' * inherit_depth, self.ident_str(inherit))
                inherit_depth += 2
            result += '%s- %s\n' % ('  ' * inherit_depth, text_to_md(self.item['name']))

        derived_classes = self.item.get('derivedClasses')
        if derived_classes is not None:
            if inherit_depth != 0:
                inherit_depth += 2
            for classname in derived_classes:
                result += '%s- %s\n' % ('  ' * inherit_depth, self.ident_str(classname))
            result += '\n'

        return result if len(result) != 0 else None

    def inherited_members(self):
        inherited_members = self.item.get('inheritedMembers')
        if inherited_members is None:
            return None

        result = 'Inherited Members\n'
        for member in inherited_members:
            result += '- ' + self.ident_str(member, is_member=True) + '\n'
        return result + '\n'

    def namespace(self):
        namespace = self.item.get('namespace')
        if namespace is None:
            return None

        return '**Namespace**: %s\n' % self.ident_str(namespace, truncate_name=False)

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
                    self.ident_str(param['type']),
                    text_to_md(param['id']),
                    newline_to_br(html_to_md(param.get('description', '&nbsp;'))),
                )
        else:
            result += '\n| Type | Name |\n'
            result += '|---|---|\n'
            for param in parameters:
                result += '| %s | *%s* |\n' % (
                    self.ident_str(param['type']),
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
                self.ident_str(return_result['type']),
                newline_to_br(html_to_md(return_result['description'])),
            )
        else:
            result += '\n| Type |\n'
            result += '|---|\n'
            result += '| %s |\n' % self.ident_str(return_result['type'])

        return result + '\n'

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
        return result
