import os

from flask import Flask, redirect, url_for


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    from configparser import ConfigParser
    config = ConfigParser()
    # Ensure the config file exists
    config.read('config.ini')
    # Ensure the DB path is specified and exists
    if not config.has_option('main', 'DB'):
        raise Exception("DB path not specified in config.ini")
    if not os.path.exists(config.get('main', 'DB')):
        raise Exception("DB path does not exist")
    
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(config.get('main', 'DB')).replace('\\', os.sep)
    )
    app.config['DATABASE'] = config.get('main', 'DB').replace('\\', os.sep)
    # Set the maximum file size if specified else default to 10MB
    if config.has_option('main', 'MAX_FILE_SIZE'):
        app.config['MAX_FILE_SIZE'] = config.getint('main', 'MAX_FILE_SIZE') * 1024 * 1024
    else:
        app.config['MAX_FILE_SIZE'] = 20 * 1024 * 1024
    print(app.config['DATABASE'])

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route('/')
    def index():
        # Redirect to query page
        return redirect(url_for('query.query'))
    
    # If route is undefined, redirect to query page
    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('query.query'))
    
    from . import query
    app.register_blueprint(query.bp)

    from . import db
    db.init_app(app)

    return app