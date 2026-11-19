import QtQuick
import QtQuick.Layouts

Rectangle {
    color: "#C0FFFFFF"
    radius: 16
    border.color: "#80DCE5F5"
    border.width: 1

    RowLayout {
        anchors.fill: parent
        anchors.margins: 14
        spacing: 12

        Rectangle {
            width: 52
            height: 52
            radius: 26
            color: "#EEF3FF"
            border.color: "#1677F8"
            border.width: 2

            Text {
                anchors.centerIn: parent
                text: "🧑🏻‍💻"
                font.pixelSize: 26
            }
        }

        ColumnLayout {
            spacing: 2
            Text {
                text: "Good Morning! ☀️"
                font.pixelSize: 15
                font.bold: true
                color: "#17233D"
            }
            Text {
                text: "Let's make today amazing."
                font.pixelSize: 12
                color: "#65738D"
            }
        }
    }
}
