#!/bin/bash
#
# This file is part of Liri.
#
# Copyright (C) 2018 Pier Luigi Fiorini <pierluigi.fiorini@gmail.com>
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

channel=$1
releasever=$2

if [ -z "$channel" -o -z "$releasever" ]; then
    echo "Usage: $0 <channel> <releasever>"
    echo
    echo "<channel> can be either 'stable' or 'unstable'"
    exit 1
fi

# Repository
curl "https://copr.fedorainfracloud.org/coprs/plfiorini/liri-unstable/repo/fedora-${releasever}/plfiorini-liri-${channel}-fedora-${releasever}.repo" > /etc/yum.repos.d/plfiorini-liri-${channel}.repo

# Install packages
dnf install -y \
    liri-materialdecoration \
    liri-networkmanager \
    liri-platformtheme \
    liri-power-manager \
    liri-pulseaudio \
    liri-screencast \
    liri-screenshot \
    liri-settings \
    liri-shell \
    liri-wallpapers \
    qml-xwayland \
    xdg-desktop-portal-liri \
    paper-icon-theme \
    liri-color-schemes \
    liri-appcenter \
    liri-calculator \
    liri-files \
    liri-terminal \
    liri-browser \
    liri-text

# Clean up
dnf clean all

# Remove unnecessary files
rm -rf /usr/share/man/* /usr/share/info/* /usr/share/doc/* /usr/include/* /usr/lib{,64}/pkgconfig /usr/lib{,64}/cmake

# Create the user
useradd -G wheel,video,input -ms /bin/bash lirios
echo "lirios:U6aMy0wojraho" | chpasswd -e
echo "lirios ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
mkdir /run/lirios && chown lirios:lirios /run/lirios && chmod 0700 /run/lirios
