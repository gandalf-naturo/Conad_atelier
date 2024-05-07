from flask import Flask, session, abort, redirect, request, render_template,url_for
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests
import requests
import os
import pathlib
from datetime import date
import time
from werkzeug.utils import secure_filename
import pymysql 
from PIL import Image 
import os
import db_query  
#import db
#https://www.youtube.com/watch?v=FKgJEfrhU1E Video con creazione API
#https://www.youtube.com/watch?v=n4e3Cy2Tq3Q Video con modifiche funzionanti

app = Flask(__name__,template_folder='template')
app.secret_key="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" #secret key ottenuta dal json API di google
LOCAL_DB = True  #DA CAMBIARE
os.environ["OAUTHLIB_INSECURE_TRANSPORT"]="1"

GOOGLE_CLIENT_ID="145155795581-7jl6jltokmprc0m286nctr2n6b9g0cq3.apps.googleusercontent.com" #GOOGLE_CLIENT_ID ottenuta dal json API di google
client_secrets_file=os.path.join(pathlib.Path(__file__).parent, "secret.apps.googleusercontent.com.json") #specifico il file json contentente le credenziali
                                                                                      #scaricato da google cloud console dalla mail personale
        
flow=Flow.from_client_secrets_file( 
    client_secrets_file=client_secrets_file, #specifico il secret file
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"], #scopes
    redirect_uri="http://localhost:5000/callback" #url di reindirizzo
)


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
    
def login_is_required(function): #Fa accedere solo se si è loggati
    def check_login(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)
        else:
            return function(*args, **kwargs)
    check_login.__name__ = function.__name__
    return check_login
def check(conn):
    conn.ping(reconnect=True)
def check_email_domain(email): #controllo sul dominio inserito nel login
    session["email"]=email  # Salva l'indirizzo email nella sessione
    domain = email.split("@")[1]
    if domain == "einaudicorreggio.it": #qua metti il dominio che vuoi far accedere
        return False
    return True



@app.route('/')
def home():
    if 'google_id' in session:
        return render_template('home.html', username=session['google_id'])
    else:
        return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    authorization_url, state=flow.authorization_url()
    session["state"]=state
    return redirect(authorization_url)
@app.route("/callback")
def callback():
    try:
        # Recupera il token di accesso utilizzando la risposta di autorizzazione
        flow.fetch_token(authorization_response=request.url)

        # Verifica se la chiave 'state' è presente nella sessione e se corrisponde alla chiave 'state' nella richiesta
       # if "state" not in session or session["state"] != request.args.get("state"):
        #    abort(500)

        # Rimuovi la chiave 'state' dalla sessione dopo averla utilizzata
        session.pop("state", None)

        # Verifica le informazioni sull'ID dell'utente utilizzando il token di accesso
        credentials = flow.credentials
        request_session = requests.session()
        cached_session = cachecontrol.CacheControl(request_session)
        token_request = google.auth.transport.requests.Request(session=cached_session)
        id_info = id_token.verify_oauth2_token(
            id_token=credentials._id_token,
            request=token_request,
            audience=GOOGLE_CLIENT_ID
        )

        # Controlla se il dominio dell'email è valido
        if not check_email_domain(id_info.get("email")):
            return "Il dominio della mail non è valido!"

        # Imposta le informazioni dell'utente nella sessione 
        session["google_id"] = id_info.get("sub")
        session["name"] = id_info.get("name")

        # Reindirizza alla home page
        return redirect("/")

    except Exception as e:
        # Gestisci eventuali errori e interrompi l'esecuzione con un errore 500
        print("Errore durante la callback:", e)
        abort(500)


@app.route("/register", methods=['GET', 'POST'])
def register():
    
    if request.method == "POST":
        check(conn)
        username = request.form["username"]
        pwd = request.form['password']
     
        
        #db.get_dati_utente(diz)
        existing_user = db_query.select_username(conn,username)# Controllo se l'utente esiste già nel database   

        if existing_user:
            return render_template('register.html', error="Username già in uso. Scegli un altro username.")

        # Inserisco i dati nel database se l'utente non esiste già
        db_query.insert_user(conn,username,pwd) 
        return redirect(url_for('login'))

    return render_template('register.html')
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route("/inserisci_prodotti", methods=['GET', 'POST'])
@login_is_required
def inserisci_prodotti():
    if request.method == "POST":
            check(conn)
            nome_prodotto = request.form["nome"]
            corsia = request.form["corsia"]
            # Verifico se esiste già un prodotto con lo stesso nome nella stessa corsia
            existing_product = db_query.select_prodotti(conn,nome_prodotto,corsia)        
            if existing_product:
                # Se il prodotto esiste già, mostra un messaggio di errore
                return render_template('inserisci_prodotti.html',  username=session['google_id'], errore="Prodotto già presente nella corsia.")
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
            db_query.insert_prodotti(conn, corsia, nome_prodotto, descrizione, image_path, image_scaff_path)  
            return render_template('home.html', successo="Prodotto inserito con successo!",  username=session['google_id'])
    return render_template('inserisci_prodotti.html', username=session['google_id'])
    
@app.route("/mostra_prodotti",methods=['GET','POST'])
@login_is_required
def mostra_prodotti():
        if request.method=="POST":
            check(conn)
            nome_prodotto=request.form["nome"]
            prodotto= db_query.select_mostra(conn, nome_prodotto)  
            #Verifico l'esistenza del prodotto nel database
            if prodotto:
                prodotto=list(prodotto)
                return render_template('mostra_prodotti.html', prodotto=prodotto)
            else:
                #se non esiste mostro un messaggio di errore
                return render_template('mostra_prodotti.html', errore="Prodotto non trovato.", username=session['google_id'])
        else:
            return render_template('mostra_prodotti.html')
@app.route("/mostra_corsia",methods=['GET','POST'])
@login_is_required
def mostra_corsia():
        if request.method=="POST":
            check(conn)
            corsia=request.form["corsia"]
            cur = conn.cursor()  
            ris=db_query.select_corsia(conn,corsia)
            if ris:
                ris=list(ris)
                return render_template('mostra_corsia.html',corsia=ris,len=len(ris))
            else:
                return render_template('mostra_corsia.html', errore="Corsia non trovata.", username=session['google_id'])
        else:
            return render_template('mostra_corsia.html')

@app.route("/elimina",methods=['GET','POST'])
@login_is_required
def elimina():
    if 'google_id' not in session:
        return redirect(url_for('home'))
    else:
        if request.method=="POST":
            check(conn)
            nome_prodotto=request.form["nome"]
            corsia=request.form["corsia"]
            #cur.execute("SELECT * FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia))       
            prodotto = db_query.select_elimina(conn,nome_prodotto,corsia)
           
            #Verifico l'esistenza del prodotto nel database
            if prodotto:
                db_query.delete_prodotti(nome_prodotto, corsia)
                return render_template('elimina.html',successo="Prodotto eliminato con successo " )
            else:
                #se non esiste mostro un messaggio di errore
                return render_template('elimina.html', errore="Prodotto non trovato.", username=session['google_id'])
        else:
            return render_template('elimina.html')

@app.route("/update", methods=['GET','POST'])
@login_is_required
def update():

        if request.method == "POST":
            check(conn)
            nome_prodotto = request.form["nome"]
            campo_da_modificare = request.form["campo"]
           

            cur = conn.cursor()
            db_query.update_prodotto(conn, nome_prodotto)    
            prodotto = cur.fetchone()

            if prodotto:
                if campo_da_modificare == "nome":
                    nuovo_valore = request.form["nuovo_nome"]
                    db_query.update_prodotto(conn,campo_da_modificare,nuovo_valore)   
                elif campo_da_modificare == "descrizione":
                    nuovo_valore = request.form["nuova_descrizione"]
                    db_query.update_prodotto(conn,campo_da_modificare,nuovo_valore)   
                elif campo_da_modificare == "immagine_prodotto":
                    nuova_immagine_prodotto = request.files["nuova_immagine_prodotto"]
                    nuova_immagine_prodotto_filename = secure_filename(nuova_immagine_prodotto.filename)
                    nuova_immagine_prodotto_path = os.path.join('static/immagini/', nuova_immagine_prodotto_filename)
                    nuova_immagine_prodotto.save(nuova_immagine_prodotto_path)
                    db_query.update_prodotto(conn,campo_da_modificare,nuovo_valore)   
                elif campo_da_modificare == "corsia":
                    nuovo_valore = request.form["nuova_corsia"]
                    db_query.update_prodotto(conn,campo_da_modificare,nuovo_valore)   
                elif campo_da_modificare == "immagine_scaffale":
                    nuova_immagine_scaffale = request.files["nuova_immagine_scaffale"]
                    nuova_immagine_filename_scaffale = secure_filename(nuova_immagine_scaffale.filename)
                    nuova_immagine_scaffale_path = os.path.join('static/immagini/', nuova_immagine_filename_scaffale)
                    nuova_immagine_scaffale.save(nuova_immagine_scaffale_path)
                    db_query.update_prodotto(conn,campo_da_modificare,nuovo_valore)   

                conn.commit()
                cur.close()

                return render_template('update.html', successo="Prodotto aggiornato con successo.", username=session['username'])
            else:
                cur.close()
                return render_template('update.html', errore="Prodotto non trovato.", username=session['google_id'])
        else:
            return render_template('update.html')

            





if __name__=='__main__':
    app.run(debug=True)

    
