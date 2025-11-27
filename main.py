from PySide6.QtCore import QUrl, QObject, Property, Signal
from PySide6.QtWidgets import QApplication, QProgressBar, QPushButton
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickView
from pymodbus.client import ModbusTcpClient
import time
import threading
import sqlite3
import sys
import dbSet
from dbSet import set_db

pz_min = 5 # Numero di pezzi minimi che devono essere presenti sulla rulliera

class ModbusOperations(QObject):
    # Segnale che notifica il cambiamento del numero di pezzi sulla rulliera
    pezPresChanged1 = Signal()
    pezPresChanged2 = Signal()

    def __init__(self):
        super().__init__()
        self._pezPres1 = 10 # Numero di pezzi presenti sulla prima rulliera
        self._pezPres2 = 10 # Numero di pezzi presenti sulla seconda rulliera

    @Property(int, notify=pezPresChanged1)
    def pezPres1(self):
        """Getter automatico per QML"""
        return self._pezPres1

    @pezPres1.setter
    def pezPres1(self, value):
        """Setter automatico, emette il segnale se cambia"""
        if self._pezPres1 != value:
            self._pezPres1 = value
            self.pezPresChanged1.emit() #emetto il segnale di cambiamento

    @Property(int, notify=pezPresChanged2)
    def pezPres2(self):
        """Getter automatico per QML della seconda rulliera"""
        return self._pezPres2
    
    @pezPres2.setter
    def pezPres2(self, value):
        """Setter automatico, emette il segnale se cambia"""
        if self._pezPres2 != value:
            self._pezPres2 = value
            self.pezPresChanged2.emit() #emetto il segnale di cambiamento

    def start_operations(self):
        client = ModbusTcpClient('192.168.200.170', port=502)
        # Leggo i toggle iniziali
        front_result1 = client.read_coils(address=0x00, count=1)
        back_result1 = client.read_coils(address=0x01, count=1)
        front_result2 = client.read_coils(address=0x02, count=1)
        back_result2 = client.read_coils(address=0x03, count=1)
        # Salvo i valori iniziali per il confronto con quelli attuali
        front_prectoggle1 = front_result1.bits[0]
        back_prectoggle1 = back_result1.bits[0]
        front_prectoggle2 = front_result2.bits[0]
        back_prectoggle2 = back_result2.bits[0]
        conta_pezzi = 10
        while(True):
            front_result1 = client.read_coils(address=0, count=1)
            front_result2 = client.read_coils(address=2, count=1)
            back_result1 = client.read_coils(address=1, count=1)
            back_result2 = client.read_coils(address=3, count=1)
            try:
                if (front_result1.isError() or back_result1.isError() or front_result2.isError() or back_result2.isError()):
                    print("Errore nella lettura dei toggle:", front_result1, back_result1, front_result2, back_result2)
                else:
                    print("Prima rulliera --> valore del toggle anteriore:" + str(front_result1.bits[0]) + ", valore del toggle posteriore:" + str(back_result1.bits[0]))
                    print("Seconda rulliera --> valore del toggle anteriore:" + str(front_result2.bits[0]) + ", valore del toggle posteriore:" + str(back_result2.bits[0]))
                    current_front_toggle1 = front_result1.bits[0]
                    current_back_toggle1 = back_result1.bits[0]
                    current_front_toggle2 = front_result2.bits[0]
                    current_back_toggle2 = back_result2.bits[0]
                    # Controllo i cambiamenti di stato dei toggle nella PRIMA RULLIERA
                    if current_front_toggle1 != front_prectoggle1:
                        front_prectoggle1 = current_front_toggle1
                        conta_pezzi += 1
                        self.pezPres1 += 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres1}")
                    if current_back_toggle1 != back_prectoggle1:
                        back_prectoggle1 = current_back_toggle1
                        conta_pezzi -= 1
                        self.pezPres1 -= 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres1}")
                    # Controllo i cambiamenti di stato dei toggle nella SECONDA RULLIERA
                    if current_front_toggle2 != front_prectoggle2:
                        front_prectoggle2 = current_front_toggle2
                        conta_pezzi += 1
                        self.pezPres2 += 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres2}")
                    if current_back_toggle2 != back_prectoggle2:
                        back_prectoggle2 = current_back_toggle2
                        conta_pezzi -= 1
                        self.pezPres2 -= 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres2}")
                    if self.pezPres1 < pz_min:
                        print("Attenzione: numero di pezzi sotto la soglia minima!")
                        # QUI DOVREI LANCIARE MISSIONE AD AMR
                    if self.pezPres2 < pz_min:
                        print("Attenzione: numero di pezzi sotto la soglia minima!")
                        # QUI DOVREI LANCIARE MISSIONE AD AMR
                    if self.pezPres1 == 0:
                        time.sleep(5) #attendo 5 secondi
                        self.pezPres1 = 10 #resetto il numero di pezzi presenti sulla rulliera
                    if self.pezPres2 == 0:
                        time.sleep(5) #attendo 5 secondi
                        self.pezPres2 = 10 #resetto il numero di pezzi presenti sulla rulliera

            except Exception as e:
                print("Errore durante la comunicazione Modbus TCP:", e)   
            except KeyboardInterrupt:
                print("Chiusura del client Modbus TCP.")
                client.close()
                break
                
                        
            
    #pz_pres = Property(int, get_pres, set_pres, notify=pz_pres_changed)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    modbus_operations = ModbusOperations()
    # Avvio impostazioni del database
    set_db()
    thread_modbus = threading.Thread(target=modbus_operations.start_operations)
    thread_modbus.daemon = True
    thread_modbus.start()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("modbusOperations", modbus_operations)
    #carico il file QML
    engine.load(QUrl.fromLocalFile(r"C:\Users\SIEMENS\Desktop\Zarattini_Andrea\Prova_QtGUI\semaforo_qml\main_varie_pagine.qml"))


    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec())