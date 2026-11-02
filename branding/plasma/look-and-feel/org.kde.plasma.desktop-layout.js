// SPDX-License-Identifier: GPL-2.0-or-later
//
// SANORA OS Plasma desktop layout script (KDE Plasma 6 scripting API).
// API verified against shell/scripting/{scriptengine,panel,containment}.cpp
// in the KDE plasma-workspace source tree (master, retrieved 2026-11-02).
//
// The KDE bug tracker (bug 487816) confirms this layout-script mechanism is
// the robust way for a distribution to set a first-start wallpaper; writing
// ~/.config/plasma-org.kde.plasma.desktop-appletsrc is overwritten by Plasma.

// Keep upstream widgets (Kickoff launcher, Task Manager, system tray, clock).
loadTemplate("org.kde.plasma.desktop.defaultPanel");

var allPanels = panels();
for (var i = 0; i < allPanels.length; i++) {
    var p = allPanels[i];
    // Compact, floating, bottom-centre panel: a dock-like task manager with
    // an application launcher, without copying any other OS's layout assets.
    p.location = "bottom";
    p.alignment = "center";
    p.lengthMode = "fit";
    p.height = 46;
    p.floating = true;
    p.opacity = "translucent";
    p.hiding = "none";
}

var desks = desktopsForActivity(currentActivity());
for (var j = 0; j < desks.length; j++) {
    var d = desks[j];
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = ["Wallpaper", "org.kde.image", "General"];
    d.writeConfig("Image", "/usr/share/sanora/wallpapers/sanora-default.png");
}
