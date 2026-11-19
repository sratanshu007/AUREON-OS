import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

Rectangle {
    color: "#D0FFFFFF"
    radius: 20
    border.color: "#80DCE5F5"
    border.width: 1
    width: 280
    height: 320

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12

        Text {
            text: "Control Center"
            font.pixelSize: 15
            font.bold: true
            color: "#17233D"
        }

        GridLayout {
            columns: 2
            Layout.fillWidth: true
            rowSpacing: 10
            columnSpacing: 10

            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 12
                color: "#1677F8"
                Text { anchors.centerIn: parent; text: "📶 Wi-Fi On"; color: "#fff"; font.bold: true; font.pixelSize: 12 }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 12
                color: "#238BFF"
                Text { anchors.centerIn: parent; text: "ᛒ Bluetooth"; color: "#fff"; font.bold: true; font.pixelSize: 12 }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 12
                color: "#8175EE"
                Text { anchors.centerIn: parent; text: "🌙 Dark Mode"; color: "#fff"; font.bold: true; font.pixelSize: 12 }
            }

            Rectangle {
                Layout.fillWidth: true
                height: 48
                radius: 12
                color: "#A99BFF"
                Text { anchors.centerIn: parent; text: "🎯 Focus On"; color: "#fff"; font.bold: true; font.pixelSize: 12 }
            }
        }
    }
}
