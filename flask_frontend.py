from flask import Flask, Response, render_template, request
from src.postgres import PostgresQL

app = Flask(__name__)

@app.route("/") 
def index():     
    return render_template('index.html') 

@app.route("/api/search") 
def api_search():
    search_str = request.args.get('query', default = None, type = str)
    count = request.args.get('count', default = 5, type = int)
    
    # Return error if no search stri
    if search_str is None:
        return Response(response="There was no search string provided", status=400)
    
    return PostgresQL.search_cards(search_str, count)     

if __name__ == '__main__':    
    print("Hallo, Welt!")
    app.run(host="0.0.0.0", port=80, debug=True)
