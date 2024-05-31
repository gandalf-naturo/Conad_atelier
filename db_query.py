import pymysql

LOCAL_DB = True

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

def select_username(conn,username): 
    check(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM utenti WHERE username = %s", (username,))  
    user_data = cur.fetchone()
    cur.close()
    return user_data

def insert_user(conn,username, password):
    check(conn)
    cur = conn.cursor()
    cur.execute("INSERT INTO utenti (username, password) VALUES (%s, %s)", (username, password)) #
    conn.commit()
    cur.close()

def select_prodotti(conn,nome_prodotto,corsia):
    check(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM item WHERE nome = %s AND num_corsia = %s", (nome_prodotto, corsia))   #query
    items = cur.fetchall()
    cur.close()
    return items

def insert_prodotti(conn, corsia, nome_prodotto, descrizione, image_path, image_scaff_path):
    check(conn)
    cur = conn.cursor()
    cur.execute("INSERT INTO item (nome, num_corsia, desc_prod, immagine, immagine_scaffale) VALUES (%s, %s, %s, %s, %s)",   
        (nome_prodotto, corsia, descrizione, image_path, image_scaff_path))
    items = cur.fetchall()
    cur.close()
    return items

def select_mostra(conn, nome_prodotto):
    check(conn)
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM item WHERE nome LIKE '%{nome_prodotto}%'")
    conn.commit()
    prodotto= cur.fetchall()
    cur.close()
    return prodotto

def select_corsia(conn, corsia):
    check(conn)
    cur = conn.cursor()
    ris=cur.execute(f" SELECT * FROM item WHERE num_corsia= {corsia}")
    conn.commit()
    cur.close()
    return ris

def select_elimina(conn, nome_prodotto, corsia):
    check(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia)) 
    conn.commit()
    cur.close()

def delete_prodotti(conn, corsia, nome_prodotto):
    check(conn)
    cur = conn.cursor()
    cur.execute("DELETE FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia))
    conn.commit()
    cur.close()

def select_update(conn, nome_prodotto):
    check(conn)
    cur = conn.cursor()
    cur.execute("SELECT * FROM item WHERE nome=%s", (nome_prodotto,))
    conn.commit()
    items= cur.fetchall
    cur.close()
    return items

def update_prodotto(conn,campo,nome_prodotto, nuovo_valore ):
    check(conn)
    cur = conn.cursor()
    if campo == "nome":
        cur.execute("UPDATE item SET nome = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
    elif campo == "descrizione":
        cur.execute("UPDATE item SET desc_prod = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
    elif campo == "immagine_prodotto":
        cur.execute("UPDATE item SET immagine = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
    elif campo == "corsia":
        cur.execute("UPDATE item SET num_corsia = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
    elif campo == "immagine_scaffale":
        cur.execute("UPDATE item SET immagine_scaffale = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
    conn.commit()
    cur.close()





'''cur.execute("SELECT * FROM utenti WHERE username = %s", (username,))
   cur.execute("INSERT INTO utenti(username, password) VALUES (%s, %s)", (username, pwd))
   cur.execute("SELECT * FROM item WHERE nome = %s AND num_corsia = %s", (nome_prodotto, corsia))
   cur.execute("INSERT INTO item (nome, num_corsia, desc_prod, immagine, immagine_scaffale) VALUES (%s, %s, %s, %s, %s)",(nome_prodotto, corsia, descrizione, image_path, image_scaff_path))
   cur.execute(f"SELECT * FROM item WHERE nome LIKE '%{nome_prodotto}%'")
   cur.execute(f" SELECT * FROM item WHERE num_corsia= {corsia}")
   cur.execute("SELECT * FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia)) 
   cur.execute("DELETE FROM item WHERE nome=%s AND num_corsia=%s", (nome_prodotto, corsia))
   cur.execute("SELECT * FROM item WHERE nome=%s", (nome_prodotto,))

   cur.execute("UPDATE item SET nome = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
   cur.execute("UPDATE item SET desc_prod = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
   cur.execute("UPDATE item SET immagine = %s WHERE nome = %s", (nuova_immagine_prodotto_path, nome_prodotto))
   cur.execute("UPDATE item SET num_corsia = %s WHERE nome = %s", (nuovo_valore, nome_prodotto))
   cur.execute("UPDATE item SET immagine_scaffale = %s WHERE nome = %s", (nuova_immagine_scaffale_path, nome_prodotto))
   '''