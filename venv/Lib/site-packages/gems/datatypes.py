# -*- coding: utf-8 -*-
#
# Decorators for terminal-based wait animations
#
# @author <bprinty@gmail.com>
# ------------------------------------------------


# imports
# -------
import os
import re
import json
import yaml
import glob

from .utils import depricated_name, deprecated


# data management
# -----------------
class composite(object):
    """
    Data structure for traversing object relationships via attributes
    instead of keys and indices.

    Args:
        data (tuple, list, dict): Data to build composite datastructure from.

    Example:
        >>> data = composite({
        >>>     'one': 1,
        >>>     'two': [1, 2, 3],
        >>>     'three': ['one', 2, {'three': 'four'}],
        >>>     'four': {'five': [6, 7, 8], 'nine': 10, 'eleven': 'twelve'}
        >>> })
        >>> data.four.five[1] == 6
        True
        >>> data.two[0] == 1
        True
    """

    def __init__(self, data):
        self._list = []
        self._dict = {}
        self.meta_type = None

        if hasattr(data, 'read'):
            data = json.load(data)

        if isinstance(data, (list, tuple)):
            for dat in data:
                if not isinstance(dat, (list, tuple, dict)):
                    self._list.append(dat)
                else:
                    self._list.append(composite(dat))
            self.meta_type = 'list'

        elif isinstance(data, dict):
            for key in data:
                if not isinstance(data[key], (list, tuple, dict)):
                    self._dict[key] = data[key]
                else:
                    self._dict[key] = composite(data[key])
            self.meta_type = 'dict'

        elif isinstance(data, composite):
            self.meta_type = data.meta_type
            if data.meta_type == 'dict':
                self._dict = data._dict
            elif data.meta_type == 'list':
                self._list = data._list

        else:
            raise TypeError('unsupported type for creating composite: {}'.format(type(data)))
        return

    @classmethod
    def load(cls, fh):
        """
        Load json or yaml data from file handle.

        Args:
            fh (file): File handle to load from.

        Examlple:
            >>> with open('data.json', 'r') as json:
            >>>    jsdata = composite.load(json)
            >>>
            >>> with open('data.yml', 'r') as yml:
            >>>    ymldata = composite.load(yml)
        """
        dat = fh.read()
        try:
            ret = cls.from_json(dat)
        except:
            ret = cls.from_yaml(dat)
        return ret

    @classmethod
    def from_json(cls, fh):
        """
        Load json from file handle.

        Args:
            fh (file): File handle to load from.

        Examlple:
            >>> with open('data.json', 'r') as json:
            >>>    data = composite.load(json)
        """
        if isinstance(fh, str):
            return cls(json.loads(fh))
        else:
            return cls(json.load(fh))

    @classmethod
    def from_yaml(cls, fh):
        """
        Load yaml from file handle.

        Args:
            fh (file): File handle to load from.

        Examlple:
            >>> with open('data.yml', 'r') as json:
            >>>    data = composite.load(json)
        """
        return cls(yaml.load(fh))

    @classmethod
    def from_string(cls, string):
        """
        Load data from string.

        Args:
            string (str): String to load from.

        Examlple:
            >>> with open('data.json', 'r') as json:
            >>>     jdat = json.read()
            >>> data = composite.from_string(jdat)
        """
        return cls(eval(string))

    def __len__(self):
        return max(len(self._list), len(self._dict))

    def __str__(self):
        return str(self.json())

    def __repr__(self):
        return str(self)

    def __iter__(self):
        if self.meta_type == 'list':
            for entry in self._list:
                yield entry

        elif self.meta_type == 'dict':
            for entry in self._dict:
                yield entry
        return

    def __getattr__(self, name):
        if name in self._dict:
            return self._dict[name]
        else:
            raise AttributeError('\'composite\' object has no attribute {}'.format(name))
        return

    def __getitem__(self, item):
        if self.meta_type == 'list':
            return self._list[item]
        elif self.meta_type == 'dict':
            return self._dict[item]
        else:
            raise KeyError(str(item))
        return

    def __delitem__(self, item):
        if self.meta_type == 'list':
            del self._list[item]
        elif self.meta_type == 'dict':
            del self._dict[item]
        else:
            raise KeyError(str(item))
        return

    def __setattr__(self, name, value):
        if name == '_list' or name == '_dict' or name == 'meta_type':
            super(composite, self).__setattr__(name, value)
        else:
            self._dict[name] = value
        return

    def __setitem__(self, idx, value):
        if self.meta_type == 'list':
            self._list[idx] = value
        elif self.meta_type == 'dict':
            self._dict[idx] = value
        return

    def __add__(self, other):
        # TODO: Think about doing a recursive addition of all the
        #       properties -- for strings, concat, for ints, add, etc.
        #       Get feedback about this, and see if it intuitively makes
        #       sense. Since we have set-based operators now, it makes
        #       sense.
        if self.meta_type == 'list':
            if isinstance(other, (composite, dict, list, tuple)):
                other = composite(other)
                if len(self) == 0:
                    return other
                elif len(other) == 0:
                    return self
                elif other.meta_type == 'list':
                    return composite(self._list + other._list)
                elif other.meta_type == 'dict':
                    return composite([self._list, other._dict])
            else:
                return composite(self._list + [other])
        elif self.meta_type == 'dict':
            if isinstance(other, (composite, dict, list, tuple)):
                other = composite(other)
                if len(self) == 0:
                    return other
                elif len(other) == 0:
                    return self
                elif other.meta_type == 'list':
                    return composite([self._dict, other._list])
                elif other.meta_type == 'dict':
                    return self.union(other, recursive=True, overwrite=True)
            else:
                return composite([self._dict, other])
        return

    def __contains__(self, item):
        if self.meta_type == 'list':
            return item in self._list
        elif self.meta_type == 'dict':
            return item in self._dict

    def __eq__(self, other):
        if isinstance(other, composite):
            return self.json() == other.json()
        else:
            return self.json() == other

    def __ne__(self, other):
        return not (self == other)

    def intersection(self, other, recursive=True):
        """
        Recursively compute intersection of data. For dictionaries, items
        for specific keys will be reduced to unique items. For lists, items
        will be reduced to unique items. This method is meant to be analogous
        to set.intersection for composite objects.

        Args:
            other (composite): Other composite object to intersect with.
            recursive (bool): Whether or not to perform the operation recursively,
                for all nested composite objects.
        """
        if not isinstance(other, composite):
            raise AssertionError('Cannot intersect composite and {} types'.format(type(other)))
        
        if self.meta_type != other.meta_type:
            return composite({})

        if self.meta_type == 'list':
            keep = []
            for item in self._list:
                if item in other._list:
                    if recursive and isinstance(item, composite):
                        keep.extend(item.intersection(other.index(item), recursive=True))
                    else:
                        keep.append(item)
            return composite(keep)
        elif self.meta_type == 'dict':
            keep = {}
            for key in self._dict:
                item = self._dict[key]
                if key in other._dict:
                    if recursive and \
                       isinstance(item, composite) and \
                       isinstance(other.get(key), composite):
                       keep[key] = item.intersection(other.get(key), recursive=True)
                    elif item == other[key]:
                        keep[key] = item
            return composite(keep)
        return

    def difference(self, other, recursive=True):
        """
        Recursively compute difference of data. For dictionaries, items
        for specific keys will be reduced to differences. For lists, items
        will be reduced to differences. This method is meant to be analogous
        to set.difference for composite objects.

        Args:
            other (composite): Other composite object to difference with.
            recursive (bool): Whether or not to perform the operation recursively,
                for all nested composite objects.
        """
        if not isinstance(other, composite):
            raise AssertionError('Cannot difference composite and {} types'.format(type(other)))
        
        if self.meta_type != other.meta_type:
            return self

        if self.meta_type == 'list':
            keep = []
            for item in self._list:
                if item not in other._list:
                    if recursive and isinstance(item, composite):
                        keep.extend(item.difference(other.index(item), recursive=True))
                    else:
                        keep.append(item)
            return composite(keep)
        elif self.meta_type == 'dict':
            keep = {}
            for key in self._dict:
                item = self._dict[key]
                if key in other._dict:
                    if recursive and \
                       isinstance(item, composite) and \
                       isinstance(other.get(key), composite):
                       keep[key] = item.difference(other.get(key), recursive=True)
                    elif item != other[key]:
                        keep[key] = item
                else:
                    keep[key] = item
            return composite(keep)
        return

    def union(self, other, recursive=True, overwrite=False):
        """
        Recursively compute union of data. For dictionaries, items
        for specific keys will be combined into a list, depending on the
        status of the overwrite= parameter. For lists, items will be appended
        and reduced to unique items. This method is meant to be analogous
        to set.union for composite objects.

        Args:
            other (composite): Other composite object to union with.
            recursive (bool): Whether or not to perform the operation recursively,
                for all nested composite objects.
            overwrite (bool): Whether or not to overwrite entries with the same
                key in a nested dictionary. 
        """
        if not isinstance(other, composite):
            raise AssertionError('Cannot union composite and {} types'.format(type(other)))
        
        if self.meta_type != other.meta_type:
            return composite([self, other])

        if self.meta_type == 'list':
            keep = []
            for item in self._list:
                keep.append(item)
            for item in other._list:
                if item not in self._list:
                    keep.append(item)
            return composite(keep)
        elif self.meta_type == 'dict':
            keep = {}
            for key in list(set(list(self._dict.keys()) + list(other._dict.keys()))):
                left = self._dict.get(key)
                right = other._dict.get(key)
                if recursive and \
                   isinstance(left, composite) and \
                   isinstance(right, composite):
                    keep[key] = left.union(right, recursive=recursive, overwrite=overwrite)
                elif left == right:
                    keep[key] = left
                elif left is None:
                    keep[key] = right
                elif right is None:
                    keep[key] = left
                elif overwrite:
                    keep[key] = right
                else:
                    keep[key] = composite([left, right])
            return composite(keep)
        return

    def index(self, item):
        """
        Return index containing value.
        """
        return self._list.index(item)

    def get(self, *args, **kwargs):
        """
        Return item or None, depending on if item exists. This is
        meant to be similar to dict.get() for safe access of a property.
        """
        return self._dict.get(*args, **kwargs)

    def pop(self, *args, **kwargs):
        """
        Return item or None, depending on if item exists. This is
        meant to be similar to dict.pop() for safe access of a property.
        """
        return self._dict.pop(*args, **kwargs)

    def update(self, other):
        """
        Update internal dictionary object. This is meant to be an
        analog for dict.update().
        """
        if self.meta_type == 'list':
            raise AssertionError('Cannot update object of `list` base type!')
        elif self.meta_type == 'dict':
            self._dict = dict(self + composite(other))
            return

    def keys(self):
        """
        Return keys for object, if they are available.
        """
        if self.meta_type == 'list':
            return None
        elif self.meta_type == 'dict':
            return self._dict.keys()

    def items(self):
        """
        Return keys for object, if they are available.
        """
        if self.meta_type == 'list':
            return self._list
        elif self.meta_type == 'dict':
            return self._dict.items()

    def values(self):
        """
        Return keys for object, if they are available.
        """
        if self.meta_type == 'list':
            return self._list
        elif self.meta_type == 'dict':
            return self._dict.values()

    def append(self, item):
        """
        Append to object, if object is list.
        """
        if self.meta_type == 'dict':
            raise AssertionError('Cannot append to object of `dict` base type!')
        if self.meta_type == 'list':
            self._list.append(item)
        return

    def extend(self, item):
        """
        Extend list from object, if object is list.
        """
        if self.meta_type == 'dict':
            raise AssertionError('Cannot extend to object of `dict` base type!')
        if self.meta_type == 'list':
            self._list.extend(item)
        return

    def json(self):
        """
        Return JSON representation of object.
        """
        if self.meta_type == 'list':
            ret = []
            for dat in self._list:
                if not isinstance(dat, composite):
                    ret.append(dat)
                else:
                    ret.append(dat.json())
            return ret

        elif self.meta_type == 'dict':
            ret = {}
            for key in self._dict:
                if not isinstance(self._dict[key], composite):
                    ret[key] = self._dict[key]
                else:
                    ret[key] = self._dict[key].json()
            return ret

    def write_json(self, fh, pretty=True):
        """
        Write composite object to file handle in JSON format.

        Args:
            fh (file): File handle to write to.
            pretty (bool): Sort keys and indent in output.
        """
        sjson = json.JSONEncoder().encode(self.json())
        if pretty:
            json.dump(json.loads(sjson), fh, sort_keys=True, indent=4)
        else:
            json.dump(json.loads(sjson), fh)
        return

    def write_yaml(self, fh):
        """
        Write composite object to file handle in YAML format.

        Args:
            fh (file): File handle to write to.
        """
        yaml.dump(self.json(), fh)
        return

    def write(self, fh, pretty=True):
        """
        API niceness defaulting to composite.write_json().
        """
        return self.write_json(fh, pretty=pretty)


# data management
# -----------------
class filetree(object):
    """
    Data structure for traversing directory structure and creating object for
    accessing relative file paths.

    .. NOTE: The filetree is completely walked through when this object is
        instantiated, so expect object creation for large trees to be
        relatively expensive.

    Args:
        directory (str): Directory to build filetree from.
        ignore (str): Regular expression with items to ignore. If you wish
            to recurse through all directories (including hidden directories),
            set ignore=None. By default, this is set to "^[._]" (i.e. any files
            beginning with "." or "_").

    Example:
        >>> data = filetree('mydir')
        >>> print data
        mydir/
             one/
                two.txt
                three.json
            two/
                three/
                      four.txt
                five six/
                         seven.txt
                eight.config
        >>> print data.one['two.txt']
        /full/path/to/mydir/one/two.txt
        >>> print data.two.three['four.txt']
        /full/path/to/mydir/two/three/four.txt
        >>> print data.two['five six']['eight.config']
        /full/path/to/mydir/two/five six/eight.config
    """

    def __init__(self, directory, ignore=r"^[._]", regex=r".*"):
        self.ignore = ignore
        self.regex = regex
        self._data = {}
        self.root = os.path.realpath(directory)
        if os.path.isdir(directory):
            for item in os.listdir(self.root):
                if ignore is not None:
                    if re.search(ignore, item):
                        continue
                fullpath = os.path.realpath(os.path.join(self.root, item))
                if os.path.isdir(fullpath):
                    self._data[os.path.basename(fullpath)] = filetree(fullpath, ignore=ignore, regex=regex)
                else:
                    if re.search(regex, fullpath):
                        self._data[os.path.basename(fullpath)] = fullpath
        else:
            for fi in glob.glob(directory):
                fullpath = os.path.realpath(fi)
                self._data[os.path.basename(fullpath)] = fullpath
        self._filelist = []
        return

    def __len__(self):
        return len(self._data)

    def __str__(self):
        """
        .. NOTE:: This needs to be completed -- print filetree
        """
        def jstr(data, tab=''):
            res = ''
            for item in data:
                if isinstance(data[item], basestring):
                    res += tab + item + '\n'
                else:
                    res += tab + item + '/\n'
                    res += jstr(data[item], tab=tab+'\t')
            return res
        return jstr(self.json())

    def __iter__(self):
        for item in self._data:
            yield self._data[item]

    def __getattr__(self, name):
        if name not in self._data:
            raise AttributeError('filetree object has no attribute {}!'.format(name))
        return self._data[name]

    def __getitem__(self, item):
        if item not in self._data:
            raise KeyError('filetree object has no attribute {}!'.format(item))
        return self._data[item]

    def __contains__(self, item):
        if item in self._data:
            return True
        item = item.replace(self.root, '')
        item = re.sub(r"^[/\\]", "", item)
        subpaths = item.split("/")
        idx, cdata = 0, self
        try:
            while idx < len(subpaths):
                cdata = cdata[subpaths[idx]]
                idx += 1
        except KeyError:
            return False
        return True

    def __eq__(self, other):
        sf = sorted(self.filelist())
        of = sorted(other.filelist())
        if len(sf) != len(of):
            return False
        for i in range(0, len(sf)):
            if sf[i] != of[i]:
                return False
        return True

    def get(self, item):
        """
        Safe way to get items, similar to __dict__.get().

        Args:
            item (str): Item to get in file tree.
        """
        return self._data.get(item)

    def json(self):
        """
        Return JSON representation of object.
        """
        data = {}
        for item in self._data:
            if isinstance(self._data[item], filetree):
                data[item] = self._data[item].json()
            else:
                data[item] = self._data[item]
        return data

    @depricated_name('filelist()')
    def files(self):
        return self.filelist()

    def filelist(self):
        """
        Return list of files in filetree.
        """
        if len(self._filelist) == 0:
            for item in self._data:
                if isinstance(self._data[item], filetree):
                    self._filelist.extend(self._data[item].filelist())
                else:
                    self._filelist.append(self._data[item])
        return self._filelist

    def prune(self, regex=r".*"):
        """
        Prune leaves of filetree according to specified
        regular expression.

        Args:
            regex (str): Regular expression to use in pruning tree.
        """
        return filetree(self.root, ignore=self.ignore, regex=regex)
