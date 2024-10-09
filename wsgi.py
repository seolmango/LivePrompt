from run import socketio, app

application = socketio

if __name__ == '__main__':
    application.run(app, host='0.0.0.0', port=8000, debug=True)