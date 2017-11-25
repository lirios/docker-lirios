#!/bin/bash
#
# This file is part of Liri.
#
# Copyright (C) 2017 Pier Luigi Fiorini <pierluigi.fiorini@gmail.com>
#
# $BEGIN_LICENSE:GPL3+$
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# $END_LICENSE$
#

set -e

# Install packages
pacman -S --noconfirm \
    sudo \
    sed \
    liri-shell-git \
    liri-wayland-git \
    liri-workspace-git \
    liri-settings-git \
    liri-files-git \
    liri-appcenter-git \
    liri-terminal-git \
    liri-wallpapers-git \
    liri-themes-git \
    xorg-server \
    mesa-libgl \
    phonon-qt5-gstreamer

# Remove unnecessary files
rm -rf /README /usr/share/man/* /usr/share/info/* /usr/share/doc/* /usr/include/* /usr/lib/pkgconfig /usr/lib/cmake /var/lib/pacman

# Create the user
useradd -G wheel,video,input -ms /bin/bash lirios
echo "lirios:U6aMy0wojraho" | chpasswd -e
echo "lirios ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
mkdir /run/lirios && chown lirios:lirios /run/lirios && chmod 0700 /run/lirios
