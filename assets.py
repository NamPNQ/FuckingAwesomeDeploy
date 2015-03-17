from flask.ext.assets import Environment, Bundle

css_all = Bundle(
    'lib/bootstrap/bootstrap.css',
    'lib/bootstrap-select/bootstrap-select.css',
    'lib/font-awesome/font-awesome.css',
    'css/admin/*.css',
    'css/*.css',
    output='application.css'
)
js_all = Bundle(
    'js/jquery.js',
    output='application.js')

def register_app(app):
    assets = Environment(app)
    assets.register('js_all', js)
