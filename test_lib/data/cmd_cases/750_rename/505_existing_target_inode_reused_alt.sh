#!/usr/bin/env bash
set -euf -o pipefail
mkdir -p "$IMAGE_ROOTFS/etc"

declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.conf"
declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.conf.prelink"

echo "content of ld.so.conf.prelink" > "$ldsoconf_prelink"

mv "$ldsoconf_prelink" "$ldsoconf"
cp "$ldsoconf" "$ldsoconf_prelink"
mv "$ldsoconf_prelink" "$ldsoconf"

for i in $(seq 1 20); do
  declare machineid="$IMAGE_ROOTFS/etc/machine-id-$i"
  touch "$machineid"
done

rm -r "${IMAGE_ROOTFS?}"
