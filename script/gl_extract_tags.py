# -*- coding: utf-8 -*-

'''
python gl_extract_tags.py projct_dir -o result_dir
'''

import os
import re
import argparse
import subprocess

from analysis_const import Const


def run_global(args, proj_dir, out_file):
    cmd_line = ' '.join(args)

    cwd = os.getcwd()
    try:
        os.chdir(proj_dir)
        proc = subprocess.Popen(args, shell=False, stdout=subprocess.PIPE)
    finally:
        os.chdir(cwd)

    with open(out_file, 'wb') as outf:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
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
    parser.add_argument('--target-list', '-t', default=None,
                        help='target list file(default: result/target_list.txt)')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    if conf.target_list is not None:
        list_file = conf.target_list
    else:
        list_file = os.path.join(conf.out_dir, Const.TARGET_LIST_FNAME)
    list_file = os.path.abspath(list_file)

    if not os.path.exists(conf.out_dir):
        os.mkdir(conf.out_dir)

    cmd_prefix = [Const.CMD_GLOBAL, '-f', '-L', list_file]

    out_file = os.path.join(conf.out_dir, Const.TAGS_DEF_FNAME)
    run_global(cmd_prefix + ['-d'], conf.proj_dir, out_file)

    out_file = os.path.join(conf.out_dir, Const.TAGS_REF_FNAME)
    run_global(cmd_prefix + ['-r'], conf.proj_dir, out_file)

    out_file = os.path.join(conf.out_dir, Const.TAGS_SYM_FNAME)
    run_global(cmd_prefix + ['-s'], conf.proj_dir, out_file)
