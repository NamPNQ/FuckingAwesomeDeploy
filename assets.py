from flask.ext.assets import Environment, Bundle

css_all = Bundle(
    'lib/bootstrap/css/bootstrap.min.css',
    'lib/bootstrap-select/css/bootstrap-select.min.css',
    'css/admin/*.css',
    'css/*.css',
    output='application.css'
)
js_all = Bundle(
    'js/jquery.min.js',
    'lib/bootstrap/js/bootstrap.min.js',
    'lib/bootstrap-select/js/bootstrap-select.min.js',
    output='application.js')


def register_app(app):
    assets = Environment(app)
    assets.register('css_all', css_all)
    assets.register('js_all', js_all)
