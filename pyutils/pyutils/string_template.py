import re

class ExtendedTemplate(object):
    def __init__(self, template, idpattern, delimiter='$'):
        self.idpattern = idpattern
        self.delimiter = delimiter
        self.template = template

        pattern = r"""
        %(delim)s(?:
          (?P<escaped>%(delim)s) |   # Escape sequence of two delimiters
          (?P<named>%(id)s)      |   # delimiter and a Python identifier
          {(?P<braced>%(id)s)}   |   # delimiter and a braced identifier
          (?P<invalid>)              # Other ill-formed delimiter exprs
        )
        """ % {
            'delim' : re.escape(delimiter),
            'id'    : idpattern,
        }
        self.pattern = re.compile(pattern, re.VERBOSE)

    def _invalid(self, mo):
        i = mo.start('invalid')
        lines = self.template[:i].splitlines(True)
        if not lines:
            colno = 1
            lineno = 1
        else:
            colno = i - len(''.join(lines[:-1]))
            lineno = len(lines)
        raise ValueError('Invalid placeholder in string: line %d, col %d' %
                         (lineno, colno))

    #Search for $$, $identifier, ${identifier}, and any bare $'s
    def substitute(self, get_value):
        def convert(mo):
            # Check the most common path first.
            named = mo.group('named') or mo.group('braced')
            if named is not None:
                val = get_value(named)
                return val
            if mo.group('escaped') is not None:
                return self.delimiter
            if mo.group('invalid') is not None:
                self._invalid(mo)
            raise ValueError('Unrecognized named group in pattern',
                             self.pattern)
        return self.pattern.sub(convert, self.template)


class JsonPathTemplate(ExtendedTemplate):
    def __init__(self, template, **kwargs):
        idpattern = r'[_a-zA-Z][_a-zA-Z0-9\[\].]*'
        super(JsonPathTemplate, self).__init__(template, idpattern=idpattern, **kwargs)


