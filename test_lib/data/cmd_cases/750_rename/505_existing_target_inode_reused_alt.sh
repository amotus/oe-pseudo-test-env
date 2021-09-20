#!/usr/bin/env bash
set -euf -o pipefail

for _ in $(seq 1 3); do
  mkdir -p "$IMAGE_ROOTFS/etc"

  for i in $(seq 1 15); do
    declare ldsoconf="$IMAGE_ROOTFS/etc/ld.so.${i}.conf"
    declare ldsoconf_prelink="$IMAGE_ROOTFS/etc/ld.so.${i}.conf.prelink"

    echo "content of ld.so.${i}.conf.prelink" > "$ldsoconf_prelink"

    mv "$ldsoconf_prelink" "$ldsoconf"
    cp "$ldsoconf" "$ldsoconf_prelink"
    mv "$ldsoconf_prelink" "$ldsoconf"

    declare machineid="$IMAGE_ROOTFS/etc/machine-id-$i"
    touch "$machineid"
  done

  rm -r "${IMAGE_ROOTFS?}"
done