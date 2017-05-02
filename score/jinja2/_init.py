# Copyright © 2015-2017 STRG.AT GmbH, Vienna, Austria
#
# This file is part of the The SCORE Framework.
#
# The SCORE Framework and all its parts are free software: you can redistribute
# them and/or modify them under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation which is in the
# file named COPYING.LESSER.txt.
#
# The SCORE Framework and all its parts are distributed without any WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE. For more details see the GNU Lesser General Public
# License.
#
# If you have not received a copy of the GNU Lesser General Public License see
# http://www.gnu.org/licenses/.
#
# The License-Agreement realised between you as Licensee and STRG.AT GmbH as
# Licenser including the issue of its valid conclusion and its pre- and
# post-contractual effects is governed by the laws of Austria. Any disputes
# concerning this License-Agreement including the issue of its valid conclusion
# and its pre- and post-contractual effects are exclusively decided by the
# competent court, in whose district STRG.AT GmbH has its registered seat, at
# the discretion of STRG.AT GmbH also the competent court, in whose district the
# Licensee has his registered seat, an establishment or assets.

from score.init import ConfiguredModule
from score.tpl import Renderer
from functools import wraps
import jinja2
import errno
import os


defaults = {
    'extension': 'jinja2',
    'cachedir': None,
}


def init(confdict, tpl):
    """
    Initializes this module acoording to the :ref:`SCORE module initialization
    guidelines <module_initialization>` with the following configuration keys:
    """
    conf = defaults.copy()
    conf.update(confdict)
    return ConfiguredJinja2Module(tpl, conf['extension'], conf['cachedir'])


class ConfiguredJinja2Module(ConfiguredModule):

    def __init__(self, tpl, extension, cachedir):
        import score.jinja2
        super().__init__(score.jinja2)
        self.tpl = tpl
        self.extension = extension
        self.cachedir = cachedir
        tpl.engines[extension] = self._create_renderer
        tpl.filetypes['text/html'].extensions.append(extension)

    def _create_renderer(self, tpl_conf, filetype):
        return Jinja2Renderer(self, tpl_conf, filetype)


class Jinja2Renderer(Renderer):

    def __init__(self, jinja2_conf, *args, **kwargs):
        self._jinja2_conf = jinja2_conf
        super().__init__(*args, **kwargs)
        self.env = self.build_environment()
        self.root_file_loader = jinja2.FileSystemLoader('/')

    def render_file(self, file, variables, path=None):
        """
        Renders given template *file* with the given *variables* dict.
        """
        try:
            tpl = self.root_file_loader.load(self.env, file)
        except jinja2.TemplateNotFound as e:
            raise FileNotFoundError(
                errno.ENOENT, os.strerror(errno.ENOENT), file) from e
        else:
            return tpl.render(variables)

    def render_string(self, string, variables, path=None):
        """
        Renders given template *string* with the given *variables* dict.
        """
        tpl = self.env.from_string(string)
        return tpl.render(variables)

    def build_environment(self):
        """
        Buids a :class:`jinja2.Environment` and registers all functions,
        filters and global variables. No need to call this function manually,
        an environment will be created automatically if it does not exist when
        accessing :attr:`.env`.
        """
        kwargs = {}
        if self._jinja2_conf.cachedir:
            kwargs['bytecode_cache'] =\
                jinja2.FileSystemBytecodeCache(self._jinja2_conf.cachedir)
        if self._tpl_conf.rootdirs:
            kwargs['loader'] = \
                jinja2.FileSystemLoader(self._tpl_conf.rootdirs)
        can_escape = self.filetype.mimetype in ('text/xml', 'text/html')
        env = jinja2.Environment(
            autoescape=can_escape,
            extensions=self.get_extensions(),
            undefined=jinja2.StrictUndefined,
            **kwargs,
        )
        if can_escape:
            for name, value, escape in self.filetype.globals:
                if not escape:
                    if callable(value):
                        @wraps(value)
                        def wrapped_callable(*args, **kwargs):
                            return jinja2.Markup(value(*args, **kwargs))
                        value = wrapped_callable
                    elif isinstance(value, str):
                        value = jinja2.Markup(value)
                env.globals[name] = value
        else:
            for name, value, escape in self.filetype.globals:
                env.globals[name] = value
        return env

    def get_extensions(self):
        """
        The extensions to register while generating the
        :class:`jinja2.Environment` in :meth:`.build_environment`.
        """
        return ['jinja2.ext.i18n', 'jinja2.ext.autoescape']
