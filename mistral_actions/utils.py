import prettytable
import re
import six

from oslo_utils import encodeutils


def convert_to_snake_case(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def print_list(objs, fields, formatters={}, sortby_index=None):
    if sortby_index is None:
        sortby = None
    else:
        sortby = fields[sortby_index]
    pt = prettytable.PrettyTable([f for f in fields], caching=False)
    pt.align = 'l'

    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                data = o[field]
                if data is None:
                    data = '-'
                data = data.split('\n')[0]
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        pt.add_row(row)

    if sortby is not None:
        result = encodeutils.safe_encode(pt.get_string(sortby=sortby))
    else:
        result = encodeutils.safe_encode(pt.get_string())

    if six.PY3:
        result = result.decode()

    print(result)


def _convert_to_md_row(fields):
    return '|' + '|'.join(fields) + '|'


def dump_as_markdown_table(objs, fields, formatters={}):
    print(_convert_to_md_row(fields))
    print(_convert_to_md_row(['---'] * len(fields)))
    for o in objs:
        row = []
        for field in fields:
            if field in formatters:
                row.append(formatters[field](o))
            else:
                data = o[field]
                if data is None:
                    data = '-'
                data = data.split('\n')[0]
                # '\r' would break the table, so remove it.
                data = six.text_type(data).replace("\r", "")
                row.append(data)
        print(_convert_to_md_row(row))
