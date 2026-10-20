# qt-static

Prebuilt static Qt 6 installs for the [ComBomb](https://github.com/cdesjardins/ComBomb)
release workflow. Building Qt takes one to two hours per platform. A CI cache
would be evicted between releases, so the builds are uploaded here once, as
release assets, and the workflow downloads the one it needs.

## Releases

Each release is one Qt build per platform, tagged `<qt version>-<n>`. `<n>` goes
up when the same Qt version is rebuilt with different options. The ComBomb
workflow pins the tag, so changing Qt is a deliberate one-line change there.

| asset | built with |
|---|---|
| `qt-<ver>-linux-x64-glibc2.35.tar.xz` | `ComBomb/build/docker-2204` (Ubuntu 22.04, gcc-12), qtbase + qtwayland |
| `qt-<ver>-windows-x86-msvc-static.tar.xz` | MSVC x86 developer prompt, `-static -static-runtime` |

The Windows build is 32-bit to match Boost and Botan in the ComBomb build. Each
archive holds the prefix contents at its root, plus a `QT_STATIC_INFO.txt` that
records the configure options.

## Adding a build

```bash
./package-qt.py ~/sw/qt6/Qt-2204 linux-x64-glibc2.35 \
    --config-opt ~/sw/qt6/qt6.8.3-build-2204/config.opt
gh release create 6.8.3-1 --title "Qt 6.8.3" qt-6.8.3-linux-x64-glibc2.35.tar.xz
```

On Windows, from the machine that built Qt:

```bat
py package-qt.py C:\Qt\6 windows-x86-msvc-static --config-opt <qt build dir>\config.opt
gh release upload 6.8.3-1 qt-6.8.3-windows-x86-msvc-static.tar.xz
```

## Using a build

Extract it into an empty directory and point `CMAKE_PREFIX_PATH` (or ComBomb's
`build.py --qt=`) at that directory. The CMake package files are relocatable,
so it does not have to be the prefix Qt was built for.
