class EnumValueError(ValueError):
    pass
class EnumMemberError(AttributeError):
    pass

def deepcopy(obj):
    """
    Perform a deep copy of obj using cPickle. Faster than copy.deepcopy()
    for large objects.
    
    @param obj: the object to copy
    @return: a deep copy of obj
    """
    import cPickle, sys
    sys.setrecursionlimit(100000)
    tmp = cPickle.dumps(obj, cPickle.HIGHEST_PROTOCOL)
    return cPickle.loads(tmp)

class enum(object):
    """
    Extended enumeration type. Supports both string and integer enumeration
    values. Examples:
    
        1. Implicit values:
        
            >>> MolTypes = enum('DNA', 'RNA'...)
            DNA=1, RNA=2...
            >>> MolTypes.DNA
            1
            >>> MolTypes.DNA == 1
            True
            >>> int(MolTypes.DNA)
            1
            >>> repr(MolTypes.DNA)
            'DNA'
            >>> type(MolTypes.DNA)
            EnumItem instance
            
        2. Explicit values:
        
            >>> MolTypes = enum(DNA='d', RNA='r'...)
            DNA='d', RNA='r'...
            >>> MolTypes.DNA
            'd'
    """

    def __init__(self, *items, **kitems):

        object.__setattr__(self, '_uq_names', { })
        object.__setattr__(self, '_uq_namesci', { })
        object.__setattr__(self, '_uq_values', { })
        object.__setattr__(self, '_uq_valuesci', { })

        count = 0

        for v, i in enumerate(items):
            i = str(i).strip()
            self.__check(i, v)
            self.__dict__[i] = EnumItem(i, v, self)
            count += 1

        for i in kitems:
            v = kitems[i]
            ii = i
            i = str(i).strip()
            self.__check(i, v)
            self.__dict__[ii] = EnumItem(i, v, self)
            count += 1

        if count < 1:
            raise ValueError('Empty enum.')

    def __check(self, i, v):

            import re

            if not (isinstance(i, basestring) and re.match('^[a-zA-Z_]', i)):
                raise AttributeError('Enum items must be valid Python identifiers.')

            if i in self._uq_names:
                raise ValueError('Duplicate item {0} in enum.'.format(i))
            if v in self._uq_values:
                raise ValueError('Duplicate value {0} in enum.'.format(v))

            self._uq_names[i] = i
            self._uq_namesci[i.lower()] = i
            self._uq_values[v] = i
            if isinstance(v, basestring):
                self._uq_valuesci[v.lower()] = i

    def __setattr__(self, name, value):
        raise NotImplementedError()

    def __repr__(self):
        n = ''
        if len(self._uq_names) > 1:
            n = ', ...'
        i = iter(Enum.members(self)).next()
        return '<enum: {0!r}={0!s}{1}>'.format(i, n)

class EnumItem(object):

    def __init__(self, name, value, container):
        self.__name = name
        self.__value = value
        self.__container = container

    def __repr__(self):
        return '{0}'.format(self.__name, self.__value)
    def __str__(self):
        return str(self.__value)
    def __int__(self):
        return int(self.__value)
    def __float__(self):
        return float(self.__value)
    def __hash__(self):
        return hash(self.__value)
    def __cmp__(self, other):
        if isinstance(other, EnumItem):
            return cmp(self.__value, other.value)
        else:
            return cmp(self.__value, other)

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        return self.__value

    @property
    def enum(self):
        return self.__container

class Enum(object):
    """
    A collection of static methods for working with L{enum}s.
    """

    @staticmethod
    def members(enum):
        """
        Return all member items of the C{enum}.
        
        @param enum: the enumeration object to traverse
        @type enum: L{enum}
        
        @return: a set of all enum members
        @rtype: frozenset
        """
        return frozenset([enum.__dict__[i] for i in enum._uq_names])

    @staticmethod
    def names(enum):
        """
        Return the names of all items in the C{enum}.
        
        @param enum: the enumeration object to traverse
        @type enum: L{enum}
        
        @return: a set of all enum member names
        @rtype: frozenset        
        """
        return frozenset(enum._uq_names)

    @staticmethod
    def values(enum):
        """
        Return all values of the C{enum}.
        
        @param enum: the enumeration object to traverse
        @type enum: L{enum}
        
        @return: a set of all enum values
        @rtype: frozenset        
        """
        return frozenset(enum._uq_values)

    @staticmethod
    def parse(enum, value, ignore_case=True):
        """
        Parse as C{enum} value and convert it to a member of the L{enum} type.
        
        @param enum: an instance of the target enumeration type
        @type enum: L{enum}
        @param value: the value to be parsed as an enum item
        @type value: str, int
        @param ignore_case: if set to True, triggers case insensitive parsing
        @type ignore_case: bool
        
        @return: a member of the enum which has that value
        @rtype: EnumItem
        
        @raise EnumValueError: when value is not found in enum
        """

        if ignore_case:
            values = enum._uq_valuesci
            value = value.lower()
        else:
            values = enum._uq_values

        if value in values:
            return enum.__dict__[ values[value] ]
        else:
            raise EnumValueError('No such value {0} in {1}'.format(value, enum))

    @staticmethod
    def parsename(enum, name, ignore_case=True):
        """
        Parse as C{enum} item name and convert it to a member of the L{enum} type.
        
        @param enum: an instance of the target enumeration type
        @type enum: L{enum}
        @param name: the value to be parsed as an enum item
        @type name: str
        @param ignore_case: if set to True, triggers case insensitive parsing
        @type ignore_case: bool
        
        @return: a member of the enum having that name
        @rtype: L{EnumItem}
        
        @raise EnumValueError: when name is not found in enum's members        
        """

        if ignore_case:
            names = enum._uq_namesci
            name = name.lower()
        else:
            names = enum._uq_names

        if name in names:
            return enum.__dict__[ names[name] ]
        else:
            raise EnumMemberError('No such item {0} in {1}'.format(name, enum))

    @staticmethod
    def tostring(item):
        """
        Return a string representation of the enum item.
        
        @param item: an enum item to be converted to a string
        @type item: L{EnumItem}
        
        @return: the value of the enum member
        @rtype: str
        """
        return item.name

    @staticmethod
    def ismember(item, enum):
        """
        Return True if item is a member of enum.
        
        @param enum: an instance of the target enumeration type
        @type enum: L{enum}
        @param item: the enum item to be tested
        @type item: L{EnumItem}
        @rtype: bool        
        """
        return item.enum is enum

class ItemNotFoundError(KeyError):
    pass
class InvalidKeyError(KeyError):
    pass
class DuplicateKeyError(InvalidKeyError):
    pass

class DictionaryContainerBase(object):
    """ 
    Base class which defines the behavior of a read only key-value collection 
    container. 

    @param items: an initialization dictionary
    @param restrict: a list of keys allowed for this dictionary
    """

    def __init__(self, items=None, restrict=None):

        self._keys = None
        self._items = { }

        if items is not None:
            self._set(items)
        if restrict:
            self._keys = frozenset(restrict)

    def __getitem__(self, key):
        try:
            return self._items[key]
        except KeyError:
            raise ItemNotFoundError(key)

    def __contains__(self, item):
        return item in self._items

    def __len__(self):
        return len(self._items)

    def __nonzero__(self):
        return len(self) > 0

    @property
    def length(self):
        return len(self)

    def keys(self):
        return self._items.keys()

    def __iter__(self):
        return iter(self._items)

    def __repr__(self):
        return repr(self._items)

    def _set(self, new_items):
        new_items = dict(new_items)

        if self._keys and not self._keys.issuperset(new_items):
            raise InvalidKeyError("One or more of the keys provided are not allowed for this collection.")

        self._items = new_items

    def _update(self, new_items={ }, **named_items):
        new_items = dict(new_items)

        if self._keys:
            if not set(self).issuperset(new_items) or not set(self).issuperset(named_items):
                raise ItemNotFoundError("One or more of the keys provided were not found in this collection.")

        self._items.update(new_items)
        self._items.update(named_items)

class DictionaryContainer(DictionaryContainerBase):
    """ 
    Write-enabled Dictionary Container.
    """
    def __init__(self, items=None, restrict=None):

        super(DictionaryContainer, self).__init__(items, restrict)

    def append(self, key, item):
        """
        Append a new key-value to the collection.
        
        @param key: key
        @param item: value

        @raise InvalidKeyError: when the key is not allowed for this container
        @raise DuplicateKeyError: when such a key already exists 
        """
        if self._keys and key not in self._keys:
            raise InvalidKeyError("Key {0} is not allowed for this collection.".format(key))
        if key in self:
            raise DuplicateKeyError("Key {0} already exists in the collection.".format(key))
        self._items[key] = item

    def set(self, new_items):
        """ 
        Set the collection to the dictionary provided in the new_items parameter.
        
        @param new_items: the new value of the dictionary container
        @type new_items: dict
        """
        self._set(new_items)

    def update(self, new_items={ }, **named_items):
        """ 
        Update the collection with the dictionary provided in the C{new_items} parameter.
        Update also specific items with the values provided as keyword arguments.
        
        @param new_items: a dictionary that provides new values for certain keys
        @type new_items: dict
        """
        self._update(new_items, **named_items)

class CollectionIndexError(IndexError):
    pass

class CollectionContainerBase(object):
    """ 
    Base class which defines the behavior of a read-only collection container.
    
    @param items: initialization list
    @type items: list
    @param type: if defined, makes the container type-safe
    @type type: type
    @param start_index: the index of the zero element
    @type start_index: int
    """

    def __init__(self, items=None, type=None, start_index=0):

        self._items = [ ]
        self._type = type

        if not (isinstance(start_index, int) or start_index >= 0):
            raise ValueError('start_index must be a positive integer.')

        self._start = start_index

        if items is not None:
            self._update(items)

    def __fix(self, i):
        if i >= 0:
            if i < self._start:
                return None
            return i - self._start
        else:
            return i

    def __getitem__(self, i):
        try:
            if isinstance(i, slice):
                sl = slice(self.__fix(i.start), self.__fix(i.stop), i.step)
                return self._items[sl]
            else:
                if 0 <= i < self._start:
                    raise IndexError
                return self._items[self.__fix(i)]

        except IndexError:
            if len(self) > 0:
                raise CollectionIndexError('List index {0} out of range: {1}..{2}'.format(i, self.start_index, self.last_index))
            else:
                raise CollectionIndexError('List index out of range. The collection is empty.')

    def __contains__(self, item):
        return item in self._items

    def __len__(self):
        return len(self._items)

    def __nonzero__(self):
        return len(self) > 0

    @property
    def length(self):
        return len(self)

    @property
    def start_index(self):
        return self._start

    @property
    def last_index(self):
        length = len(self._items)
        if length > 0:
            return length + self._start - 1
        else:
            return None

    def __iter__(self):
        return iter(self._items)

    def __repr__(self):
        return repr(self._items)

    def _append(self, item):

        if self._type:
            if not isinstance(item, self._type):
                raise TypeError("Item {0} is not of the required {1} type.".format(item, self._type.__name__))
        self._items.append(item)

        return len(self) + self._start - 1

    def _update(self, new_items):

        if self._type:
            for a in new_items:
                if not isinstance(a, self._type):
                    raise TypeError("Item {0} is not of the required {1} type.".format(a, self._type.__name__))
        self._items = list(new_items)

class CollectionContainer(CollectionContainerBase):
    """ 
    Write-enabled Collection Container.
    """

    def __init__(self, items=None, type=None, start_index=0):

        super(CollectionContainer, self).__init__(items, type, start_index)

    def append(self, item):
        """
        Append a new item to the collection.
        
        @param item: the new item to append

        @return: the index of the new element        
        @rtype: int
        
        @raise TypeError: when the container is type-safe and item has an 
                          incorrect type
        """
        return self._append(item)

    def update(self, new_items):
        """ 
        Set the collection to the list provided in the new_items parameter.
        
        @param new_items: a list providing the new items for the container
        @type new_items: list
        """
        self._update(new_items)