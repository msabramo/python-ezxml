import sys
import unittest
import lxml.objectify
import ezxml


class XMLTests(unittest.TestCase):

    def get_books_xml(self):
        return """
            <?xml version="1.0" encoding="utf-8"?>
            <Books>
                <Items>
                    <Item><ISBN>0321558235</ISBN></Item>
                    <Item><ISBN>9780321558237</ISBN></Item>
                </Items>
            </Books>
            """.strip()

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
            """.strip()

    def get_pricing_xml(self):
        return """
            <ProductPricing>
                <ResponseHeader/>
                <Items>
                    <Item><BiblioId>15536985</BiblioId></Item>
                    <Item><BiblioId>16432444</BiblioId></Item>
                </Items>
            </ProductPricing>
            """.strip()

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
            """.strip()

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
            """.strip()

    def test_books_xml(self):
        for objectifier in (lxml.objectify, ezxml):
            try:
                obj = objectifier.fromstring(self.get_books_xml())
                # print('objectifier = %r; obj = %r' % (objectifier, obj))
                self.assertEqual(obj.Items.Item[0].ISBN, int('0321558235'))
                self.assertEqual(obj.Items.Item[1].ISBN, int('9780321558237'))
            except AttributeError as e:
                self.fail("Failed tests (with objectifier = %r): %s" % (objectifier, e))

    def test_people_xml(self):
        for objectifier in (lxml.objectify, ezxml):
            try:
                obj = objectifier.fromstring(self.get_people_xml())
                # print('objectifier = %r; obj = %r' % (objectifier, obj))
                self.assertEqual(obj.Person[0].Name, 'Marc')
                self.assertEqual(obj.Person[0].Age, 37)
                self.assertEqual(obj.Person[1].Name, 'Zach')
                self.assertEqual(obj.Person[1].Age, 3)
            except (AssertionError, AttributeError) as e:
                self.fail("Failed tests (with objectifier = %r): %s" % (objectifier, e))

    def test_pricing_xml(self):
        for objectifier in (lxml.objectify, ezxml):
            try:
                obj = objectifier.fromstring(self.get_pricing_xml())
                # print('objectifier = %r; obj = %r' % (objectifier, obj))
                self.assertEqual(obj.Items.Item[0].BiblioId, int('15536985'))
                self.assertEqual(obj.Items.Item[1].BiblioId, int('16432444'))
            except AttributeError as e:
                self.fail("Failed tests (with objectifier = %r): %s" % (objectifier, e))

    def test_plist_xml(self):
        for objectifier in (lxml.objectify, ezxml):
            try:
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
            except (AttributeError, AssertionError) as e:
                sys.stderr.write("Failed tests (with objectifier = %r): %s\n" % (objectifier, e))
                raise

    def test_sample_xhtml(self):
        for objectifier in (lxml.objectify, ezxml):
            try:
                obj = objectifier.fromstring(self.get_sample_xhtml())
                # print('objectifier = %r; obj = %r' % (objectifier, obj))
                self.assertEqual(obj.head.title, 'XHTML 1.0: The Extensible HyperText Markup Language')
                self.assertEqual(obj.body.div[0].a, 'table of contents')
                self.assertEqual(obj.body.div[1].p[1], 'Some more stuff')
                self.assertEqual(obj.body.div[1].p[2], 'And yet more stuff')
            except (AttributeError, AssertionError) as e:
                sys.stderr.write("Failed tests (with objectifier = %r): %s\n" % (objectifier, e))
                raise
