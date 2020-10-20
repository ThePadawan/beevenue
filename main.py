from beevenue.beevenue import get_application

app = get_application()

if __name__ == "__main__":
    if app.config["DEBUG"]:
        app.run(app.hostname, app.port, threaded=True)
    else:
        app.run(app.hostname, app.port, threaded=True, use_x_sendfile=True)
