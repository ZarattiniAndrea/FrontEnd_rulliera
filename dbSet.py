import sqlite3
import sys

#LO UTILIZZO SOLO PER INIZIALIZZARE IL DATABASE

def set_db():
    connessione = sqlite3.connect('modbus_toggle.db') # mi connetto al database (e lo creo se non esiste)
    cursore = connessione.cursor() #creo un cursore per leggere ed eseguire comandi SQL

    # Creo la tabella per memorizzare i prezzi prelevati (se non esiste già)
    """
    Formato dei dati:
    - id_rulliera: identificativo della rulliera (intero, chiave primaria)
    - pezzi: indica il numero di pezzi presenti sulla rulliera (intero)
    - time: indica il timestamp dell'ultima modifica (TIMESTAMP)
    - stato: indica lo stato della rulliera (testo, es: OK, SOTTO SOGLIA, VUOTA)
    - mittente: numero della rulliera che invia l'ordine (intero)
    - quantità: numero di pezzi richiesti nell'ordine (intero)
    - stato_ordine: stato dell'ordine (testo, es: IN PAUSA, IN CORSO, RICEVUTO, TERMINATO)
    """
    cursore.execute("CREATE TABLE IF NOT EXISTS rulliera(id_rulliera INTEGER PRIMARY KEY, " \
    "pezzi INTEGER, time TIMESTAMP, stato TEXT, mittente INTEGER, quantità INTEGER, stato_ordine TEXT)")

    # Controllo che la tabella sia stata creata
    res = cursore.execute("SELECT name FROM sqlite_master")
    print("Tabelle nel database", res.fetchone())

    #Aggiungo dei valori iniziali
    #Aggiungo dei valori iniziali  per la prima rulliera
    cursore.execute("INSERT or IGNORE INTO rulliera VALUES(1, 0, CURRENT_TIMESTAMP, 'VUOTA', 0, 0, 'TERMINATO')") 
    connessione.commit() # Salvo le modifiche
    #Aggiungo dei valori iniziali per la seconda rulliera
    cursore.execute("INSERT or IGNORE INTO rulliera VALUES(2, 0, CURRENT_TIMESTAMP, 'VUOTA', 0, 0, 'TERMINATO')")
    connessione.commit() # Salvo le modifiche

    #Verifico che i dati siano stati inseriti correttamente
    res = cursore.execute("SELECT * FROM rulliera")
    elements = res.fetchall()
    print("Rulliera | Pezzi | Time | Stato | Mittente | Quantità | Stato Ordine")
    for row in elements:
        print(row)
    
    connessione.close()
