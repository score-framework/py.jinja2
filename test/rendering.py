from .init import init_score
import unittest.mock
import pytest
import jinja2
from score.tpl import TemplateNotFound


def test_echo():
    score = init_score()
    assert score.tpl.render('echo.jinja2', {'data': 'foo'}) == 'foo'
    assert score.tpl.render('echo.jinja2', {'data': 'bar'}) == 'bar'


def test_escaping():
    score = init_score()
    assert score.tpl.render('echo.jinja2', {'data': '<'}) == '&lt;'
    assert score.tpl.render('echo.jinja2', {'data': '>'}) == '&gt;'


def test_non_escaping_1():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/html'].extensions.remove('jinja2')
    score.tpl.filetypes['text/plain'].extensions.append('jinja2')
    score._finalize()
    assert score.tpl.render('echo.jinja2', {'data': '<'}) == '<'


def test_non_escaping_2():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/css'].extensions.append('css')
    score._finalize()
    assert score.tpl.mimetype('echo.css.jinja2') == 'text/css'
    assert score.tpl.render('echo.css.jinja2', {'data': '<'}) == '<'


def test_non_escaping_3():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score._finalize()
    assert score.tpl.render('echo.jinja2.tpl', {'data': 'foo'}) == 'foo'
    assert score.tpl.render('echo.jinja2.tpl', {'data': '<'}) == '&lt;'


def test_string_rendering():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ data }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl', {'data': 'foo'}) == 'foo'
    loader.load.assert_called_once_with('foo.jinja2.tpl')
    assert score.tpl.render('foo.jinja2.tpl', {'data': '<'}) == '&lt;'


def test_function():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl', {'func': lambda: 'foo'}) == 'foo'
    loader.load.assert_called_once_with('foo.jinja2.tpl')
    assert score.tpl.render('foo.jinja2.tpl', {'func': lambda: '<'}) == '&lt;'


def test_loader():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score._finalize()
    with pytest.raises(TemplateNotFound):
        score.tpl.render('foo.jinja2.tpl')


def test_global():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/html'].add_global('data', 'foo!')
    score._finalize()
    assert score.tpl.render('echo.jinja2') == 'foo!'


def test_global_with_loader():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score.tpl.filetypes['text/html'].add_global('func', lambda: 'foo!')
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl') == 'foo!'
    loader.load.assert_called_once_with('foo.jinja2.tpl')


def test_escaped_global_function():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score.tpl.filetypes['text/html'].add_global('func', lambda: '<')
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl') == '&lt;'
    loader.load.assert_called_once_with('foo.jinja2.tpl')


def test_unescaped_global_function():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score.tpl.filetypes['text/html'].add_global('func', lambda: '<',
                                                escape=False)
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl') == '<'
    loader.load.assert_called_once_with('foo.jinja2.tpl')


def test_missing_global():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    # Note: adding global for mimetype text/plain, not text/html:
    score.tpl.filetypes['text/plain'].add_global('func', lambda: 'foo!')
    score._finalize()
    loader.load.assert_not_called()
    with pytest.raises(jinja2.UndefinedError):
        score.tpl.render('foo.jinja2.tpl')
