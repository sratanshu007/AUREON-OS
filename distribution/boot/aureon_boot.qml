import QtQuick

Rectangle {
    id: bootRoot
    width: 1920
    height: 1080
    color: "#000000"

    Image {
        id: logo
        anchors.centerIn: parent
        source: "../../assets/logos/aureon_logo.svg"
        sourceSize.width: 140
        sourceSize.height: 140
        opacity: 0.0

        NumberAnimation on opacity {
            to: 1.0
            duration: 1200
            running: true
        }
    }

    Text {
        anchors.top: logo.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.topMargin: 24
        text: "A U R E O N"
        font.pixelSize: 36
        font.bold: true
        font.letterSpacing: 12
        color: "#FFFFFF"
    }

    Text {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 48
        text: "Dream. Create. Explore."
        font.pixelSize: 13
        font.letterSpacing: 4
        color: "#80FFFFFF"
    }
}
