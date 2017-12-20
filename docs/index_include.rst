.. module:: score.jinja2
.. role:: confkey
.. role:: confdefault

************
score.jinja2
************

A small module that registers a :class:`score.tpl.Renderer` for jinja2
file types with :mod:`score.tpl`.


Quickstart
==========

Usually, it is sufficient to add this module to your initialization list:


.. code-block:: ini

    [score.init]
    modules =
        score.tpl
        score.jinja2


API
===

.. autofunction:: init

.. autoclass:: ConfiguredJinja2Module()

.. autoclass:: Jinja2Renderer()
