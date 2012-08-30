try:
    import simplejson as json
except ImportError:
    import json

try:
    import xml.etree.cElementTree as ElementTree
except ImportError:
    import xml.etree.ElementTree as ElementTree


class ObjectifiedElement(object):

    def __init__(self, *args):
        if len(args) > 0:
            if isinstance(args[0], basestring):
                text = args[0]
            else:
                raise TypeError("Invalid child type: %r" % type(args[0]))
        else:
            text = None

        self.tag = self.__class__.__name__
        self._children = []
        self._parent = None
        self._text = text

    def __str__(self):
        if self.text:
            return self.text
        else:
            return ''

    def __repr__(self):
        return super(ObjectifiedElement, self).__repr__().replace(
            '<ezxml.%s object' % self.__class__.__name__,
            '<Element %s' % self.tag)

    def getparent(self):
        return self._parent

    def getchildren(self):
        return self._children

    def countchildren(self):
        return len(self.getchildren())

    def append(self, child):
        child._parent = self
        self._children.append(child)

    def __setattr__(self, attr_name, value):
        if attr_name == 'text':
            raise TypeError("attribute %r of %r objects is not writable"
                % (attr_name, self.__class__.__name__))

        super(ObjectifiedElement, self).__setattr__(attr_name, value)

    @property
    def text(self):
        return self._text


class ObjectifiedDataElement(ObjectifiedElement):

    # def __init__(self, text=None):
    #     super(ObjectifiedDataElement, self).__init__()
    #     self._text = text

    # def __unicode__(self):
    #     if self.text:
    #         return self.text
    #     else:
    #         return u''

    def __repr__(self):
        return unicode(self)


class StringElement(ObjectifiedDataElement):

    def __repr__(self):
        if self.text:
            return repr(str(self))
        else:
            return repr(u'')


def arrayify_etree(e):
    children = e.getchildren()

    if len(children) == 0:
        try:
            return {e.tag: int(e.text)}
        except (TypeError, ValueError):
            return {e.tag: e.text}
    else:
        d = {}

        # Merge data from child nodes into one dict
        for x in children:
            for k, v in arrayify_etree(x).items():
                if k in d:
                    if isinstance(d[k], list):
                        d[k].append(v)
                    else:
                        d[k] = [d[k], v]
                else:
                    d[k] = v

        return {e.tag: d}


class Objectifier(object):
    def __init__(self, response_data):
        if type(response_data) == list:
            if self.is_list_of_2_element_tuples(response_data):
                self.response_data = dict(response_data)
            else:
                self.response_data = response_data
        else:
            try:
                self.response_data = json.loads(response_data)
            except ValueError:
                try:
                    self.response_data = arrayify_xml(response_data)
                except ElementTree.ParseError:
                    self.response_data = response_data
            except TypeError:
                self.response_data = response_data

    def is_list_of_2_element_tuples(self, input):
        if not isinstance(input, list):
            return False

        for item in input:
            if not isinstance(item, tuple) or len(item) != 2:
                return False

        return True

    @staticmethod
    def objectify_if_needed(response_data):
        """
        Returns an objectifier object to wrap the provided response_data.
        """
        if hasattr(response_data, 'pop'):
            return Objectifier(response_data)
        return response_data

    def __dir__(self):
        try:
            return self.response_data.keys()
        except AttributeError:
            return []

    def __repr__(self):
        try:
            return "<Objectifier#dict {}>".format(" ".join(["%s=%s" % (k, type(v).__name__)
                for k, v in self.response_data.iteritems()]))
        except AttributeError:
            try:
                return "<Objectifier#list elements:{}>".format(len(self.response_data))
            except TypeError:
                return self.response_data

    def __contains__(self, k):
        return k in self.response_data

    def __len__(self):
        return len(self.response_data)

    def __iter__(self):
        """
        Provides iteration functionality for the wrapped object.
        """
        try:
            for k, v in self.response_data.iteritems():
                yield (k, Objectifier.objectify_if_needed(v))
        except AttributeError:
            try:
                for i in self.response_data:
                    yield Objectifier.objectify_if_needed(i)
            except TypeError:
                raise StopIteration

    def __getitem__(self, k):
        try:
            return Objectifier.objectify_if_needed(self.response_data[k])
        except TypeError:
            return None

    def __getattr__(self, k):
        if k in self.response_data:
            return Objectifier.objectify_if_needed(self.response_data[k])
        return None


def fromstring(xml_str):
    etree = ElementTree.fromstring(xml_str)

    root = arrayify_etree(etree)
    children = root.items()[0][1]

    return Objectifier(children)
