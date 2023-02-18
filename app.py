from flask import Flask
from flask import render_template, g, url_for, request
import sqlite3

app = Flask(__name__)

@app.route('/')
def main():
    return render_template("base.html")
    

def get_message_db():
    
    #check whether there is a database called `message_db` 
    #in the g attribute of the app
    try:
        return g.message_db
    
    #otherwise connect to that database
    #ensuring that the connection is an attribute of g
    except:
        g.message_db=sqlite3.connect("message_db.sqlite")
        
        cmd=\
        """
        CREATE TABLE IF NOT EXISTS message (
            id INTEGER PRIMARY KEY,
            handle TEXT NOT NULL,
            message TEXT NOT NULL);
        """
        
        cursor=g.message_db.cursor()
        cursor.execute(cmd)
        
        return g.message_db

    
def insert_message(request):
    
    db=get_message_db()
    cursor=db.cursor()
    nrows=cursor.execute("SELECT * FROM message")
    id_num=len(nrows.fetchall())+1
    
    handle=request.form['handle']
    message=request.form['message']
    
    if message and handle:
        cursor.execute('INSERT INTO message VALUES (?,?,?)',(id_num,handle,message))
        db.commit()  
    db.close()
    
    
@app.route('/submit/', methods=['POST','GET'])
def submit():
    
    if request.method=='GET':
        return render_template('submit.html')

    else:
        try:
            insert_message(request)

            if request.form['handle'] and request.form['message']:
                return render_template('submit.html', success=True)
            else:
                return render_template('submit.html', error=True)

        except:
            return render_template('submit.html', error=True)
        

def random_messages(n=5):
    db=get_message_db()
    cursor=db.cursor()
    nrows=cursor.execute("SELECT * FROM message")
    total_rows=len(nrows.fetchall())
    
    if n>total_rows:
        n=total_rows
    
    cmd=f"""SELECT handle, message FROM message ORDER BY RANDOM() LIMIT {n}"""
    cursor.execute(cmd)
    fetched_messages=cursor.fetchall()
    db.close()
    
    return fetched_messages


@app.route('/view/')
def view():
    return render_template('view.html',fetched_messages=random_messages())