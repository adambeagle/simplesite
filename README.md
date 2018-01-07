# simplesite v0.1

*Author: Adam Beagle*

## Description

`simplesite` is a minimal static site generator written in Python, with jinja2 templating. It is an abstraction layer on top of jinja2 which automates common tasks. It is ideal for use in small (but multi-page) projects, mockups, quick educational examples, etc.

This project is still in early development, and does not yet have a full test suite.

## Requirements

* python 3.x
* Packages as defined in `requirements.txt` (`pip install -r requirements.txt`)

## Installation

1. Clone this repository (`git clone https://github.com/adambeagle/simplesite.git`)
2. Navigate to the `simplesite` directory git created and install the package with pip (`pip install . -r requirements.txt`)

## Quickstart

Given the following directory structure:
    
    project/
        project.py
        templates/
            base.html
            index.html
            example.html
        static/
            css/
                style.css
            images/
                x.jpg
                favicon.ico
                
Assume `base.html` is a base template used by the other two templates, and all templates are valid jinja2 templates.

The following code will generate a site from these files using the default settings:

    from simplesite import Page, SimpleStaticSiteGenerator
    
    pages = (
        Page('index.html'),
        Page('example.html'),
    )
    
    sitegen = SimpleStaticSiteGenerator(pages=pages, static_map={'images/favicon.ico': '../'})
    sitegen.output_site()
    
The result would be the following:

    project/
        project.py
        templates/
            [...]
        static/
            [...]
        output/
            index.html
            example.html
            favicon.ico
            static/
                css/
                    style.css
                images/
                    x.jpg
                    
                    
The resulting site is placed in `output/`. The static files are copied in their existing directory structure into the output folder.

## Example

To view an example site which uses this package, see the [landonhotel repository](https://github.com/adambeagle/landonhotel).

## API

The `simplesite` module provides the following classes:

### `class Page`

A single web page is represented by a `Page` object (or an object which subclasses `Page`). Page objects should only be created for deepest-nested templates, i.e. the finished pages to be copied to output. Template inheritance is accomplished via `jinja2`'s `{% extends %}` directive.

#### Constructor 

`Page(filename, output_path='', output_filename=None, **context)`

* `filename` is the filename (possibly including path) to the template file. It is passed to jinja2's `Environment.get_template()` method as `name`.

* `output_path` is additional path information, assumed to be relative to the output root defined elsewhere. Default is blank, which represents being placed in the root output folder. Use this setting to place the page in a nested directory in the output.
        
* `output_filename` allows the file name of the output file to be specified. If unspecified, defaults to filename.

* `context` is named parameters sent to jinja2's `Template.render()` 

#### Properties

* context

Context sent to the template. Defaults to an empty dictionary if no context sent to constructor. Readable/writable, but setting this to anything not acceptable as context by jinja2's `Template.render()` may result in an exception.

* filename (read-only)

Read-only copy of the constructor's `filename` parameter.

* output (read-only)

The full output path of the page.

#### Example:
        
`Page('x.html', output_path='folder/', output_filename='y.html', some_variable=1)` would load a template called `'x.html'`, set the `output` property to `'folder/y.html'`, and provide a variable named `some_variable` to the template as context.

### `class PrettyURLsPage(Page)`

One subclass of `Page` is provided. The `PrettyURLsPage` facilitates creation of URL schemas that allow navigation by directory rather than specific filename (via index.html files).
    
The filename of a Page (sans extension) becomes the directory it is contained in, and the page itself is output as `'index.html'`
    
#### Example:

`PrettyURLsPage('some-page.html')` results in a page with an `output` property set to `'some-page/index.html'`.

### `class SimpleStaticSiteGenerator`

This class is the primary helper class of the module, which represents a site and handles rendering and writing the output based on given Pages and path parameters.

#### Constructor

    SimpleStaticSiteGenerator(
      pages=None, 
      template_path=DEFAULT_TEMPLATE_PATH,
      output_path=DEFAULT_OUTPUT_PATH, 
      static_root=DEFAULT_STATIC_ROOT,
      static_output_root=None, # defaults to static_root if not set
      static_map=None
    )
    
* `pages` is a container of objects which are instances of `Page`

* `template_path` is sent to jinja2's `FileSystemLoader` to search for templates. Defaults to `'templates/'`.

* output_path is the path to the root output folder, relative to the current working directory. The directory will be created if it does not exist. Defaults to `'output/'`.

* `static_root` is the path to where development static files are stored. Defaults to `'static/'`. 

* `static_output_root` is the root directory at which to save static files in output. Defaults to `static_root`.

* `static_map` is a mapping (assumed to be a dictionary) of specific static files and their desired destination in the output, relative to `static_output_root`. By default, static files are copied in their existing directory structure. Use this parameter to move or rename specific files.

#### Methods

* `output_site()`

Renders and writes the site, as determined by the pages and path properties of the instance.

#### Properties

* `pages`

    Readable/writable version of the `pages` parameter sent to the constructor.

* `static_map`

    Readable/writable version of the `static_map` parameter sent to the constructor.

### `class TemplateRenderer`

Helper class to ease rendering of pages with jinja2, in conjunction with the Page classes above. This class does not need to be touched if using `SimpleStaticSiteGenerator`, but may be useful to those who simply want to automate rendering with jinja2.

#### Constructor

`TemplateRenderer(template_path=DEFAULT_TEMPLATE_PATH, output_path=DEFAULT_OUTPUT_PATH)`

The constructor parameters work the same as the respective parameters in `SimpleStaticSiteGenerator`. 

#### Methods

* `render(pages)` 

    Accepts a single `Page` object (or instance of subclass of `Page`), or an iterable of `Page` objects to render and write to output.