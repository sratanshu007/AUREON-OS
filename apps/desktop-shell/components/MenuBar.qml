import QtQuick
import QtQuick.Layouts

Rectangle {
    id: mbRoot
    color: "#D0FFFFFF"
    border.color: "#30DCE5F5"
    border.width: 1

    RowLayout {
        anchors.left: parent.left
        anchors.leftMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        spacing: 16

        Text { text: "✦"; font.pixelSize: 16; font.bold: true; color: "#1677F8" }
        Text { text: "Aureon"; font.pixelSize: 13; font.bold: true; color: "#17233D" }
        Text { text: "File"; font.pixelSize: 13; color: "#17233D" }
        Text { text: "Edit"; font.pixelSize: 13; color: "#17233D" }
        Text { text: "View"; font.pixelSize: 13; color: "#17233D" }
        Text { text: "Go"; font.pixelSize: 13; color: "#17233D" }
        Text { text: "Window"; font.pixelSize: 13; color: "#17233D" }
        Text { text: "Help"; font.pixelSize: 13; color: "#17233D" }
    }

    RowLayout {
        anchors.right: parent.right
        anchors.rightMargin: 16
        anchors.verticalCenter: parent.verticalCenter
        spacing: 12

        Text { text: "🔍"; font.pixelSize: 13 }
        Text { text: "📶"; font.pixelSize: 13 }
        Text { text: "ᛒ"; font.pixelSize: 13 }
        Text { text: "🔋 92%"; font.pixelSize: 12; font.bold: true }
        Text { text: "Mon, Apr 28  9:41 AM"; font.pixelSize: 12; font.bold: true; color: "#17233D" }
    }
}
