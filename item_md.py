from convert import html_to_md, text_to_md, text_to_md_table


TYPE_CLASS = 'class'
TYPE_CONSTRUCTOR = 'constructor'
TYPE_FIELD = 'field'
TYPE_PROPERTY = 'property'
TYPE_METHOD = 'method'

LANG_CS = 'cs'
LANG_VB = 'vb'
LANG = LANG_CS


class ItemMd:
    def __init__(self, item):
        self.item = item
        self.type = item['type'].lower()

    def type_str(self, string):
        if string.startswith('Global.'):
            string = string[7:]
        return string.replace('{', '&lt;').replace('}', '&gt;')

    def assemblies(self):
        assemblies = self.item.get('assemblies')
        if assemblies is None:
            return None

        result = 'Assembly:\n'
        for asm in assemblies:
            result += '- %s\n' % text_to_md(asm)
        return result + '\n'

    def inheritance(self):
        result = ''
        inherit_depth = 0

        inheritance = self.item.get('inheritance')
        if inheritance is not None:
            result += 'Inheritance\n'
            for inherit in inheritance:
                result += '%s- %s\n' % ('  ' * inherit_depth, text_to_md(inherit))
                inherit_depth += 2
            result += '%s- %s\n' % ('  ' * inherit_depth, text_to_md(self.item['name']))

        derived_classes = self.item.get('derivedClasses')
        if derived_classes is not None:
            if inherit_depth != 0:
                inherit_depth += 2
            for classname in derived_classes:
                result += '%s- %s\n' % ('  ' * inherit_depth, text_to_md(classname))
            result += '\n'

        return result if len(result) != 0 else None

    def inherited_members(self):
        inherited_members = self.item.get('inheritedMembers')
        if inherited_members is None:
            return None

        result = 'Inherited Members\n'
        for member in inherited_members:
            result += '- ' + text_to_md(member) + '\n'
        return result + '\n'

    def namespace(self):
        namespace = self.item.get('namespace')
        if namespace is None:
            return None

        return 'Namespace: %s\n' % text_to_md(namespace)

    def remarks(self):
        remarks = self.item.get('remarks')
        if remarks is None:
            return None
        return 'Remarks\n\n%s\n' % html_to_md(remarks)

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
        result += '\n```\n'

        parameters = syntax.get('parameters')
        if parameters is not None and len(parameters) != 0:
            has_description = any(map(lambda x: 'description' in x, parameters))
            result += 'Parameters\n'
            if has_description:
                result += '\n| Type | Name | Description |\n'
                result += '|---|---|---|\n'
                for param in parameters:
                    result += '| %s | *%s* | %s |\n' % (
                        self.type_str(param['type']),
                        text_to_md(param['id']),
                        html_to_md(text_to_md_table(param.get('description', ''))),
                    )
            else:
                result += '\n| Type | Name |\n'
                result += '|---|---|\n'
                for param in parameters:
                    result += '| %s | *%s* |\n' % (
                        self.type_str(param['type']),
                        text_to_md(param['id']),
                    )
            result += '\n'

        return_result = syntax.get('return')
        if return_result is None:
            return result

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
                self.type_str(return_result['type']),
                html_to_md(text_to_md_table(return_result['description'])),
            )
        else:
            result += '\n| Type |\n'
            result += '|---|\n'
            result += '| %s |\n' % self.type_str(return_result['type'])

        return result + '\n'
