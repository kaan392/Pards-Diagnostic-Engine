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


def check_file_permissions():
    return _info(
        "Dosya ve dizin izinlerini kontrol eder.",
        [
            "ls -l",
            "namei -l \"${PATH}\""
        ]
    )


def check_permissions():
    return _info(
        "Mevcut kullanıcı ve temel izinleri kontrol eder.",
        [
            "id",
            "groups"
        ]
    )


def check_sudo_permissions():
    return _info(
        "Kullanıcının sudo yetkilerini kontrol eder.",
        [
            "id",
            "groups",
            "sudo -l"
        ]
    )


def install_sudo():
    return _action(
        "sudo paketini kurar.",
        "su -c 'apt install sudo'"
    )


def repair_sudoers():
    return _action(
        "Sudoers yapılandırmasını güvenli biçimde düzenlemek için visudo açar.",
        "sudo visudo"
    )


def diagnose_sudo():
    return _info(
        "sudo yapılandırmasını ve policy plugin durumunu inceler.",
        [
            "sudo -V",
            "sudo -l"
        ]
    )


def request_authentication():
    return _info(
        "Kimlik doğrulama gereksinimini ve mevcut kullanıcıyı kontrol eder.",
        [
            "id",
            "whoami"
        ]
    )


def check_authorization():
    return _info(
        "Kullanıcının yetki ve grup durumunu kontrol eder.",
        [
            "id",
            "groups",
            "sudo -l"
        ]
    )


def check_user_credentials():
    return _info(
        "Kullanıcı hesabının mevcut durumunu kontrol eder.",
        [
            "whoami",
            "passwd -S $(whoami)"
        ]
    )


def check_file_ownership():
    return _info(
        "Dosya ve dizin sahipliğini kontrol eder.",
        [
            "ls -l \"${PATH}\"",
            "stat \"${PATH}\""
        ]
    )


def check_directory_permissions():
    return _info(
        "Dizin erişim ve izinlerini kontrol eder.",
        [
            "ls -ld \"${PATH}\"",
            "namei -l \"${PATH}\""
        ]
    )


def diagnose_acl():
    return _info(
        "ACL izinlerini kontrol eder.",
        [
            "getfacl \"${PATH}\"",
            "setfacl --test \"${PATH}\""
        ]
    )


def diagnose_polkit():
    return _info(
        "Polkit servisinin ve authentication agent durumunu inceler.",
        [
            "systemctl status polkit --no-pager",
            "journalctl -u polkit -b -p err --no-pager"
        ]
    )


def diagnose_security_policy():
    return _info(
        "Sistem güvenlik politikalarının erişimi engelleyip engellemediğini inceler.",
        [
            "id",
            "journalctl -b -p err --no-pager | grep -Ei 'denied|authorization|policy'"
        ]
    )


def diagnose_selinux():
    return _info(
        "SELinux durumunu ve engellenen işlemleri inceler.",
        [
            "getenforce",
            "sestatus 2>/dev/null",
            "ausearch -m avc -ts recent 2>/dev/null"
        ]
    )


def diagnose_apparmor():
    return _info(
        "AppArmor durumunu ve engellenen işlemleri inceler.",
        [
            "aa-status 2>/dev/null",
            "journalctl -k -b --no-pager | grep -i apparmor"
        ]
    )


def diagnose_linux_capabilities():
    return _info(
        "Linux capability izinlerini kontrol eder.",
        [
            "getcap -r /usr/bin /usr/sbin 2>/dev/null",
            "capsh --print 2>/dev/null"
        ]
    )


def diagnose_filesystem():
    return _info(
        "Dosya sisteminin salt okunur olup olmadığını ve mount durumunu kontrol eder.",
        [
            "findmnt",
            "mount | grep ' ro[,)]'"
        ]
    )