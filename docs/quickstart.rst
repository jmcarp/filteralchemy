.. _quickstart:

Quickstart
==========

Use **filteralchemy** to auto-generate filters based on a SQLAlchemy model:

.. code-block:: python

    import flask
    from models import Album, session
    from webargs.flaskparser import parser
    from filteralchemy import FilterSet

    class AlbumFilterSet(FilterSet):
        class Meta:
            model = Album
            query = session.query(Album)
            parser = parser

    app = flask.Flask(__name__)

    @app.route('/albums')
    def get_albums():
        query = AlbumFilterSet().filter()
        return flask.jsonify(query.all())

Customizing operators
---------------------

By default, **filteralchemy** generates filters using the `Equal` operator. To generate filters with different operators, set the `operators` and `column_overrides` options in `Meta`:

    from filteralchemy.operators import Greater, Less, Like

    class AlbumFilterSet(FilterSet):
        class Meta:
            model = Album
            query = session.query(Album)
            operators = (Equal, Greater, Less)
            column_overrides = {
                'name': {'operators': (Equal, Like)}
            }

Declaring fields manually
-------------------------

Individual filters can also be declared manually as class variables:

.. code-block:: python

    from webargs import fields
    from filteralchemy import Filter
    from filteralchemy.operators import In, ILike

    class AlbumFilterSet(FilterSet):
        class Meta:
            model = Album
            query = session.query(Album)
            parser = parser
        name = Filter(fields.Str(), operator=ILike)
        genre = Filter(fields.List(fields.Str), operator=In)

Customizing query format
------------------------

By default, **filteralchemy** uses two underscores to separate field names and operator names for non-default operators (e.g., "value__gt=5"). Multiple values for the same field are passed using repeated query parameters (e.g., "foo=&foo=2"). To override these defaults, set the `formatter` and `list_class` options in `Meta`:

.. code-block:: python

    from webargs.fields import DelimitedList
    from filteralchemy.formatters import JsonApiFormatter

    class AlbumFilterSet(FilterSet):
        class Meta:
            model = Album
            query = session.query(Album)
            formatter = JsonApiFormatter()
            list_class = DelimitedList

This example implements the JSON API standards for filtering, using parameters like "filter[value][in]=1,2,3".
