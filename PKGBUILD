# Maintainer: gabesan21
# This PKGBUILD is for local installation only: run `makepkg -si` from the
# repository root. This personal fork is not published on the Arch User Repository.

pkgname=youtui-player
pkgver=1.3.2
pkgrel=1
pkgdesc="YouTube TUI player with playlist, thumbnails and Catppuccin themes"
arch=('x86_64' 'aarch64')
url="https://github.com/gabesan21/youtui-player"
license=('MIT')
depends=('mpv' 'yt-dlp' 'socat')
makedepends=('go')

prepare() {
  cd "$startdir"
  go mod download
}

build() {
  cd "$startdir"
  export CGO_ENABLED=0
  go build \
    -trimpath \
    -ldflags "-X main.Version=$pkgver -s -w" \
    -o "$pkgname" .
}

package() {
  cd "$startdir"
  install -Dm755 "$pkgname" "$pkgdir/usr/bin/$pkgname"
  install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
  install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
}
