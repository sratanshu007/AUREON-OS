import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import "components"

ApplicationWindow {
    id: root
    visible: true
    width: 1440
    height: 900
    title: "AUREON OS Desktop"

    // Background Wallpaper
    Image {
        anchors.fill: parent
        source: "../../assets/wallpapers/mountain_lake_sunrise.svg"
        fillMode: Image.PreserveAspectCrop
    }

    // Top Menu Bar
    MenuBar {
        id: menuBar
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        height: 36
    }

    // Centerpiece Brandmark
    ColumnLayout {
        anchors.centerIn: parent
        spacing: 12

        Image {
            Layout.alignment: Qt.AlignHCenter
            source: "../../assets/logos/aureon_logo.svg"
            sourceSize.width: 110
            sourceSize.height: 110
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "A U R E O N"
            font.pixelSize: 42
            font.bold: true
            font.letterSpacing: 14
            color: "#17233D"
        }

        Text {
            Layout.alignment: Qt.AlignHCenter
            text: "DREAM • CREATE • EXPLORE"
            font.pixelSize: 13
            font.letterSpacing: 4
            color: "#65738D"
        }
    }

    // Top-Left Welcome Widget
    WelcomeWidget {
        anchors.top: menuBar.bottom
        anchors.left: parent.left
        anchors.margins: 20
        width: 320
        height: 110
    }

    // Bottom Translucent Dock
    Dock {
        anchors.bottom: parent.bottom
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottomMargin: 14
        height: 72
    }
}
