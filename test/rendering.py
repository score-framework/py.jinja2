from .init import init_score
import unittest.mock


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


def test_global_function():
    score = init_score(finalize=False)
    loader = unittest.mock.Mock()
    loader.load.return_value = (False, '{{ func() }}')
    score.tpl.loaders['tpl'].append(loader)
    score.tpl.filetypes['text/plain'].extensions.append('tpl')
    score.tpl.filetypes['text/plain'].add_global('func', lambda: 'foo!')
    score._finalize()
    loader.load.assert_not_called()
    assert score.tpl.render('foo.jinja2.tpl') == 'foo'
    loader.load.assert_called_once_with('foo.jinja2.tpl')
