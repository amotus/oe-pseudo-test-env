#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare a="$IMAGE_ROOTFS/etc/a.txt"
declare b="$IMAGE_ROOTFS/etc/b.txt"

touch "$a"
chmod a+rwx "$a"
# chown root:root "$a"
rm "$a"
# sleep 0.025
touch "$b"
