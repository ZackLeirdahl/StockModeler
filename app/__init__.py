from flask import Flask

def create_app():
    app = Flask(__name__)
    
    from .blueprints import auth, options, tasks
    app.register_blueprint(auth.bp)
    app.register_blueprint(options.bp)
    app.register_blueprint(tasks.bp)
    return app

app = create_app()
