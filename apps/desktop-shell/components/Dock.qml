import QtQuick
import QtQuick.Layouts

Rectangle {
    id: dockRoot
    color: "#B0FFFFFF"
    radius: 20
    border.color: "#80DCE5F5"
    border.width: 1
    width: dockRow.implicitWidth + 32

    RowLayout {
        id: dockRow
        anchors.centerIn: parent
        spacing: 12

        Repeater {
            model: [
                { name: "Files", icon: "📁", color: "#1677F8" },
                { name: "Browser", icon: "🌐", color: "#238BFF" },
                { name: "Terminal", icon: "⌨️", color: "#17233D" },
                { name: "Settings", icon: "⚙️", color: "#65738D" },
                { name: "Store", icon: "🛍️", color: "#8175EE" },
                { name: "Notes", icon: "📝", color: "#F2AE45" },
                { name: "Calendar", icon: "📅", color: "#E85D70" },
                { name: "AI", icon: "✨", color: "#A99BFF" },
                { name: "Trash", icon: "🗑️", color: "#95A5A6" }
            ]

            Rectangle {
                width: 48
                height: 48
                radius: 12
                color: modelData.color

                Text {
                    anchors.centerIn: parent
                    text: modelData.icon
                    font.pixelSize: 24
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onEntered: parent.scale = 1.15
                    onExited: parent.scale = 1.0
                }

                Behavior on scale {
                    NumberAnimation { duration: 150; easing.type: Easing.OutQuad }
                }
            }
        }
    }
}
