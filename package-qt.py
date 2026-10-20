#!/usr/bin/env python3

# qt-static - prebuilt static Qt for the ComBomb release builds
# Copyright (c) 2026, Chris Desjardins
# https://github.com/cdesjardins/qt-static cjd@chrisd.info
#
# SPDX-License-Identifier: BSD-3-Clause

# Packs an installed static Qt prefix into qt-<version>-<platform>.tar.xz, the
# form the ComBomb release workflow downloads from this repository's releases.
#
#   ./package-qt.py ~/sw/qt6/Qt-2204 linux-x64-glibc2.35 \
#       --config-opt ~/sw/qt6/qt6.8.3-build-2204/config.opt
#   py package-qt.py C:\Qt\6 windows-x86-msvc-static --config-opt <build>\config.opt
#
# The archive holds the prefix's contents at its root (bin/, lib/, ...), so it
# is extracted straight into whatever directory is to become the Qt prefix.
# Qt's CMake package files are relocatable, so that need not be the path Qt was
# installed to; only qmake's .pri files and Qt6BuildInternals keep the original
# prefix, and building ComBomb uses neither.
#
# Standard library only, so it runs the same with the stock Python on Windows.

import argparse, hashlib, io, lzma, os, re, sys, tarfile, time

def qtVersion(prefix):
    path = os.path.join(prefix, "lib", "cmake", "Qt6", "Qt6ConfigVersionImpl.cmake")
    if (os.path.exists(path) == False):
        path = os.path.join(prefix, "lib", "cmake", "Qt6", "Qt6ConfigVersion.cmake")
    with open(path) as f:
        m = re.search(r'set\(PACKAGE_VERSION "([0-9.]+)"\)', f.read())
    if (m == None):
        sys.exit("Error: no PACKAGE_VERSION in " + path)
    return m.group(1)

def addText(tar, name, text):
    data = text.encode("utf-8")
    info = tarfile.TarInfo(name)
    info.size = len(data)
    info.mtime = int(time.time())
    info.mode = 0o644
    tar.addfile(info, io.BytesIO(data))

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    parser = argparse.ArgumentParser(description = "Package a static Qt install prefix")
    parser.add_argument("prefix", help = "Qt install prefix (the configure -prefix)")
    parser.add_argument("platform", help = "platform tag for the file name, e.g. linux-x64-glibc2.35")
    parser.add_argument("--config-opt", help = "the Qt build directory's config.opt, stored in the archive")
    parser.add_argument("-o", "--outdir", default = ".", help = "where to write the archive")
    args = parser.parse_args()

    prefix = os.path.abspath(os.path.expanduser(args.prefix))
    if (os.path.isdir(os.path.join(prefix, "lib", "cmake", "Qt6")) == False):
        sys.exit("Error: " + prefix + " is not a Qt6 install prefix")
    version = qtVersion(prefix)
    name = "qt-" + version + "-" + args.platform + ".tar.xz"
    out = os.path.join(os.path.abspath(args.outdir), name)

    info = "Qt " + version + " for " + args.platform + "\n" + \
           "Packaged " + time.strftime("%Y-%m-%d %H:%M:%S %Z") + " from " + prefix + "\n"
    if (args.config_opt != None):
        with open(os.path.expanduser(args.config_opt)) as f:
            info += "\nconfigure options (config.opt):\n" + f.read()

    print("Packing " + prefix + " -> " + out)
    sys.stdout.flush()
    # preset 6 keeps the pack time sensible; the Linux prefix comes out around
    # 125 MB either way. Entries are relative to the prefix, so it extracts
    # in place.
    with tarfile.open(out, "w:xz", preset = 6) as tar:
        for entry in sorted(os.listdir(prefix)):
            tar.add(os.path.join(prefix, entry), arcname = entry)
        addText(tar, "QT_STATIC_INFO.txt", info)

    size = os.path.getsize(out)
    print("%s  %.1f MB" % (name, size / 1e6))
    print("sha256 " + sha256(out))

if __name__ == "__main__":
    main()
