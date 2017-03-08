#!/usr/bin/env python3
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

import sys
import os
import shutil

CONTAINER_NAME = 'lirios/base'

CHROOT_DIR = 'chroot'

ARCH_LINUX_MIRROR = 'https://mirrors.lug.mtu.edu/archlinux'
ARCH_LINUX_ARCH = 'x86_64'

PACKAGES_LIST = [
    'sudo',
    'liri-shell-git',
    'liri-wayland-git',
    'liri-workspace-git',
    'liri-settings-git',
    'liri-files-git',
    'liri-appcenter-git',
    'liri-terminal-git',
    'liri-wallpapers-git',
    'liri-themes-git',
    'xorg-server',
    'xorg-server-utils',
    'mesa-libgl',
    'phonon-qt5-gstreamer'
]
PACKAGES_TO_REMOVE = []


class CommandError(Exception):
    """
    Exception raised when a command has failed.
    """
    pass


def download_file(url, dest_path):
    """
    Download file from `url` into `dest_path` destination location.
    """
    import requests
    import shutil
    r = requests.get(url, stream=True)
    if r.status_code == 200:
        with open(dest_path, 'wb') as f:
            total = r.headers.get('Content-Length')
            print('Downloading %s' % url)
            if total is None:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            else:
                total = int(total)
                written = 0
                for data in r.iter_content(chunk_size=4096):
                    written += len(data)
                    done = int(50 * written / total)
                    sys.stdout.write('\r[{}{}]'.format('=' * done, ' ' * (50 - done)))
                    sys.stdout.flush()
                sys.stdout.write('\n')
            return True
    return False


def find_iso():
    """
    Find an Arch Linux bootstrap ISO published in the last month, download
    the tarball and return its filename.
    """
    import calendar
    import datetime
    today = datetime.date.today()
    one_month_ago = today - datetime.timedelta(days=calendar.monthrange(today.year, today.month)[1])
    dates = [one_month_ago + datetime.timedelta(days=x) for x in range((today - one_month_ago).days + 1)]
    print('Searching for last archive...')
    for date in dates:
        iso_date = date.strftime('%Y.%m.%d')
        archive_filename = 'archlinux-bootstrap-{}-{}.tar.gz'.format(iso_date, ARCH_LINUX_ARCH)
        url = '{}/iso/{}/{}'.format(ARCH_LINUX_MIRROR, iso_date, archive_filename)
        if download_file(url, archive_filename):
            return archive_filename
    return None


def replace_in_file(filename, search, replace):
    """
    Replace `search` with `replace` on file `filename`.
    """
    with open(filename, 'r') as f:
        filedata = f.read()
    filedata = filedata.replace(search, replace)
    with open(filename, 'w') as f:
        f.write(filedata)


def append_to_file(filename, text):
    """
    Append `text` to file `filename`.
    """
    with open(filename, 'a') as f:
        f.write(text)


def mount_chroot(root_dir, chroot_dir):
    """
    Mount directory `root_dir` to `chroot_dir` for chroot.
    """
    os.system('mount --bind {} {}'.format(root_dir, chroot_dir))
    for dir in ('proc', 'sys', 'dev', 'dev/pts', 'dev/shm', 'run'):
        os.system('mount --bind /{dir} {to}/{dir}'.format(dir=dir, to=root_dir))


def umount_chroot(chroot_dir):
    """
    Unmount chroot mounted at `chroot_dir`.
    """
    for dir in ('proc', 'sys', 'dev/pts', 'dev/shm', 'dev', 'run'):
        os.system('umount {to}/{dir}'.format(dir=dir, to=chroot_dir))
    os.system('umount {}'.format(chroot_dir))


def chroot(chroot_dir, cmd):
    """
    Execute command `cmd` in the chroot `chroot_dir`.
    """
    print(cmd)
    if os.system('sudo setarch {arch} chroot {chroot} /bin/bash -c "{cmd}"'.format(arch=ARCH_LINUX_ARCH, chroot=chroot_dir, cmd=cmd)) != 0:
        raise CommandError('Chroot command failed')


def setup_dev(root_dir):
    """
    Create a static /dev directory for containers.
    """
    dev_dir = os.path.join(root_dir, 'dev')
    devices = {
        'null': {'mode': 666, 'args': 'c 1 3'},
        'zero': {'mode': 666, 'args': 'c 1 5'},
        'random': {'mode': 666, 'args': 'c 1 8'},
        'urandom': {'mode': 666, 'args': 'c 1 9'},
        'tty': {'mode': 666, 'args': 'c 5 0'},
        'console': {'mode': 600, 'args': 'c 5 1'},
        'tty0': {'mode': 666, 'args': 'c 4 0'},
        'full': {'mode': 666, 'args': 'c 1 7'},
        'initctl': {'mode': 600, 'args': 'p'},
        'ptmx': {'mode': 666, 'args': 'c 5 2'},
    }
    shutil.rmtree(dev_dir)
    os.makedirs(dev_dir)
    os.system('mkdir -m 755 {}'.format(os.path.join(dev_dir, 'pts')))
    os.system('mkdir -m 1777 {}'.format(os.path.join(dev_dir, 'shm')))
    os.symlink('/proc/self/fd', os.path.join(dev_dir, 'fd'))
    for device in devices:
        os.system('mknod -m {mode} {path}/{name} {args}'.format(name=device, path=dev_dir, mode=devices[device]['mode'], args=devices[device]['args']))


def setup_chroot(archive_filename):
    """
    Set OS root up uncompressing the `archive_filename` tar archive.
    """
    import tarfile
    # Remove previously unpacked tar
    root_dir = 'root.' + ARCH_LINUX_ARCH
    if os.path.exists(root_dir):
        shutil.rmtree(root_dir)
    # Extract base archive
    tar = tarfile.open(archive_filename, 'r')
    tar.extractall()
    tar.close()
    pacmanconf_filename = os.path.join(root_dir, 'etc', 'pacman.conf')
    mirror_filename = os.path.join(root_dir, 'etc', 'pacman.d', 'mirrorlist')
    resolvconf_filename = os.path.join(root_dir, 'etc', 'resolv.conf')
    # Do not require signed packages
    replace_in_file(pacmanconf_filename, 'SigLevel    = Required DatabaseOptional', 'SigLevel = Never')
    # Add Liri OS repository
    append_to_file(pacmanconf_filename, '\n[liri-unstable]\nSigLevel = Optional TrustAll\nServer = https://repo.liri.io/archlinux/unstable/$arch\n')
    # Add mirror
    append_to_file(mirror_filename, 'Server = {}/$repo/os/$arch\n'.format(ARCH_LINUX_MIRROR))
    # Add Google nameserver to resolv.conf
    append_to_file(resolvconf_filename, 'nameserver 8.8.8.8')
    # Mount chroot
    mount_chroot(root_dir, CHROOT_DIR)
    # Update packages, install Liri OS and setup
    chroot(CHROOT_DIR, 'pacman -Syu --noconfirm')
    chroot(CHROOT_DIR, 'pacman -S --noconfirm haveged procps-ng')
    chroot(CHROOT_DIR, 'haveged -w 1024; pacman-key --init; pkill haveged; pacman -Rs --noconfirm haveged; pacman-key --populate archlinux; pkill gpg-agent')
    if len(PACKAGES_LIST) > 0:
        chroot(CHROOT_DIR, 'pacman -S --noconfirm {}'.format(' '.join(PACKAGES_LIST)))
    if len(PACKAGES_TO_REMOVE) > 0:
        chroot(CHROOT_DIR, 'pacman -R --noconfirm {}'.format(' '.join(PACKAGES_TO_REMOVE)))
    # Setup locale
    chroot(CHROOT_DIR, 'ln -sf /usr/share/zoneinfo/UTC /etc/localtime')
    append_to_file(os.path.join(CHROOT_DIR, 'etc', 'locale.gen'), 'en_US.UTF-8 UTF-8')
    chroot(CHROOT_DIR, 'locale-gen')
    # Remove unnecessary files
    chroot(CHROOT_DIR, 'rm -rf /usr/share/man/* /usr/share/info/* /usr/share/doc/* /usr/include/* /usr/lib/pkgconfig /usr/lib/cmake /var/lib/pacman')
    # Unmount chroot
    umount_chroot(CHROOT_DIR)
    # Setup /dev
    setup_dev(root_dir)


def create_container(name):
    """
    Create a base container with the Arch Linux system.
    """
    if os.system('tar --numeric-owner --xattrs --acls -C root.{} -c . | docker import - {}'.format(ARCH_LINUX_ARCH, name)) != 0:
        raise CommandError('Failed to create container ' + name)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Create Arch Linux base container')
    parser.add_argument('-n', '--name', dest='name', type=str,
                        help='container name (default: %s)' % CONTAINER_NAME)
    parser.add_argument('--arch', dest='arch', type=str,
                        help='architecture (default: %s)' % ARCH_LINUX_ARCH)
    parser.add_argument('--mirror', dest='mirror', type=str,
                        help='alternative Arch Linux mirror (default: %s)' % ARCH_LINUX_MIRROR)
    parser.add_argument('--archive', dest='archive', type=str,
                        help='use this archive instead of downloading a new one')

    args = parser.parse_args()

    if args.name:
        CONTAINER_NAME = args.name
    if args.arch:
        ARCH_LINUX_ARCH = args.arch
    if args.mirror:
        ARCH_LINUX_MIRROR = args.mirror
    if args.archive:
        archive_filename = args.archive
    else:
        archive_filename = find_iso()
    if archive_filename:
        try:
            setup_chroot(archive_filename)
        except Exception as e:
            umount_chroot(CHROOT_DIR)
            raise e
        create_container(CONTAINER_NAME)
    else:
        print('Unable to find an Arch Linux ISO!', file=sys.stderr)
        sys.exit(1)
