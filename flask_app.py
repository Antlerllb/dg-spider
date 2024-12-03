from application.factory import Flask, init_app
from application.monitor import monitor_bp
from application.task import task_bp

app: Flask = init_app()

@app.route('/')
def index():
    return 'Welcome to dg_spider'

app.register_blueprint(task_bp, url_prefix='/task')
app.register_blueprint(monitor_bp, url_prefix='/monitor')


if __name__ == '__main__':
    app.run()

