import QtQuick 6.5
import QtQuick.Controls 6.5
import QtQuick.Layouts 6.5

ApplicationWindow {
    id: window
    visible: true
    width: 800
    height: 600
    title: "Semaforo QML"

    // StackView per la navigazione
    StackView {
        id: stackView
        anchors.fill: parent
        initialItem: mainPage
    }

    // Pagina principale
    Component {
        id: mainPage
        Page {
            title: "Home"
            Button {
                text: "Vai alla pagina del semaforo"
                anchors.centerIn: parent
                onClicked: stackView.push(semaforoPage)
            }
        }
    }

    // Pagina del semaforo
    Component 
    {
        id: semaforoPage
        Page 
        {
            title: "Semaforo"

            ColumnLayout 
            {
                anchors.centerIn: parent
                spacing: 20

                // Cerchio del semaforo
                Rectangle 
                {
                    anchors.horizontalCenter: parent.horizontalCenter
                    Layout.preferredWidth: 100
                    Layout.preferredHeight: 100
                    radius: 50
                    color: getColor(modbusOperations.pezPres)
                    border.color: "black"
                    border.width: 2

                    // Transizione animata per il cambio di colore
                    Behavior on color 
                    {
                        ColorAnimation { duration: 300 }
                    }
                }

                // Testo che mostra il valore
                Text 
                {
                    text: "Valore: " + getValue(modbusOperations.pezPres)
                    font.pointSize: 20
                    horizontalAlignment: Text.AlignHCenter
                    Layout.alignment: Qt.AlignHCenter
                }
            }

            // Funzione per determinare il colore
            function getColor(value) 
            {
                if (value >= 5) return "green";
                else if (value > 3 && value < 5) return "yellow";
                else return "red";
            }

            function getValue(value)
            {
                if (value <= 0) return "Caricamento rulliera in corso ...";
                else return value;
            }
        }
    }
}
