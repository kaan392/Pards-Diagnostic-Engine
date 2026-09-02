def _info(description, commands):
    return {
        "description": description,
        "commands": commands,
        "requires_confirmation": False
    }


def _action(description, command):
    return {
        "description": description,
        "command": command,
        "requires_confirmation": True
    }


def check_disk_usage():
    return _info(
        "Disk kullanımını ve doluluk oranlarını kontrol eder.",
        [
            "df -h",
            "df -i",
            "du -xhd1 / 2>/dev/null | sort -h"
        ]
    )


def diagnose_filesystem():
    return _info(
        "Dosya sistemi durumunu ve olası I/O hatalarını inceler.",
        [
            "findmnt",
            "lsblk -f",
            "dmesg -T | grep -Ei 'read-only filesystem|I/O error|filesystem'"
        ]
    )


def diagnose_storage_device():
    return _info(
        "Depolama cihazının durumunu ve kernel hata kayıtlarını inceler.",
        [
            "lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS,MODEL",
            "dmesg -T | grep -Ei 'I/O error|Buffer I/O|blk_update_request|medium error'",
            "cat /proc/partitions"
        ]
    )


def diagnose_ext4():
    return _info(
        "EXT4 dosya sistemi hata ve uyarı kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'EXT4-fs|ext4'",
            "lsblk -f",
            "findmnt -t ext4"
        ]
    )


def diagnose_xfs():
    return _info(
        "XFS dosya sistemi hata kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'XFS'",
            "lsblk -f",
            "findmnt -t xfs"
        ]
    )


def diagnose_btrfs():
    return _info(
        "BTRFS dosya sistemi hata ve uyarı kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'BTRFS|btrfs'",
            "lsblk -f",
            "findmnt -t btrfs"
        ]
    )


def run_filesystem_check():
    return _action(
        "Dosya sistemi kontrolünün çalıştırılması için uygun cihazın belirlenmesini ister.",
        "lsblk -f"
    )


def diagnose_filesystem_check():
    return _info(
        "Dosya sistemi kontrolü ve fsck hatalarını inceler.",
        [
            "journalctl -b --no-pager | grep -Ei 'fsck|filesystem check'",
            "dmesg -T | grep -Ei 'fsck|filesystem'",
            "lsblk -f"
        ]
    )


def run_filesystem_repair():
    return _action(
        "Dosya sistemi onarımı için uygun bölümün belirlenmesini sağlar.",
        "lsblk -f"
    )


def diagnose_filesystem_journal():
    return _info(
        "Dosya sistemi journal hatalarını inceler.",
        [
            "dmesg -T | grep -Ei 'journal|checksum|aborted'",
            "journalctl -k -b -p err --no-pager",
            "lsblk -f"
        ]
    )


def diagnose_mount():
    return _info(
        "Dosya sistemi bağlama hatalarını inceler.",
        [
            "findmnt",
            "lsblk -f",
            "journalctl -b --no-pager | grep -Ei 'mount failed|mounting|mount'"
        ]
    )


def diagnose_filesystem_type():
    return _info(
        "Bölümün dosya sistemi türünü ve mount yapılandırmasını kontrol eder.",
        [
            "lsblk -f",
            "blkid",
            "findmnt"
        ]
    )


def diagnose_filesystem_superblock():
    return _info(
        "Dosya sistemi superblock durumunu inceler.",
        [
            "lsblk -f",
            "blkid",
            "dmesg -T | grep -Ei 'superblock|EXT4-fs|filesystem'"
        ]
    )


def diagnose_ata_device():
    return _info(
        "ATA/SATA cihaz hata kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'ata error|ata[0-9]|SATA'",
            "lsblk -o NAME,SIZE,MODEL,SERIAL",
            "journalctl -k -b -p err --no-pager"
        ]
    )


def diagnose_storage_link():
    return _info(
        "Depolama bağlantısı ve link reset kayıtlarını inceler.",
        [
            "dmesg -T | grep -Ei 'hard resetting link|link reset|SATA'",
            "lsblk -o NAME,MODEL,TRAN",
            "journalctl -k -b -p err --no-pager"
        ]
    )


def diagnose_nvme():
    return _info(
        "NVMe cihaz ve controller hata kayıtlarını inceler.",
        [
            "nvme list 2>/dev/null",
            "dmesg -T | grep -Ei 'nvme|timeout|reset controller'",
            "lsblk -o NAME,SIZE,MODEL,TRAN"
        ]
    )


def check_smart_health():
    return _info(
        "Depolama cihazının SMART sağlık durumunu kontrol eder.",
        [
            "lsblk -d -o NAME,MODEL,TYPE",
            "smartctl --scan-open 2>/dev/null",
            "dmesg -T | grep -Ei 'SMART|health'"
        ]
    )


def check_disk_quota():
    return _info(
        "Disk kota kullanımını ve kota sınırlarını kontrol eder.",
        [
            "quota -s 2>/dev/null",
            "repquota -a 2>/dev/null",
            "df -h"
        ]
    )


def check_mount_point():
    return _info(
        "Mount point'in mevcut olup olmadığını ve mount yapılandırmasını kontrol eder.",
        [
            "findmnt",
            "cat /etc/fstab",
            "ls -ld \"${MOUNT_POINT}\""
        ]
    )


def diagnose_busy_device():
    return _info(
        "Meşgul olan depolama cihazını kullanan işlemleri belirler.",
        [
            "lsblk",
            "fuser -vm \"${DEVICE}\"",
            "lsof \"${DEVICE}\" 2>/dev/null"
        ]
    )