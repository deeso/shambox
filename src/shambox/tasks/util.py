import os
import zipfile
import subprocess

DEFAULT_SIZE = '8g'
UPDATE_PERMS_RW = 'sudo chmod -R a+rw {location}'
CREATE_DIR = 'sudo mkdir -p {location}'
MOUNT_RAM_DISK = 'sudo mount -t tmpfs -o size={ramdisk_sz} tmpfs {mount_point}'
UNMOUNT_DISK = 'sudo umount {mount_point}'
UNZIP_COMMAND = 'unzip {source} -d {working_input}'
COPY_COMMAND = 'cp {source} {destination}'
RM_SOURCE_COMMAND = 'rm -rf {location}'


class Util:
    @staticmethod
    def run_command(cmd, capture_output=True):
        if isinstance(cmd, str):
            cmd = cmd.split()
        return subprocess.run(cmd, capture_output=capture_output)

    @staticmethod
    def post_run_command(cmd, error_msg=None, fail=False, expected_return_code=0, capture_output=True):
        cp = Util,run_command(cmd, capture_output=capture_output)
        if cp.returncode == expected_return_code:
            return True
        if fail:
            msg = "Failed: ({}): {}".format(cmd, error_msg)
            if error_msg is None:
                msg = "Failed: {}".format(cmd)
        return False

    @staticmethod
    def unzip_file(src, dst, fail=False, expected_return_code=0) -> bool:
        cmd = UNZIP_COMMAND.format(source=src, destination=dst).split()
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def copy_file(src, dst, fail=False, expected_return_code=0) -> bool:
        cmd = COPY_COMMAND.format(source=src, destination=dst).split()
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def rm_file(location, fail=False, expected_return_code=0) -> bool:
        cmd = RM_SOURCE_COMMAND.format(location).split()
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def mount_ram_disk(mount_point, ramdisk_sz=DEFAULT_SIZE, fail=False, expected_return_code=0) -> bool:
        cmd = MOUNT_RAM_DISK.format(ramdisk_sz=ramdisk_sz, mount_point=mount_point)
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def unmount_disk(mount_point, fail=False, expected_return_code=0) -> bool:
        cmd = UNMOUNT_DISK.format(mount_point=mount_point)
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def create_dir(location, fail=False, expected_return_code=0) -> bool:
        cmd = CREATE_DIR.format(location=location)
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def update_perms(location, fail=False, expected_return_code=0) -> bool:
        cmd = UPDATE_PERMS_RW.format(location=location)
        return Util.post_run_command(cmd, fail=fail, expected_return_code=expected_return_code)

    @staticmethod
    def exists(location, fail=False, expected_return_code=0) -> bool:
        return os.path.exists(location)

    @staticmethod
    def is_dir(location, fail=False, expected_return_code=0) -> bool:
        return os.path.isdir(location)

    @staticmethod
    def is_file(location, fail=False, expected_return_code=0) -> bool:
        return not Util.is_dir(location)

