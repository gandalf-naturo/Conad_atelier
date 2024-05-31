# Conad Atelier
https://einaudilocal.pythonanywhere.com/
## Basato sul micro-framework Flask
Il progetto nasce con l'obiettivo di supportare il laboratorio dei ragazzi con disabilità psico-fisica dell’atelier dell’istituto einaudi nel loro periodo di stage presso il supermercato Conad di Correggio.
Lo scopo è quello di poter inserire i prodotti sulla piattaforma indicando nome del prodotto, numero corsia, immagine del prodotto e immagine dello scaffale.


## Struttura Sito
Il sito presenta una pagina home dove è richiesto il login. Al momento chiunque può registrarsi e utilizzare il servizio.
La gestione degli utenti è effettuata lato server.
Nella home è presente un menu per l’inserimento, la modifica, l’eliminazione e visualizzazione dei prodotti. È possibile visualizzare anche la corsia.
Per eliminare un elemento è necessario conoscere il nome di esso e il numero di corsia.

## Software
Il software si appoggia su un database relazionale, in particolare MySQL.
Strutturato in due tabelle: utenti e item.
Gli utenti che si registrano vengono aggiunti alla tabella utenti.
La table item è utile per l’inserimento di un elemento: verranno salvati:
- dettagli del prodotto
- percorso delle immagini.

In questo modo per effettuare una ricerca, verrà eseguita una query utilizzando come parametro il nome e la corsia richiesta e tornerà il percorso dell’immagine.




## Installation
Clona la repo
```sh
git clone https://github.com/gandalf-naturo/Conad_atelier.git
```
Per installare le dipendenze crea una Virtual Environment e attivala
```sh
cd Conad_atelier
python -m venv venv
venv/Source/activate.bat        //windows
source venv/bin/activate.sh     //linux
```
Installa le dipendenze
```sh
pip install -r requirements.txt
```



## Development
Per sviluppare in locale è necessario creare il seguente file
```sh
touch local_settings.py
```
Scrivi dentro al file 'local_settings.py'
```
LOCAL_DB = True
```

Runna il progetto
```sh
python server_flask_conad.py
```
Apri sul browser
```sh
http://localhost:5000/
```

## License

**Free Software**