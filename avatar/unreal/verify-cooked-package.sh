#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 || ! -d "$1" ]]; then
    printf 'Usage: %s /path/to/cooked/archive\n' "${0##*/}" >&2
    exit 64
fi

archive_root=$(cd "$1" && pwd -P)

mapfile -t executables < <(find "$archive_root" -type f -perm -u+x -print)
mapfile -t containers < <(find "$archive_root" -type f \( -name '*.pak' -o -name '*.utoc' \) -print)

arm64_executable=
for candidate in "${executables[@]}"; do
    description=$(file -b "$candidate")
    if [[ "$description" == *"ELF 64-bit"* && "$description" == *"ARM aarch64"* ]]; then
        arm64_executable=$candidate
        printf 'ARM64 executable: %s\n' "$candidate"
        printf '  %s\n' "$description"
        break
    fi
done

if [[ -z "$arm64_executable" ]]; then
    printf 'error: no Linux AArch64 executable found under %s\n' "$archive_root" >&2
    exit 1
fi
if [[ ${#containers[@]} -eq 0 ]]; then
    printf 'error: no cooked .pak or .utoc container found under %s\n' "$archive_root" >&2
    exit 1
fi

printf 'Cooked content containers: %s\n' "${#containers[@]}"
printf 'Package verification passed.\n'
