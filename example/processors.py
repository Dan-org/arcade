import os

from django.conf import settings



### Sass Filter ### 
from scss import Scss
from compressor.filters.css_default import CssAbsoluteFilter



class SassFilter(CssAbsoluteFilter):
    compiler = Scss()

    def __init__(self, content, attributes, filter_type=None, filename=None):
        return super(SassFilter, self).__init__(content, filter_type=filter_type, filename=filename)

    def input(self, *args, **kwargs):
        compiler = Scss(
            search_paths=[os.path.dirname(self.filename)]
        )
        self.content = compiler.compile(self.content.encode('utf-8'))
        return super(SassFilter, self).input(*args, **kwargs)

