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

    def setParts(self, id_rulliera, quantity):
        self.cursore.execute("UPDATE rulliera SET pezzi = ?, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (quantity, id_rulliera))
        self.connessione.commit()

    def insertPart(self, id_rulliera):
        self.cursore.execute("UPDATE rulliera SET pezzi = pezzi+1, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (id_rulliera,))
        self.connessione.commit()

    def removePart(self, id_rulliera):
        self.cursore.execute("UPDATE rulliera SET pezzi = pezzi - 1, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (id_rulliera,))
        self.connessione.commit() 

    def rechargeParts(self, id_rulliera, quantity):
        self.cursore.execute("UPDATE rulliera SET pezzi = pezzi + ?, time = CURRENT_TIMESTAMP WHERE id_rulliera = ?", (quantity, id_rulliera))
        self.connessione.commit()

    def getParts(self, id_rulliera):
        self.cursore.execute("SELECT pezzi FROM rulliera WHERE id_rulliera = ?", (id_rulliera,))
        result = self.cursore.fetchone()
        if result:
            return result[0]
        else:
            return None
        
    def getAllParts(self):
        self.cursore.execute("SELECT * FROM rulliera")
        results = self.cursore.fetchall()
        return results