from score.init import init
from score.tpl import TemplateNotFound
import pytest
import os
import tempfile


def init_score(extra=None, *, finalize=True):
    conf = {
        'score.init': {
            'modules': [
                'score.tpl',
                'score.jinja2',
            ],
        },
        'tpl': {
            'rootdir': os.path.join(os.path.dirname(__file__), 'templates')
        }
    }
    if extra:
        for key in extra:
            conf[key] = extra[key]
    return init(conf, finalize=finalize)


def test_initialization():
    init_score()


def test_empty_rendering():
    score = init_score()
    assert score.tpl.render('empty.jinja2') == ''


def test_caching():
    score = init_score()
    filetype = score.tpl.filetypes['text/html']
    renderer = score.jinja2._create_renderer(score.tpl, filetype)
    assert renderer.env.bytecode_cache is None
    with tempfile.TemporaryDirectory() as folder:
        score = init_score({'jinja2': {'cachedir': folder}})
        renderer = score.jinja2._create_renderer(score.tpl, filetype)
        assert renderer.env.bytecode_cache is not None


def test_different_extension():
    score = init_score({'jinja2': {'extension': 'tpl'}})
    assert score.tpl.render('a.tpl') == 'a'
    with pytest.raises(TemplateNotFound):
        score.tpl.render('a.jinja2')


def test_symlink():
    score = init_score({'jinja2': {'extension': 'tpl'}})
    assert score.tpl.render('a.tpl') == 'a'
    assert score.tpl.render('a_symlink.tpl') == 'a'


def test_simple_rendering():
    score = init_score()
    assert score.tpl.render('a.jinja2') == 'a'


def test_mimetype():
    score = init_score()
    assert score.tpl.mimetype('echo.jinja2') == 'text/html'


def test_changing_mimetype():
    score = init_score(finalize=False)
    score.tpl.filetypes['text/html'].extensions.remove('jinja2')
    score.tpl.filetypes['text/xml'].extensions.append('jinja2')
    score._finalize()
    assert score.tpl.mimetype('echo.jinja2') == 'text/xml'
