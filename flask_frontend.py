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
    target = request.args.get('target', default = "name", type = str)
    
    # Return error if no search stri
    if search_str is None:
        return Response(response="There was no search string provided", status=400)
    
    return PostgresQL.search_cards(search_str, target, count)

@app.route("/api/card") 
def api_card():    
    ids = request.args.get('id', default = None, type = int)
    df = json_normalize()
    
    # Return error if no search stri
    if id is None:
        return Response(response="No card id was provided", status=404)
    
    return PostgresQL.get_card(id)     

if __name__ == '__main__':        
    app.run(host="0.0.0.0", port=80, debug=True)
