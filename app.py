from flask import Flask, request, render_template

app = Flask(__name__)

@app.route('/')
def blocked_page():
    domain = request.host  # Get the domain from the request headers
    return render_template('index.html', domain=domain)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=5000)