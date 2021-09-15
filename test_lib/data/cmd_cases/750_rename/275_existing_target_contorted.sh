#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.conf"
echo "content of ld.so.conf" > "$ldsoconf"

declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"
cp "$ldsoconf" "$ldsoconf_prelink"

declare ldsoconf_src="$IMAGE_ROOTFS/etc/ld.so.conf;613adfee"
echo "content of ld.so.conf source" > "$ldsoconf_src"
cat "$ldsoconf_src" > "$ldsoconf"

mv "$ldsoconf_prelink" "$ldsoconf"
