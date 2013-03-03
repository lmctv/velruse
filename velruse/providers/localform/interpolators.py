"""General helpers allowing use of py:class:``string.Template``
and py:method:``str.format`` template syntax in a string interpolation
context

    >>> import interpolators
    >>> mask = "test %(replaced)s"
    >>> mask % {"replaced": "output string"}
    'test output string'
    >>> mask = interpolators.format("{one} -> {two}")
    >>> mask % {'one': 1, 'two': 2}
    '1 -> 2'
    >>> mask = interpolators.template("${three} <=> ${four}")
    >>> mask % {'three': 3, 'four': 4}
    '3 <=> 4'

"""

import string

class FormatInterpolator(str):
    """A utility class allowing the % operator to format a PEP 3101
    format string

    >>> f = FormatInterpolator('{one} -> {two}')
    >>> f
    <FormatInterpolator('{one} -> {two}')>

    >>> f % {'one': 1, 'two': 2}
    '1 -> 2'

    >>> f.format(one=1, two=2)
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

    >>> f.format(1, 2, 3)
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

    def __repr__(self):
        return '<FormatInterpolator(%s)>' % str.__repr__(self)

    def __mod__(self, other):

        if isinstance (other, dict):
            try:
                return self.format(**other)
            except IndexError:
                raise TypeError('not enough arguments for format string')

        try:
            if isinstance(other, tuple):
                return self.format(*other)
            else:
                return self.format(str(other))

        except KeyError:
            raise TypeError('format requires a mapping')
        except IndexError:
            raise TypeError('not enough arguments for format string')

class TemplateInterpolator(str):
    """A utility class allowing the % operator to format a PEP 292
    string template

    >>> f = TemplateInterpolator("${three} <=> ${four}")
    >>> f
    <TemplateInterpolator('${three} <=> ${four}')>

    >>> f % {'three': 3, 'four': 4}
    '3 <=> 4'

    >>> f.safe_substitute({'three': 3, 'four': 4})
    '3 <=> 4'

    >>> f.substitute({'three': 3}, four=4)
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

    def substitute(self, mapping=None, **kws):
        return self.tpl.substitute(mapping, **kws)

    def safe_substitute(self, mapping=None, **kws):
        return self.tpl.safe_substitute(mapping, **kws)

def template(tpl=''):
    return TemplateInterpolator(tpl)

def format(tpl=''):
    return FormatInterpolator(tpl)

if __name__ == '__main__':
    import doctest
    doctest.testmod(exclude_empty=True)
