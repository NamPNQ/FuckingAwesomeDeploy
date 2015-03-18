from flask.ext.assets import Environment, Bundle

css_all = Bundle(
    'lib/bootstrap/css/bootstrap.css',
    'lib/bootstrap-select/css/bootstrap-select.css',
    'lib/font-awesome/css/font-awesome.css',
    'css/admin/*.css',
    'css/*.css',
    output='application.css'
)
js_all = Bundle(
    'js/jquery.min.js',
    output='application.js')


def register_app(app):
    assets = Environment(app)
    assets.register('css_all', css_all)
    assets.register('js_all', js_all)
