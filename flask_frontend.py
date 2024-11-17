from flask import Flask, Response, render_template

app = Flask(__name__)

@app.route("/") 
def index():     
    return render_template('index.html') 

if __name__ == '__main__':    
    print("Hallo, Welt!")
    app.run(host="0.0.0.0", port=80, debug=True)
