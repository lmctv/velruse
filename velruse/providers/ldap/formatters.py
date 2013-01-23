"""General helpers allowing use of py:class:``string.Template``
and py:method:``str.format`` template syntax in a string interpolation
context

    >>> import formatters
    >>> mask = "test %(replaced)s"
    >>> mask % {"replaced": "output string"} 
    'test output string'
    >>> mask = formatters.format("{one} -> {two}")
    >>> mask % {'one': 1, 'two': 2}
    '1 -> 2'
    >>> mask = formatters.template("${three} <=> ${four}")
    >>> mask % {'three': 3, 'four': 4}
    '3 <=> 4'

"""

import string

class FormatInterpolator(str):
    """An utility class allowing the % operator to format a PEP 3101
    format string

    >>> f = FormatInterpolator('{one} -> {two}')
    >>> f
    <FormatInterpolator('{one} -> {two}')>

    >>> f % {'one': 1, 'two': 2}
    '1 -> 2'

    >>> f % (1,2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "interp.py", line 33, in __mod__
        raise TypeError('format requires a mapping')
    TypeError: format requires a mapping

    >>> f % {'one': 1}
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "interp.py", line 22, in __mod__
        return self.tpl.format(**other)
    KeyError: 'two'

    >>> f % {'one': 1, 'two': 2, 'three': 3}
    '1 -> 2'

    >>> f = FormatInterpolator('{} {} {}')
    >>> f % (1, 2, 3)
    '1 2 3'

    >>> f % (1, 2,)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "formatters.py", line 86, in __mod__
        raise TypeError('not enough arguments for format string')
    TypeError: not enough arguments for format string

    >>> f = FormatInterpolator('{one} -> {two}')
    >>> True if f else False
    True
    >>> 
    >>> f = FormatInterpolator('')
    >>> True if f else False
    False

    """

    def __init__(self, template=''):
        self.tpl = template

    def __str__(self):
        return self.tpl

    def __repr__(self):
        return '<FormatInterpolator(%r)>' % self.tpl

    def __nonzero__(self):
        return bool(self.tpl)

    def __mod__(self, other):

        if isinstance (other, dict):
            try:
                return self.tpl.format(**other)
            except IndexError:
                raise TypeError('not enough arguments for format string')

        try:
            if isinstance(other, tuple):
                return self.tpl.format(*other)
            else:
                return self.tpl.format(str(other))

        except KeyError:
            raise TypeError('format requires a mapping')
        except IndexError:
            raise TypeError('not enough arguments for format string')

format = FormatInterpolator

class TemplateInterpolator(str):
    """
    >>> f = TemplateInterpolator("${three} <=> ${four}")
    >>> f
    <TemplateInterpolator('${three} <=> ${four}')>

    >>> f % {'three': 3, 'four': 4}
    '3 <=> 4'

    >>> f % (1,2)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "formatters.py", line 94, in __mod__
        raise TypeError('format requires a mapping')
    TypeError: format requires a mapping

    >>> f % {'one': 1}
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "formatters.py", line 93, in __mod__
        return self.tpl.substitute(**other)
      File "/usr/lib/python2.7/string.py", line 172, in substitute
        return self.pattern.sub(convert, self.template)
      File "/usr/lib/python2.7/string.py", line 162, in convert
        val = mapping[named]
    KeyError: 'three'

    >>> f %  { 'two': 2, 'three': 3, 'four': 4}
    '3 <=> 4'

    >>> f = TemplateInterpolator("${three} <=> ${four}")
    >>> True if f else False
    True
    >>> f = TemplateInterpolator("")
    >>> True if f else False
    False


    """

    def __init__(self, tpl=''):
        self.tpl = string.Template(tpl)

    def __str__(self):
        return self.tpl.template

    def __repr__(self):
        return '<TemplateInterpolator(%r)>' % self.tpl.template

    def __nonzero__(self):
        return bool(self.tpl.template)

    def __mod__(self, other):
        other = {} or other
        if isinstance (other, dict):
            return self.tpl.substitute(**other)
        raise TypeError('format requires a mapping')

template = TemplateInterpolator
