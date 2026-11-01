/* SPDX-License-Identifier: GPL-2.0-or-later
 *
 * Minimal SANORA OS Calamares slideshow. Structure follows the upstream
 * Calamares default branding slideshow (Presentation / Slide elements).
 * User-visible sentences use qsTr() so they can be translated later;
 * the product name itself is deliberately not translated.
 */
import QtQuick 2.0;
import calamares.slideshow 1.0;

Presentation {
    id: presentation

    Slide {
        Image {
            id: logo
            source: "sanora-logo.png"
            width: 160; height: 160
            fillMode: Image.PreserveAspectFit
            anchors.centerIn: parent
        }
        Text {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.top: logo.bottom
            anchors.topMargin: 16
            text: "SANORA OS"
            color: "#F2F6FA"
            font.pixelSize: 28
            horizontalAlignment: Text.AlignHCenter
        }
    }

    Slide {
        centeredText: qsTr("Installing SANORA OS. This is a development build, not a release.")
    }

    Slide {
        centeredText: qsTr("Quality over speed.")
    }

    function onActivate() {
        presentation.currentSlide = 0;
    }

    function onLeave() {
    }
}
