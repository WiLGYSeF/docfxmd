import re


TAG_CODE = 'code'

TAG_REGEX = re.compile(r'<(/?)([A-Za-z]+)>')


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
