from flask import app


@app.route('/test', methods=['GET'])
def get_tasks():
    return 'toto'