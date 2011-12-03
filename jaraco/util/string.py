from __future__ import absolute_import, unicode_literals

import re
import inspect
import itertools
import functools

from .functools import compose
from .exceptions import throws_exception


def substitution(old, new):
	"""
	Return a function that will perform a substitution on a string
	"""
	return lambda s: s.replace(old, new)

def multi_substitution(*substitutions):
	"""
	Take a sequence of pairs specifying substitutions, and create
	a function that performs those substitutions.

	>>> multi_substitution(('foo', 'bar'), ('bar', 'baz'))('foo')
	u'baz'
	"""
	substitutions = itertools.starmap(substitution, substitutions)
	# compose function applies last function first, so reverse the
	#  substitutions to get the expected order.
	substitutions = reversed(tuple(substitutions))
	return compose(*substitutions)

class FoldedCase(unicode):
	"""
	A case insensitive string class; behaves just like str
	except compares equal when the only variation is case.
	>>> s = FoldedCase('hello world')

	>>> s == 'Hello World'
	True

	>>> 'Hello World' == s
	True

	>>> s.index('O')
	4

	>>> s.split('O')
	[u'hell', u' w', u'rld']

	>>> sorted(map(FoldedCase, ['GAMMA', 'alpha', 'Beta']))
	[u'alpha', u'Beta', u'GAMMA']
	"""
	def __lt__(self, other):
		return self.lower() < other.lower()
	def __gt__(self, other):
		return self.lower() > other.lower()
	def __eq__(self, other):
		return self.lower() == other.lower()
	def __hash__(self):
		return hash(self.lower())
	# cache lower since it's likely to be called frequently.
	def lower(self):
		self._lower = super(FoldedCase, self).lower()
		self.lower = lambda: self._lower
		return self._lower

	def index(self, sub):
		return self.lower().index(sub.lower())

	def split(self, splitter=' ', maxsplit=0):
		pattern = re.compile(re.escape(splitter), re.I)
		return pattern.split(self, maxsplit)

def local_format(string):
	"""
	format the string using variables in the caller's local namespace.

	>>> a = 3
	>>> local_format("{a:5}")
	u'    3'
	"""
	return string.format(**inspect.currentframe().f_back.f_locals)

def is_decodable(value):
	"""
	Return True if the supplied value is decodable (using the 'unicode'
	constructor and thus the default encoding).
	"""
	return not throws_exception(functools.partial(unicode, value),
		UnicodeDecodeError)

def is_binary(value):
	"""
	Return True if the value appears to be binary (that is, it's a byte
	string and isn't decodable).
	"""
	return isinstance(value, bytes) and not is_decodable(value)

def trim(s):
	"""
	Trim something like a docstring to remove the whitespace that
	is common due to indentation and formatting.
	"""
	return dedent(s).strip()

class Splitter(object):
	"""object that will split a string with the given arguments for each call
	>>> s = Splitter(',')
	>>> s('hello, world, this is your, master calling')
	[u'hello', u' world', u' this is your', u' master calling']
	"""
	def __init__(self, *args):
		self.args = args

	def __call__(self, s):
		return s.split(*self.args)
