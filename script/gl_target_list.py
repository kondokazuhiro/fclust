# -*- coding: utf-8 -*-

'''
python gl_target_list.py projct_dir -o result_dir
'''

import os
import re
import argparse
import subprocess

from analysis_const import Const


def run_global_path(proj_dir, out_file):
    args = [Const.CMD_GLOBAL, '-P']
    cmd_line = ' '.join(args)

    cwd = os.getcwd()
    try:
        os.chdir(proj_dir)
        proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE,
                                universal_newlines=True)
    finally:
        os.chdir(cwd)

    with open(out_file, 'w') as outf:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            if re.match(Const.TARGET_FNAME_PATTERN, line, re.IGNORECASE):
                outf.write(line)
        proc.wait()

    if proc.returncode != 0:
        raise RuntimeError('ERROR: "%s" returned %d' % (
            cmd_line, proc.returncode))


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('proj_dir',
                        help='project dir that contains GTAGS file')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')
    #parser.add_argument('--suffixes', '-s', nargs='+', default=None,
    #                    help='suffixes of target file name')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    # GTAGSROOT を指定すると、出力に余分なパスが付加される.
    # GTAGSROOT: The root directory of the project.
    #     Usually, it is recognized by existence of GTAGS.
    # https://www.gnu.org/software/global/globaldoc_toc.html
    #os.environ['GTAGSROOT'] = os.path.abspath(conf.proj_dir)
    #print(os.environ['GTAGSROOT'])

    if not os.path.exists(conf.out_dir):
        os.mkdir(conf.out_dir)

    out_file = os.path.join(conf.out_dir, Const.TARGET_LIST_FNAME)
    run_global_path(conf.proj_dir, out_file)
