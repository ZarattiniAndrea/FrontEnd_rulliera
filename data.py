import sys
import sqlite3

# Utility per la gestione dei dati nel database
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

class Connection:
    def __init__(self, db_name="modbus_toggle.db"):
        self.connessione = sqlite3.connect(db_name)
        self.cursore = self.connessione.cursor()

def setParts(id_rulliera, quantity):
    conn = Connection()
    conn.cursore.execute("UPDATE rulliera SET pezzi = ?, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (quantity, id_rulliera))
    conn.connessione.commit()
    conn.connessione.close()

def insertPart(id_rulliera):
    conn = Connection()
    conn.cursore.execute("UPDATE rulliera SET pezzi = pezzi+1, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (id_rulliera,))
    conn.connessione.commit()
    conn.connessione.close() #quando chiudo la connessione, l'oggetto viene rimosso automaticamente dal garbage collector

def removePart(id_rulliera):
    conn = Connection()
    conn.cursore.execute("UPDATE rulliera SET pezzi = pezzi - 1, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (id_rulliera,))
    conn.connessione.commit()
    conn.connessione.close() 

def rechargeParts(id_rulliera, quantity):
    conn = Connection()

