from PySide6.QtCore import QUrl, QObject, Property, Signal
from PySide6.QtWidgets import QApplication, QProgressBar, QPushButton
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickView
from pymodbus.client import ModbusTcpClient
import time
import threading
import sqlite3
import sys

pz_min = 5 # Numero di pezzi minimi che devono essere presenti sulla rulliera

class ModbusOperations(QObject):
    # Segnale che notifica il cambiamento del numero di pezzi sulla rulliera
    pezPresChanged = Signal()

    def __init__(self):
        super().__init__()
        self._pezPres = 10 # Numero di pezzi presenti sulla rulliera

    @Property(int, notify=pezPresChanged)
    def pezPres(self):
        """Getter automatico per QML"""
        return self._pezPres
    
    @pezPres.setter
    def pezPres(self, value):
        """Setter automatico, emette il segnale se cambia"""
        if self._pezPres != value:
            self._pezPres = value
            self.pezPresChanged.emit() #emetto il segnale di cambiamento
    
    def start_operations(self):
        client = ModbusTcpClient('192.168.200.170', port=502)
        front_result = client.read_coils(address=0x00, count=1)
        back_result = client.read_coils(address=0x01, count=1)
        front_prectoggle = front_result.bits[0]
        back_prectoggle = back_result.bits[0]
        conta_pezzi = 10
        while(True):
            front_result = client.read_coils(address=0, count=1)
            back_result = client.read_coils(address=1, count=1)
            try:
                if (front_result.isError() or back_result.isError()):
                    print("Errore nella lettura dei toggle:", front_result, back_result)
                else:
                    print("Valore del toggle anteriore:" + str(front_result.bits[0]) + " Valore del toggle posteriore:" + str(back_result.bits[0]))
                    current_front_toggle = front_result.bits[0]
                    current_back_toggle = back_result.bits[0]
                    if current_front_toggle != front_prectoggle:
                        front_prectoggle = current_front_toggle
                        conta_pezzi += 1
                        self.pezPres += 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres}")
                    if current_back_toggle != back_prectoggle:
                        back_prectoggle = current_back_toggle
                        conta_pezzi -= 1
                        self.pezPres -= 1 # Aggiorno il valore globale per l'interfaccia grafica
                        print(f"Pezzi presenti sulla rulliera: {self._pezPres}")
                    if self.pezPres < pz_min:
                        print("Attenzione: numero di pezzi sotto la soglia minima!")
                        # QUI DOVREI LANCIARE MISSIONE AD AMR
                    if self.pezPres == 0:
                        time.sleep(5) #attendo 5 secondi
                        self.pezPres = 10 #resetto il numero di pezzi presenti sulla rulliera

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