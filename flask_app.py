from application.cancel_task import cancel_bp
from application.factory import Flask, init_app
from application.monitor import monitor_bp
from application.execute_task import execute_task_bp

app: Flask = init_app()

@app.route('/')
def index():
    return 'Welcome to dg_spider'

app.register_blueprint(execute_task_bp, url_prefix='/api')
app.register_blueprint(monitor_bp, url_prefix='/api')
app.register_blueprint(cancel_bp, url_prefix='/api')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6801)

