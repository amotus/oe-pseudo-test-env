#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.conf"
declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"

echo "content of ld.so.conf" > "$ldsoconf"
echo "content of ld.so.conf.prelink" > "$ldsoconf_prelink"


mv "$ldsoconf_prelink" "$ldsoconf"
