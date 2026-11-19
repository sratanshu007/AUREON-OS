import QtQuick
import QtQuick.Controls
import QtQuick.Layouts

Rectangle {
    width: 1920
    height: 1080

    Image {
        anchors.fill: parent
        source: "../../assets/wallpapers/mountain_lake_sunrise.svg"
        fillMode: Image.PreserveAspectCrop
    }

    Rectangle {
        anchors.centerIn: parent
        width: 360
        height: 380
        radius: 24
        color: "#B0FFFFFF"
        border.color: "#80FFFFFF"
        border.width: 1

        ColumnLayout {
            anchors.fill: parent
            anchors.margins: 32
            spacing: 16

            Rectangle {
                Layout.alignment: Qt.AlignHCenter
                width: 72
                height: 72
                radius: 36
                color: "#EEF3FF"
                border.color: "#1677F8"
                border.width: 2
                Text { anchors.centerIn: parent; text: "🧑🏻‍💻"; font.pixelSize: 32 }
            }

            Text {
                Layout.alignment: Qt.AlignHCenter
                text: "Sratanshu Shukla"
                font.pixelSize: 18
                font.bold: true
                color: "#17233D"
            }

            TextField {
                Layout.fillWidth: true
                placeholderText: "Password"
                echoMode: TextInput.Password
            }

            Button {
                Layout.fillWidth: true
                text: "Sign In"
            }
        }
    }
}
