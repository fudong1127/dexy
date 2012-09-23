from dexy.common import OrderedDict
from dexy.plugin import PluginMeta
import dexy.storage
import dexy.wrapper
import json
import os
import shutil

class Data:
    __metaclass__ = PluginMeta

    ALIASES = []
    DEFAULT_STORAGE_TYPE = 'generic'

    @classmethod
    def is_active(klass):
        return True

    @classmethod
    def retrieve(klass, key, ext, data_type, hashstring, storage_type, **kwargs):
        """
        Method to retrieve a Data object based on info stored in database.

        Optional kwags are passed to a RunParams instance.
        """
        wrapper = dexy.wrapper.Wrapper(**kwargs)
        data_class = klass.aliases[data_type]
        return data_class(key, ext, hashstring, wrapper, storage_type)

    def __init__(self, key, ext, hashstring, wrapper, storage_type=None):
        self.key = key
        self.ext = ext
        self.hashstring = hashstring
        self.wrapper = wrapper

        self.calculate_name()

        self.storage_type = storage_type or self.DEFAULT_STORAGE_TYPE
        storage_class = dexy.storage.Storage.aliases[self.storage_type]
        self.storage = storage_class(hashstring, ext, self.wrapper)

        self._data = None

        # Allow doing custom setup stuff in subclasses.
        self.setup()

    def setup(self):
        pass

    def calculate_name(self):
        name_without_ext = os.path.splitext(self.key)[0]
        self.name = "%s%s" % (name_without_ext, self.ext)

    def parent_dir(self):
        return os.path.dirname(self.name)

    def long_name(self):
        if "|" in self.key:
            return "%s%s" % (self.key.replace("|", "-"), self.ext)
        else:
            return self.name

    def basename(self):
        return os.path.basename(self.name)

    def web_safe_document_key(self):
        return self.long_name().replace("/", "--")

    def relative_path_to(self, relative_to):
        return os.path.relpath(relative_to, self.parent_dir())

    def relative_refs(self, relative_to_file):
        doc_dir = os.path.dirname(relative_to_file)
        return [
                os.path.relpath(self.key, doc_dir),
                os.path.relpath(self.long_name(), doc_dir),
                "/%s" % self.key,
                "/%s" % self.long_name()
        ]

class GenericData(Data):
    ALIASES = ['generic']
    DEFAULT_STORAGE_TYPE = 'generic'

    """
    Data in a single lump, which may be binary or text-based.
    """
    def save(self):
        self.storage.write_data(self._data)

    def set_data(self, data):
        """
        Set data to the passed argument and persist data to disk.
        """
        self._data = data
        self.save()

    def load_data(self):
        self._data = self.storage.read_data()

    def has_data(self):
        return self._data or self.storage.data_file_exists()

    def is_cached(self):
        return self.storage.data_file_exists()

    def __unicode__(self):
        return self.as_text()

    def __getattr__(self, key):
        if self.__dict__.has_key(key):
            return self.__dict__[key]
        else:
            if self.ext == '.json':
                return json.loads(self.data())[key]
            else:
                raise Exception("what's happening here")

    def filesize(self):
        if self.is_cached():
            return os.path.getsize(self.storage.data_file())

    def data(self):
        if not self._data:
            self.load_data()
        return self._data

    def as_text(self):
        return self.data().decode(encoding="utf-8")

    def as_sectioned(self):
        return {'1' : self.data()}

    def copy_from_file(self, filename):
        shutil.copyfile(filename, self.storage.data_file())

    def clear_data(self):
        self._data = None

    def output_to_file(self, filepath):
        """
        Write canonical output to a file. Parent directory must exist already.
        """
        self.storage.write_data(self.data(), filepath)

class SectionedData(GenericData):
    ALIASES = ['sectioned']
    DEFAULT_STORAGE_TYPE = 'jsonordered'

    def as_text(self):
        return "\n".join(v for v in self.data().values())

    def as_sectioned(self):
        return self.data()

    def keys(self):
        return self.data().keys()

    def output_to_file(self, filepath):
        """
        Write canonical output to a file.
        """
        with open(filepath, "wb") as f:
            f.write(self.as_text())

    def value(self, key):
        return self.data()[key]

    def __getitem__(self, key):
        return self.value(key)

    def __getattr__(self, key):
        if self.__dict__.has_item(key):
            return self.__dict__[key]
        else:
            return self.value(key)

class KeyValueData(GenericData):
    ALIASES  = ['keyvalue']
    DEFAULT_STORAGE_TYPE = 'sqlite3'

    def setup(self):
        self.storage.setup()

    def as_text(self):
        text = []
        for k, v in self.storage:
            text.append("%s: %s" % (k, v))
        return "\n".join(text)

    def as_sectioned(self):
        od = OrderedDict()
        for k, v in self.storage:
            od[k] = v
        return od

    def data(self):
        return self.as_sectioned()

    def value(self, key):
        return self.storage[key]

    def __getitem__(self, key):
        return self.value(key)

    def __getattr__(self, key):
        if self.__dict__.has_item(key):
            return self.__dict__[key]
        else:
            return self.value(key)

    def append(self, key, value):
        self.storage.append(key, value)

    def keys(self):
        return self.storage.keys()

    def save(self):
        self.storage.save()