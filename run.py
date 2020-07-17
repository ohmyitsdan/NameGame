from game import app

# Runs in debug mode if the .py file is called directly
if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, threaded=True)

