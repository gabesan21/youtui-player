#!/usr/bin/env bash
#
# install.sh — compila e instala o youtui-player no PATH do sistema.
#
# Uso:
#   ./install.sh                    instala em /usr/local/bin (pede sudo)
#   PREFIX="$HOME/.local" ./install.sh
#
set -euo pipefail

PREFIX="${PREFIX:-/usr/local}"
BINDIR="$PREFIX/bin"
BINARY="youtui-player"

# ── cores ──────────────────────────────────────────────────────────
if [[ -t 1 ]]; then
	B=$'\e[1m'; D=$'\e[2m'; R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; C=$'\e[36m'; N=$'\e[0m'
else
	B=""; D=""; R=""; G=""; Y=""; C=""; N=""
fi

step() { printf "\n${B}${C}▸ %s${N}\n" "$1"; }
ok()   { printf "  ${G}✓${N} ${B}%-10s${N} %s\n" "$1" "$2"; }
miss() { printf "  ${R}✗${N} ${B}%-10s${N} ${D}%s${N}\n" "$1" "não encontrado"; }
die()  { printf "\n${R}${B}✗ %s${N}\n" "$1" >&2; exit 1; }

# ── banner ─────────────────────────────────────────────────────────
printf "${B}${C}"
cat <<'EOF'
╭────────────────────────────────────────────╮
│        youtui-player · instalador          │
╰────────────────────────────────────────────╯
EOF
printf "${N}"

# ── dependências ───────────────────────────────────────────────────
MISSING=()

check() { # nome, comando de versão...
	local name="$1"; shift
	if ! command -v "$name" >/dev/null 2>&1; then
		miss "$name"
		MISSING+=("$name")
		return
	fi
	ok "$name" "$("$@" 2>/dev/null | head -n1)"
}

step "Verificando dependências de compilação"
check go go version

step "Verificando dependências de execução"
check mpv    mpv --version
check yt-dlp yt-dlp --version
check socat  socat -V
check ffmpeg ffmpeg -version

# ── instalação das dependências faltantes ──────────────────────────
if ((${#MISSING[@]})); then
	step "Dependências faltando: ${MISSING[*]}"

	if [[ -f /etc/arch-release ]]; then
		printf "  Sistema detectado: ${B}Arch Linux${N}\n\n"
		printf "  ${Y}sudo pacman -S --needed %s${N}\n" "${MISSING[*]}"
	elif [[ -f /etc/debian_version ]]; then
		printf "  Sistema detectado: ${B}Debian/Ubuntu${N}\n\n"
		printf "  ${Y}sudo apt install %s${N}\n" "${MISSING[*]/yt-dlp/python3-pip}"
		if [[ " ${MISSING[*]} " == *" yt-dlp "* ]]; then
			printf "  ${Y}pip3 install -U yt-dlp${N}  ${D}(pacote apt é desatualizado)${N}\n"
		fi
	else
		printf "  ${Y}Arch:${N}    sudo pacman -S --needed %s\n" "${MISSING[*]}"
		printf "  ${Y}Debian:${N}  sudo apt install %s\n" "${MISSING[*]/yt-dlp/python3-pip}"
	fi

	printf "\n"
	read -rp "  Instalar automaticamente agora? [s/N] " ans || ans=""
	[[ "$ans" =~ ^[sSyY]$ ]] || die "Instale as dependências e rode o script novamente."

	if [[ -f /etc/arch-release ]]; then
		sudo pacman -S --needed "${MISSING[@]}"
	elif [[ -f /etc/debian_version ]]; then
		apt_pkgs=()
		for d in "${MISSING[@]}"; do
			if [[ "$d" == yt-dlp ]]; then
				apt_pkgs+=(python3-pip)
			else
				apt_pkgs+=("$d")
			fi
		done
		sudo apt update
		sudo apt install -y "${apt_pkgs[@]}"
		if [[ " ${MISSING[*]} " == *" yt-dlp "* ]]; then
			pip3 install -U yt-dlp --break-system-packages 2>/dev/null \
				|| pip3 install --user -U yt-dlp
		fi
	else
		die "Distribuição não reconhecida — instale manualmente: ${MISSING[*]}"
	fi

	STILL=()
	for d in "${MISSING[@]}"; do
		command -v "$d" >/dev/null 2>&1 || STILL+=("$d")
	done
	((${#STILL[@]})) && die "Ainda faltando após a instalação: ${STILL[*]}"
	printf "\n  ${G}✓ Dependências instaladas${N}\n"
fi

# ── build ──────────────────────────────────────────────────────────
step "Compilando o projeto"
make build

# ── instalação ─────────────────────────────────────────────────────
step "Instalando em $BINDIR"
if ! install -Dm755 "$BINARY" "$BINDIR/$BINARY" 2>/dev/null; then
	printf "  ${D}(permissão necessária — usando sudo)${N}\n"
	sudo install -Dm755 "$BINARY" "$BINDIR/$BINARY"
fi

printf "\n${B}${G}"
cat <<'EOF'
╭────────────────────────────────────────────╮
│         ✓ Instalado com sucesso!           │
╰────────────────────────────────────────────╯
EOF
printf "${N}"
printf "  Binário:  %s\n" "$BINDIR/$BINARY"
printf "  Execute:  %s\n\n" "$BINARY"
