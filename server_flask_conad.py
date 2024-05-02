from flask import Flask, request,session,render_template,url_for,redirect,jsonify
from werkzeug.utils import secure_filename
import pymysql 
from PIL import Image 
import os

app = Flask(__name__,template_folder='template')
app.secret_key=os.urandom(24)

LOCAL_DB = False
conn = object
try:
    from local_settings import LOCAL_DB
except ImportError:
    print("Looks like no local file. You must be on production")

if LOCAL_DB:
    print("Stai lavorando in locale!!!!!")
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="conad_atelier",
        port=3306,
        )
else:
    conn = pymysql.connect(
        host="EinaudiLocal.mysql.pythonanywhere-services.com",
        user="EinaudiLocal",
        password="loredana72",
        database="EinaudiLocal$default",
        port=3306,
        ) 
def check(conn):
    conn.ping(reconnect=True)



@app.route('/')
def home():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    else:
        return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        check(conn)
        username=request.form['username']
        pwd=request.form['password']
        cur=conn.cursor()
        cur.execute(f"SELECT username,password FROM utenti WHERE username='{username}'")
        user=cur.fetchone()

        cur.close()
        if user and pwd == user[1]:
            session['username']=user[0]
            return redirect(url_for('home'))
        else:
            return render_template('login.html',errore="username o password errate")
    return render_template('login.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        check(conn)
        username = request.form["username"]
        pwd = request.form['password']

        # Controllo se l'utente esiste già nel database
        cur = conn.cursor()
        cur.execute("SELECT * FROM utenti WHERE username = %s", (username,))
        existing_user = cur.fetchone()

        if existing_user:
            cur.close()
            return render_template('register.html', error="Username già in uso. Scegli un altro username.")

        # Inserisco i dati nel database se l'utente non esiste già
        cur.execute("INSERT INTO utenti(username, password) VALUES (%s, %s)", (username, pwd))
        conn.commit()
        cur.close()

        return redirect(url_for('login'))

    return render_template('register.html')
@app.route("/logout")
def logout():
    session.pop("username",None)
    return redirect(url_for('home'))

@app.route("/inserisci_prodotti", methods=['GET', 'POST'])
def inserisci_prodotti():
    if 'username' not in session:
        return redirect(url_for('home'))
    else:
        if request.method == "POST":
            check(conn)
            nome_prodotto = request.form["nome"]
            corsia = request.form["corsia"]
            # Verifico se esiste già un prodotto con lo stesso nome nella stessa corsia
            cur = conn.cursor()
            cur.execute("SELECT * FROM item WHERE nome = %s AND num_corsia = %s", (nome_prodotto, corsia))
            existing_product = cur.fetchone()
            cur.close()
            if existing_product:
                # Se il prodotto esiste già, mostra un messaggio di errore
                return render_template('inserisci_prodotti.html', username=session['username'], errore="Prodotto già presente nella corsia.")
            # Continuo con l'inserimento se il prodotto non esiste già
            image_file = request.files["image"]
            image = Image.open(image_file)
            image.thumbnail((300, 300))  # Riduci l'immagine a una dimensione massima di 300x300
            image_filename = secure_filename(image_file.filename)
            image_path = os.path.join('static/immagini/', image_filename)
            image.save(image_path)  # Salva l'immagine ridotta
            descrizione = request.form["descrizione"]
            img_scaff_file = request.files["image_scaffale"]
            img_scaff = Image.open(img_scaff_file)
            img_scaff.thumbnail((300, 300))  # Riduci l'immagine a una dimensione massima di 300x300
            img_scaff_filename = secure_filename(img_scaff_file.filename)
            image_scaff_path = os.path.join('static/immagini/', img_scaff_filename)
            img_scaff.save(image_scaff_path)  # Salva l'immagine ridotta
            cur = conn.cursor()
            cur.execute("INSERT INTO item (nome, num_corsia, desc_prod, immagine, immagine_scaffale) VALUES (%s, %s, %s, %s, %s)",
                        (nome_prodotto, corsia, descrizione, image_path, image_scaff_path))
            conn.commit()
            cur.close()
            return render_template('home.html', successo="Prodotto inserito con successo!", username=session['username'])
        return render_template('inserisci_prodotti.html', username=session['username'])
    
@app.route("/mostra_prodotti",methods=['GET','POST'])
def mostra_prodotti():
    if 'username' not in session:
        return redirect(url_for('home'))
    else:
        if request.method=="POST":
            check(conn)
            nome_prodotto=request.form["nome"]
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM item WHERE nome LIKE '%{nome_prodotto}%'")

            prodotto = cur.fetchall()
            cur.close()
            #Verifico l'esistenza del prodotto nel database
            if prodotto:
                prodotto=list(prodotto)
                return render_template('mostra_prodotti.html', prodotto=prodotto)
            else:
                #se non esiste mostro un messaggio di errore
                return render_template('mostra_prodotti.html', errore="Prodotto non trovato.", username=session['username'])
        else:
            return render_template('mostra_prodotti.html')
@app.route("/mostra_corsia",methods=['GET','POST'])
def mostra_corsia():
    if 'username' not in session:
        return redirect(url_for('home'))
    else:
        if request.method=="POST":
            check(conn)
            corsia=request.form["corsia"]
            cur = conn.cursor()
            cur.execute(f" SELECT * FROM item WHERE num_corsia= {corsia}")
            ris=cur.fetchall()
            if ris:
                ris=list(ris)
                return render_template('mostra_corsia.html',corsia=ris,len=len(ris))
            else:
                return render_template('mostra_corsia.html', errore="Corsia non trovata.", username=session['username'])
        else:
            return render_template('mostra_corsia.html')

@app.route("/elimina",methods=['GET','POST'])
def elimina():
    if 'username' not in session:
        return redirect(url_for('home'))
    else:
        if request.method=="POST":
            check(conn)
            nome_prodotto=request.form["nome"]
            corsia=request.form["corsia"]
            cur = conn.cursor()
            cur.execute("SELECT * FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia))
            prodotto = cur.fetchone()
            cur.close()
            #Verifico l'esistenza del prodotto nel database
            if prodotto:
                cur = conn.cursor()
                cur.execute("DELETE FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia))
                conn.commit()
                cur.close()
                return render_template('elimina.html',successo="Prodotto eliminato con successo " )
            else:
                #se non esiste mostro un messaggio di errore
                return render_template('elimina.html', errore="Prodotto non trovato.", username=session['username'])
        else:
            return render_template('elimina.html')

@app.route("/update", methods=['GET','POST'])
def update():
    if 'username' not in session:
        return redirect(url_for('home'))
    else:
        if request.method == "POST":
            check(conn)
            nome_prodotto = request.form["nome"]
            campo_da_modificare = request.form["campo"]
           

            cur = conn.cursor()
            cur.execute("SELECT * FROM item WHERE nome=%s", (nome_prodotto,))
            prodotto = cur.fetchone()

            if prodotto:
                if campo_da_modificare == "nome":
                    nuovo_valore = request.form["nuovo_nome"]
                    cur.execute("UPDATE item SET nome = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
                elif campo_da_modificare == "descrizione":
                    nuovo_valore = request.form["nuova_descrizione"]
                    cur.execute("UPDATE item SET desc_prod = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
                elif campo_da_modificare == "immagine_prodotto":
                    nuova_immagine_prodotto = request.files["nuova_immagine_prodotto"]
                    nuova_immagine_prodotto_filename = secure_filename(nuova_immagine_prodotto.filename)
                    nuova_immagine_prodotto_path = os.path.join('static/immagini/', nuova_immagine_prodotto_filename)
                    nuova_immagine_prodotto.save(nuova_immagine_prodotto_path)
                    cur.execute("UPDATE item SET immagine = %s WHERE nome = %s", (nuova_immagine_prodotto_path, nome_prodotto))
                elif campo_da_modificare == "corsia":
                    nuovo_valore = request.form["nuova_corsia"]
                    cur.execute("UPDATE item SET num_corsia = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
                elif campo_da_modificare == "immagine_scaffale":
                    nuova_immagine_scaffale = request.files["nuova_immagine_scaffale"]
                    nuova_immagine_filename_scaffale = secure_filename(nuova_immagine_scaffale.filename)
                    nuova_immagine_scaffale_path = os.path.join('static/immagini/', nuova_immagine_filename_scaffale)
                    nuova_immagine_scaffale.save(nuova_immagine_scaffale_path)
                    cur.execute("UPDATE item SET immagine_scaffale = %s WHERE nome = %s", (nuova_immagine_scaffale_path, nome_prodotto))

                conn.commit()
                cur.close()

                return render_template('update.html', successo="Prodotto aggiornato con successo.", username=session['username'])
            else:
                cur.close()
                return render_template('update.html', errore="Prodotto non trovato.", username=session['username'])
        else:
            return render_template('update.html')

            





if __name__=='__main__':
    app.run(debug=True)

    
