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

FROM fedora:28
MAINTAINER Pier Luigi Fiorini <pierluigi.fiorini@liri.io>
ARG channel=unstable
COPY build.sh .
RUN ./build.sh ${channel} 28 && rm -f build.sh
ENV XDG_RUNTIME_DIR=/run/lirios
USER lirios
WORKDIR /home/lirios
CMD ["/usr/bin/liri-session"]
