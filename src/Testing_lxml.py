
import lxml
import lxml.etree
import lxml.html
from StringIO import StringIO

xhtml = '<!DOCTYPE html PUBLIC "-//W3C/DTD XHTML 1.0 Transitional//EN"\
         "http://www.w3c.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\
         <div><br />This is a simple test</div>'
         
xhtml2 = '<div><br />This is a simple test</div>'

xmlparser = lxml.etree.XMLParser(dtd_validation=True, load_dtd=True, recover=True, no_network=False)
htmlparser = lxml.etree.HTMLParser(recover=True, no_network=False)    

xhtmlTree0 = lxml.etree.parse(StringIO(xhtml), parser=htmlparser)
xhtmlTree1 = lxml.etree.XML(xhtml, parser=xmlparser)
xhtmlTree2 = lxml.etree.HTML(xhtml)
xhtmlTree3 = lxml.html.document_fromstring(xhtml, parser=htmlparser)
xhtmlTree4 = lxml.html.parse(StringIO(xhtml), parser=htmlparser)

print(lxml.html.tostring(xhtmlTree0, method='xml'))
print(lxml.etree.tostring(xhtmlTree1))
print(lxml.etree.tostring(xhtmlTree2))
print(lxml.html.tostring(xhtmlTree1))
print(lxml.html.tostring(xhtmlTree2))
print(lxml.etree.tostring(xhtmlTree3))
print(lxml.html.tostring(xhtmlTree3), )
print("\n")
print(lxml.etree.tostring(xhtmlTree4))    
print(lxml.etree.tostring( xhtmlTree4.getroot() ))
print(xhtmlTree4.getroot().tag)
print(xhtmlTree4.docinfo.doctype)
help(xhtmlTree4.docinfo)

    