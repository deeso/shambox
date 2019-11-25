import argparse
import os

from .util import Util

DEFAULT_SIZE = '8g'
BASE_DIRECTORY = '/data/memory_dumps/'
DST_DIRECTORY = BASE_DIRECTORY
SRC_DIRECTORY = BASE_DIRECTORY
DEFAULT_DIR = './'
OUTPUT_EXTENSION = '.diff'
DEFAULT_PAGE_SIZE = 4096

MEMSCRIMPER_COMMAND = 'docker run --rm -v {working_dir}:/data c /data/{reference} /data/{source} /data/{destination} {page_size} gzip 0 1'


parser = argparse.ArgumentParser(description='Run and snapshot vmware workstation.')

parser.add_argument('-page_size', default=DEFAULT_PAGE_SIZE, type=int,
                    help='page size for memscrimper')

parser.add_argument('-ramdisk_mount_point', default=None, type=str,
                    help='use ram mount point')

parser.add_argument('-ramdisk_size', default=DEFAULT_SIZE, type=str,
                    help='create ramdisk size')

parser.add_argument('-create_ramdisk', action='store_true',
                    help='create the ram disk mount point')

parser.add_argument('-src_base_dir', str=BASE_DIRECTORY,
                    help='source directory to read files from')

parser.add_argument('-wrk_base_dir', str=None,
                    help='directory where docker memscrimper will read and write from')

parser.add_argument('-dst_base_dir', str=BASE_DIRECTORY,
                    help='source directory to read files from')

parser.add_argument('-output_extension', str=OUTPUT_EXTENSION,
                    help='extension for the output diff files')

parser.add_argument('-reference', str=None, help='reference image name')
parser.add_argument('-sources', default=None, nargs='+',
                    help='source images to diff with the reference')

parser.add_argument('-unzip', action='store_true',
                    help='unzip memory dumps when needed')

parser.add_argument('-unzip_password', str=None,
                    help='unzip memory memory password')

parser.add_argument('-unmount', action="store_true",
                    help='unmount the ram disk')

parser.add_argument('-rm_src', action="store_true",
                    help='remove the source files')


class RunMemscrimper(object):

    def __init__(self, page_size=DEFAULT_PAGE_SIZE,
                 ram_disk_mount_point=None, ram_disk_size=DEFAULT_SIZE,
                 create_ram_disk=False, src_base_dir=DEFAULT_DIR,
                 dst_base_dir=DEFAULT_DIR, wrk_base_dir=DEFAULT_DIR,
                 output_extension=OUTPUT_EXTENSION, reference=None,
                 sources=None, unzip=False, unmount=False, rm_src=False):
        self.page_size = page_size
        self.ram_disk_mount_point = ram_disk_mount_point
        self.ram_disk_size = ram_disk_size
        self.create_ram_disk = create_ram_disk
        self.src_base_dir = src_base_dir
        self.dst_base_dir = dst_base_dir
        self.wrk_base_dir = wrk_base_dir
        self.output_extension = output_extension
        self.reference = reference
        self.sources = sources
        self.unzip = unzip
        self.unmount = unmount
        self.rm_src = rm_src

        source_files = self.sources
        self.src_base_names = [os.path.split(os.path.splitext(i[0]))[-1] for i in self.sources]
        self.dst_names = [".".join(i, self.output_extension) for i in self.src_base_names]

        self.ref_source = os.path.join(self.src_base_dir, self.reference)
        self.ref_working_input = os.path.join(self.wrk_base_dir, self.reference)
        self.ref_working_source = os.path.join(self.wrk_base_dir, self.reference)

        self._sources = [os.path.join(src_base_dir, sources)]

        self._working_srcs = [os.path.join(wrk_base_dir, sources)]

        self._working_dsts = [os.path.join(wrk_base_dir, self.dst_names)]


    @classmethod
    def execute_task(cls, fail=True, **kargs):
        rms = cls(**kargs)
        rms.execute(fail=fail)

    def execute(self, fail=True):

        if self.create_ram_disk and not Util.exists(self.ram_disk_mount_point):
            Util.create_dir(self.ram_disk_mount_point, fail=False)
            Util.update_perms(self.ram_disk_mount_point, fail=True)

        if self.ram_disk_mount_point is not None and not Util.exists(self.ram_disk_mount_point):
            Util.mount_ram_disk(self.ram_disk_mount_point)

        ms_kargs = {'working_dir': self.wrk_base_dir,
                    'reference': self.reference,
                    'page_size': self.page_size}

        for src, dst in zip(self.sources, self.dst_names):

            wsrc = os.path.join(self.wrk_base_dir, src)
            isrc = os.path.join(self.src_base_dir, src)

            wdst = os.path.join(self.wrk_base_dir, dst)
            odst = os.path.join(self.dst_base_dir, dst)
            # copy src to working directory
            Util.copy_file(isrc, wsrc, fail=fail)

            # execute memscrimper command
            ms_kargs['source'] = src
            cmd = MEMSCRIMPER_COMMAND.format(**ms_kargs)
            cp = Util.run_command(cmd, capture_output=True)

            # clean up
            if self.rm_src:
                Util.rm_file(wsrc, fail=fail)

            # copy result to destination
            Util.copy_file(wdst, odst, fail=fail)
            Util.rm_file(wdst, fail=fail)


        if self.unmount:
            Util.unmount_disk(self.ram_disk_mount_point, fail=fail)

        return True
