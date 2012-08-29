from __future__ import with_statement

import contextlib
import sys

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import ezxml

objectifiers = [ezxml]

try:
    import lxml.objectify
    objectifiers.insert(0, lxml.objectify)
except ImportError:
    pass

from parameterizedtestcase import ParameterizedTestCase, ParameterizedTestMixin

def for_each_objectifier(test_method):
    """A test method decorator for running the test with each supported objectifier"""

    param_names = ["objectifier"]
    param_values = [(objectifier,) for objectifier in objectifiers]

    return ParameterizedTestCase.parameterize(param_names, param_values)(test_method)


class EZXMLTests(ParameterizedTestCase):

    @contextlib.contextmanager
    def assertRaisesChildTypeError(self, arg):
        with self.assertRaises(TypeError) as cm:
            yield cm

        if cm:
            self.assertEqual(str(cm.exception), "Invalid child type: %r" % type(arg))

    @contextlib.contextmanager
    def assertRaisesAttributeNotWritableError(self, attr_name, class_name):
        with self.assertRaises(TypeError) as cm:
            yield cm

        if cm:
            self.assertEqual(str(cm.exception), "attribute %r of %r objects is not writable" % (attr_name, class_name))

class FromStringTests(EZXMLTests):

    def get_books_xml(self):
        return """
            <?xml version="1.0" encoding="utf-8"?>
            <Books>
                <Items>
                    <Item><ISBN>0321558235</ISBN></Item>
                    <Item><ISBN>9780321558237</ISBN></Item>
                </Items>
            </Books>
            """.strip().encode('utf-8')

    def get_people_xml(self):
        return """
            <?xml version="1.0" encoding="utf-8"?>
            <People>
                <Person>
                    <Name>Marc</Name>
                    <Age>37</Age>
                </Person>
                <Person>
                    <Name>Zach</Name>
                    <Age>3</Age>
                </Person>
            </People>
            """.strip().encode('utf-8')

    def get_pricing_xml(self):
        return """
            <ProductPricing>
                <ResponseHeader/>
                <Items>
                    <Item><BiblioId>15536985</BiblioId></Item>
                    <Item><BiblioId>16432444</BiblioId></Item>
                </Items>
            </ProductPricing>
            """.strip().encode('utf-8')

    def get_plist_xml(self):
        return """
            <?xml version="1.0" encoding="UTF-8"?>
            <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
            <plist version="1.0">
            <dict>
                <key>BuildVersion</key>
                <string>1</string>
                <key>CFBundleShortVersionString</key>
                <string>1.1</string>
                <key>CFBundleVersion</key>
                <string>1.1</string>
                <key>ProjectName</key>
                <string>AutomatorActions</string>
                <key>SourceVersion</key>
                <string>270001000000000</string>
            </dict>
            </plist>
            """.strip().encode('utf-8')

    def get_sample_xhtml(self):
        # @todo I stripped out the xmlns stuff, because I don't know how to handle that with ElementTree yet

        return """
            <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "dtds/xhtml1-strict.dtd">
            <?xml-stylesheet href="W3C-PR.css" type="text/css"?>
            <html lang="en" xml:lang="en">
            <head>
            <title>XHTML 1.0: The Extensible HyperText Markup Language</title>
            <link rel="stylesheet" href="W3C-PR.css" type="text/css" />
            <style type="text/css">
            span.term { font-style: italic; color: rgb(0, 0, 192) }
            code {
                color: green;
                font-family: monospace;
                font-weight: bold;
            }
            </style>
            </head>
            <body>
            <div class="navbar">
              <a href="#toc">table of contents</a> 
              <hr />
            </div>
            <div class="head">
                <p><a href="http://www.w3.org/"><img class="head" src="w3c_home.gif" alt="W3C" /></a></p>
                <p>Some more stuff</p>
                <p>And yet more stuff</p>
            </div>
            </body>
            </html>
            """.strip().encode('utf-8')

    @for_each_objectifier
    def test_books_xml(self, objectifier):
        obj = objectifier.fromstring(self.get_books_xml())
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.Items.Item[0].ISBN, int('0321558235'))
        self.assertEqual(obj.Items.Item[1].ISBN, int('9780321558237'))

    @for_each_objectifier
    def test_people_xml(self, objectifier):
        obj = objectifier.fromstring(self.get_people_xml())
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.Person[0].Name, 'Marc')
        self.assertEqual(obj.Person[0].Age, 37)
        self.assertEqual(obj.Person[1].Name, 'Zach')
        self.assertEqual(obj.Person[1].Age, 3)

    @for_each_objectifier
    def test_pricing_xml(self, objectifier):
        obj = objectifier.fromstring(self.get_pricing_xml())
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.Items.Item[0].BiblioId, int('15536985'))
        self.assertEqual(obj.Items.Item[1].BiblioId, int('16432444'))

    @for_each_objectifier
    def test_plist_xml(self, objectifier):
        obj = objectifier.fromstring(self.get_plist_xml())
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.dict.key[0], 'BuildVersion')
        self.assertEqual(obj.dict.key[1], 'CFBundleShortVersionString')
        self.assertEqual(obj.dict.key[2], 'CFBundleVersion')
        self.assertEqual(obj.dict.key[3], 'ProjectName')
        self.assertEqual(obj.dict.key[4], 'SourceVersion')
        self.assertEqual(
            list(obj.dict.key),
            ['BuildVersion', 'CFBundleShortVersionString', 'CFBundleVersion', 'ProjectName', 'SourceVersion'])

    @for_each_objectifier
    def test_sample_xhtml(self, objectifier):
        obj = objectifier.fromstring(self.get_sample_xhtml())
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.head.title, 'XHTML 1.0: The Extensible HyperText Markup Language')
        self.assertEqual(obj.body.div[0].a, 'table of contents')
        self.assertEqual(obj.body.div[1].p[1], 'Some more stuff')
        self.assertEqual(obj.body.div[1].p[2], 'And yet more stuff')


class ObjectifiedElementTests(EZXMLTests):

    @for_each_objectifier
    def test_init_with_no_args(self, objectifier):
        obj = objectifier.ObjectifiedElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.tag, 'ObjectifiedElement')
        self.assertEqual(str(obj), '')
        # print("repr(obj) = %r" % repr(obj))
        self.assertTrue('<Element ObjectifiedElement' in repr(obj))

    @for_each_objectifier
    def test_init_with_string_arg(self, objectifier):
        obj = objectifier.ObjectifiedElement('Foo')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.tag, 'ObjectifiedElement')
        self.assertEqual(str(obj), 'Foo')
        # print("repr(obj) = %r" % repr(obj))
        self.assertTrue('<Element ObjectifiedElement' in repr(obj))

    @for_each_objectifier
    def test_init_with_float_arg(self, objectifier):
        arg = 3.14

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedElement(arg)

    @for_each_objectifier
    def test_init_with_int_arg(self, objectifier):
        arg = 34

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedElement(arg)

    @for_each_objectifier
    def test_init_with_tuple_arg(self, objectifier):
        arg = (34, 56)

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedElement(arg)

    @for_each_objectifier
    def test_init_with_none_arg(self, objectifier):
        arg = None

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedElement(arg)

    @for_each_objectifier
    def test_set_tag(self, objectifier):
        obj = objectifier.ObjectifiedElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        obj.tag = 'books'
        self.assertEqual(obj.tag, 'books')
        self.assertEqual(str(obj), '')
        # print("repr(obj) = %r" % repr(obj))
        self.assertTrue('<Element books' in repr(obj))
        self.assertEqual(obj.getparent(), None)
        self.assertEqual(obj.getchildren(), [])
        self.assertEqual(obj.countchildren(), 0)

    @for_each_objectifier
    def test_append_1(self, objectifier):
        obj = objectifier.ObjectifiedElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        obj.tag = 'books'
        book1 = objectifier.ObjectifiedElement()
        book1.tag = 'book'
        obj.append(book1)
        self.assertEqual(obj.getchildren(), [book1])
        self.assertEqual(obj.countchildren(), 1)
        self.assertEqual(book1.getparent(), obj)

    @for_each_objectifier
    def test_get_text_attribute(self, objectifier):
        obj = objectifier.ObjectifiedElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.text, None)

    @for_each_objectifier
    def test_set_text_attribute_not_writable(self, objectifier):
        obj = objectifier.ObjectifiedElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))

        with self.assertRaisesAttributeNotWritableError(attr_name='text', class_name='ObjectifiedElement'):
            obj.text = 'foobar'


class ObjectifiedDataElementTests(EZXMLTests):

    @for_each_objectifier
    def test_init_with_string_arg(self, objectifier):
        obj = objectifier.ObjectifiedDataElement('MyValue')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.tag, 'ObjectifiedDataElement')
        self.assertEqual(str(obj), 'MyValue')
        self.assertEqual(repr(obj), 'MyValue')
        self.assertEqual(obj.text, 'MyValue')

    @for_each_objectifier
    def test_init_with_float_arg(self, objectifier):
        arg = 3.14

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedDataElement(arg)

    @for_each_objectifier
    def test_init_with_int_arg(self, objectifier):
        arg = 34

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedDataElement(arg)

    @for_each_objectifier
    def test_init_with_tuple_arg(self, objectifier):
        arg = (34, 56)

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedDataElement(arg)

    @for_each_objectifier
    def test_init_with_none_arg(self, objectifier):
        arg = None

        with self.assertRaisesChildTypeError(arg):
            objectifier.ObjectifiedDataElement(arg)

    @for_each_objectifier
    def test_get_text_attribute(self, objectifier):
        obj = objectifier.ObjectifiedDataElement('MyValue')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.text, 'MyValue')

    @for_each_objectifier
    def test_set_text_attribute_not_writable(self, objectifier):
        obj = objectifier.ObjectifiedDataElement('MyValue')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))

        with self.assertRaisesAttributeNotWritableError(attr_name='text', class_name='ObjectifiedDataElement'):
            obj.text = 'foobar'

    @for_each_objectifier
    def test_fromstring(self, objectifier):
        obj = objectifier.fromstring("""<books><book><title>Biology</title></book><book><title>Math</title></book></books>""")
        # print('objectifier = %r; obj = %r' % (objectifier, obj))


class StringElementTests(EZXMLTests):

    @for_each_objectifier
    def test_init_with_no_arg(self, objectifier):
        obj = objectifier.StringElement()
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.tag, 'StringElement')
        self.assertEqual(str(obj), '')
        self.assertEqual(repr(obj), "u''")
        self.assertEqual(obj.text, None)

        # Setting the `tag` attribute shouldn't affect anything
        obj.tag = 'Foo'
        self.assertEqual(obj.tag, 'Foo')
        self.assertEqual(str(obj), '')
        self.assertEqual(repr(obj), "u''")
        self.assertEqual(obj.text, None)

    @for_each_objectifier
    def test_init_with_string_arg(self, objectifier):
        obj = objectifier.StringElement('MyValue')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))
        self.assertEqual(obj.tag, 'StringElement')
        self.assertEqual(str(obj), 'MyValue')
        self.assertEqual(repr(obj), "'MyValue'")
        self.assertEqual(obj.text, 'MyValue')

    @for_each_objectifier
    def test_init_with_float_arg(self, objectifier):
        arg = 3.14

        with self.assertRaisesChildTypeError(arg):
            objectifier.StringElement(arg)

    @for_each_objectifier
    def test_init_with_int_arg(self, objectifier):
        arg = 34

        with self.assertRaisesChildTypeError(arg):
            objectifier.StringElement(arg)

    @for_each_objectifier
    def test_init_with_tuple_arg(self, objectifier):
        arg = (34, 56)

        with self.assertRaisesChildTypeError(arg):
            objectifier.StringElement(arg)

    @for_each_objectifier
    def test_init_with_none_arg(self, objectifier):
        arg = None

        with self.assertRaisesChildTypeError(arg):
            objectifier.StringElement(arg)

    @for_each_objectifier
    def test_set_text_attribute_not_writable(self, objectifier):
        obj = objectifier.StringElement('MyValue')
        # print('objectifier = %r; obj = %r' % (objectifier, obj))

        with self.assertRaisesAttributeNotWritableError(attr_name='text', class_name='StringElement'):
            obj.text = 'foobar'
