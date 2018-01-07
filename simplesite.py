"""
simplesite.py
Author: Adam Beagle

DESCRIPTION:

Minimal static site generator using jinja2 for templating and webassets for
minimization, etc.

See README.md for more information and API.
"""
from os import makedirs
from os.path import dirname, exists, join, normpath, splitext
from shutil import copy2, copytree, ignore_patterns, rmtree
from jinja2 import Environment, FileSystemLoader, select_autoescape

# Config
DEFAULT_OUTPUT_PATH = 'output/'
DEFAULT_STATIC_ROOT = 'static/'
DEFAULT_TEMPLATE_PATH = 'templates/'

class Page:
    def __init__(self, filename, output_path='', output_filename=None, **context):
        """
        filename is name of template file relative to template root.
        
        output_path is additional path information, assumed to be relative to
        an output root defined elsewhere. Default is blank.
        
        output_filename allows the file name of the output file to be specified.
        If unspecified, defaults to filename.
        
        Variables defined in context are sent to jinja2.Template.render() as
        template context.
        
        Example:
        
          Page('x.html', output_path='folder/', output_filename='y.html')
          would load a template called 'x.html' and set self.output as 
          'folder/y.html'
        """
        self.context = context
        self._filename = filename
        
        # Safeguard in case other False-equivalent values for output_path
        # passed (it's used with os.path.join later)
        if not output_path:
            output_path = ''
        
        if not output_filename:
            output_filename = filename
            
        self._output = join(output_path, output_filename)
        
    @property
    def filename(self):
        return self._filename
    
    @property
    def output(self):
        return self._output
        
class PrettyURLsPage(Page):
    """
    Facilitates creation of URL schemas that allow navigation by directory 
    rather than specific filename (via index.html files).
    
    The filename of a Page (sans extension) becomes the directory it is
    contained in, and the page itself is output as 'index.html'
    
    Example:
      PrettyURLsPage('some-page.html') results in a page with self.output
      set to 'some-page/index.html'.
    """
    def __init__(self, filename, **context):
        """Parameters work same as corresponding Page constructor parameters"""
        name = splitext(filename)[0]
        super().__init__(filename, name + '/', 'index.html', **context)

class TemplateRenderer:
    """ 
    Helper class to ease rendering of pages with jinja2, in conjunction with
    the Page classes above.
    
    Has one public method: render(pages) which accepts a single Page object
    (or instance of subclass of Page), or an iterable of Page objects to render.
    """
    
    def __init__(self, 
            template_path=DEFAULT_TEMPLATE_PATH, 
            output_path=DEFAULT_OUTPUT_PATH
        ):
        """
        template_path is sent to jinja2's FileSystemLoader to search for templates.
        Defaults to DEFAULT_TEMPLATE_PATH
        
        output_path is the path to the root output folder. 
        The directory will be created if it does not exist.
        Defaults to DEFAULT_OUTPUT_PATH
        """
        
        # False-equivalent values treated as empty string for path purposes
        self._template_path = template_path if template_path else ''
        self._output_path = output_path if output_path else ''

        self._env = Environment(
            loader=FileSystemLoader(self._template_path),
            autoescape=select_autoescape(['html', 'htm', 'xml'])
        )
        
    def render(self, pages):
        if isinstance(pages, Page):
            pages = (Page, )

        for page in pages:
            template = self._env.get_template(page.filename)
            rendered = template.render(page.context)
            full_output_path = join(self._output_path, page.output)
            page_dir = dirname(full_output_path)
            
            # Create output directories as needed
            if page_dir and not exists(page_dir):
                makedirs(page_dir)
            
            with open(full_output_path, 'w') as f:
                f.write(rendered)
                
class SimpleStaticSiteGenerator:
    """ 
    Minimal static site generator that renders HTML from templates using jinja2,
    and copies static files into an output directory.
    """
    def __init__(self, 
            pages=None, 
            template_path=DEFAULT_TEMPLATE_PATH,
            output_path=DEFAULT_OUTPUT_PATH, 
            static_root=DEFAULT_STATIC_ROOT,
            static_output_root=None,
            static_map=None
        ):
        """
        template_path is sent to jinja2's FileSystemLoader to search for templates.
        Defaults to DEFAULT_TEMPLATE_PATH.
        
        output_path is the path to the root output folder. 
        The directory will be created if it does not exist.
        Defaults to DEFAULT_OUTPUT_PATH.
        """
        # False-equivalent values treated as empty string for path purposes
        self._template_path = template_path if template_path else ''
        self._output_path = output_path if output_path else ''
        self._static_root = static_root if static_root else ''
        
        if static_output_root:
            self._static_output_root = static_output_root
        else:
            self._static_output_root = self._static_root

        self._renderer = TemplateRenderer(
            self._template_path, 
            self._output_path
        )
        
        # Force pages to be a list if None or empty container because it's assumed
        # to be a container
        if not pages:
            pages = []
            
        if not static_map:
            static_map = {}
            
        self.pages = pages
        self.static_map = static_map
        
    def output_site(self):
        """
        Render and write the site, as determined by the pages and path
        properties of the instance.
        """
        # Render and output pages
        self._renderer.render(self.pages)
        
        # Copy static files
        # Can assume output_path exists because created in renderer
        self._copy_static()
        
    def _copy_static(self):
        static_output_path = join(self._output_path, self._static_output_root)
        
        # Existing static files must be removed or copytree will fail
        # TODO only update/add static files as needed?
        if exists(static_output_path):
            rmtree(static_output_path)
        
        copytree(
            self._static_root, 
            static_output_path, 
            ignore=ignore_patterns(*self.static_map.keys())
        )
        
        for srcfile, relative_dest in self.static_map.items():
            src = normpath(join(self._static_root, srcfile))
            dest = normpath(join(static_output_path, relative_dest))
            copy2(src, dest)
        
