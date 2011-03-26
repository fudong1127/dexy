import json
import dexy
import dexy.controller
import dexy.artifact
import dexy.document
import dexy.handler

import inspect
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers.agile import PythonLexer

py_lexer = PythonLexer()
fm = HtmlFormatter()

handler_info = {
    'artifact' : {},
    'document' : {},
    'handler' : {},
    'controller' : {}
}

klasses = {
    'controller' : dexy.controller.Controller,
    'artifact' : dexy.artifact.Artifact,
    'document' : dexy.document.Document,
    'handler' : dexy.handler.DexyHandler
}

for a, b in klasses.items():
    for k, m in inspect.getmembers(b):
        if inspect.ismethod(m):
            source = inspect.getsource(m.__func__)
            html_source = highlight(source, py_lexer, fm)
            handler_info[a][k] = html_source
        else:
            handler_info[a][k] = str(m)


f = open("dexy--source.json", "w")
json.dump(handler_info, f)
f.close()
