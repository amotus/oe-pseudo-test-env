#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare a="$IMAGE_ROOTFS/etc/a.txt"
declare b="$IMAGE_ROOTFS/etc/b.txt"
declare c="$IMAGE_ROOTFS/etc/c.txt"

echo "content of a" > "$a"
ln "$a" "$b"

echo  "content of c" > "$c"
mv "$c" "$b"
