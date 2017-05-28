# -*- coding: utf-8 -*-

'''
make html from clustering result.
'''

import os
import argparse
import pickle
import shutil

from jinja2 import Environment, FileSystemLoader

from analysis_const import Const
from analysis_common import SourcePartInfo, SourceAccessor


TEMPLATE_SUB_DIR = 'templates'
RELATED_SUB_DIRS = ['styles', 'google-code-prettify']


def get_template_dir():
    my_dir = os.path.dirname(__file__)
    return os.path.join(my_dir, TEMPLATE_SUB_DIR)


def copy_related_files(out_base_dir):
    template_dir = get_template_dir()

    for sub_dir in RELATED_SUB_DIRS:
        dst_dir = os.path.join(out_base_dir, sub_dir)
        if os.path.exists(dst_dir):
            print(dst_dir + ' exists. no copied.')
            continue
        src_dir = os.path.join(template_dir, sub_dir)
        shutil.copytree(src_dir, dst_dir)


def save_html(out_file, data, src_accessor):

    def get_source_content(element):
        info = SourcePartInfo.from_dict(element)
        return src_accessor.get_content_by_info(info)

    render_dic = {
        'data': data,
        'helper': {
            'get_source_content': get_source_content,
        }
    }
    
    env = Environment(
        loader=FileSystemLoader(get_template_dir(), encoding='utf-8'),
        autoescape=True)
    template = env.get_template('similar.html')
    html = template.render(render_dic)
    with open(out_file, 'w', encoding='utf-8') as fl:
        fl.write(html)
    

def save_simple_text(out_file, data, src_accessor):
    cluster_sepalator = '=' * 76
    src_sepalator = '-' * 76
    
    with open(out_file, 'w', encoding='utf-8') as fl:
        fl.write('Summary\n\n')
        fl.write('distance threshold: %f\n\n' % data['distance_threshold'])
        for cluster in data['clusters']:
            fl.write('cluster %d distance=%f, represent=%d\n' % (
                cluster['index'], cluster['distance'], cluster['represent']))
            for elem in cluster['elements']:
                fl.write('    [%d] %s, %s, %d-%d\n' % (
                    elem['index'], elem['tag'], elem['path'],
                    elem['begin_line_num'], elem['end_line_num']))

        fl.write('\nContens\n')
        for cluster in data['clusters']:
            fl.write('\n' + cluster_sepalator + '\n')
            fl.write('cluster %d distance=%f, represent=%d\n' % (
                cluster['index'], cluster['distance'], cluster['represent']))
            for elem in cluster['elements']:
                fl.write(src_sepalator + '\n')
                fl.write('[%d] %s, %s, %d-%d\n' % (
                    elem['index'], elem['tag'], elem['path'],
                    elem['begin_line_num'], elem['end_line_num']))
                info = SourcePartInfo.from_dict(elem)
                fl.write(src_accessor.get_content_by_info(info))


def resolve_sub_dir(base_dir, sub_dir):
    if not os.path.exists(base_dir):
        os.mkdir(base_dir)
    join_dir = os.path.join(base_dir, sub_dir)
    if not os.path.exists(join_dir):
        os.mkdir(join_dir)
    return join_dir
    
                
def resolve_conf_path(conf, path, default_fname):
    if path is not None:
        return path
    return os.path.join(conf.out_dir, default_fname)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--pkl-file', default=None,
                        help='input info file saved as pickle')
    parser.add_argument('--source-root', '-s', default=None,
                        help='source root dir')
    parser.add_argument('--out-dir', '-o', default=Const.RESULT_DIR,
                        help='output dir')

    return parser.parse_args()


if __name__ == '__main__':
    conf = parse_args()

    src_accessor = SourceAccessor.create_empty(conf.source_root)

    pkl_file = resolve_conf_path(conf, conf.pkl_file, Const.SIMILAR_PKL_FNAME)
    with open(pkl_file, 'rb') as fl:
        data = pickle.load(fl)

    html_dir = resolve_sub_dir(conf.out_dir, Const.HTML_SUB_DIR)
        
    save_simple_text(os.path.join(html_dir, Const.SIMILAR_TEXT_FNAME),
                     data, src_accessor)

    save_html(os.path.join(html_dir, Const.SIMILAR_HTML_FNAME),
              data, src_accessor)
    copy_related_files(html_dir)
