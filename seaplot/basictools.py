"""
                            Generic tools
"""

import re
import os
import sys
import argparse
import numpy as np
import logging
import logging.config
import json
from ConfigParser import SafeConfigParser
from matplotlib.artist import setp


def check_file(prospective_file):

    if not os.path.exists(prospective_file):
        raise argparse.ArgumentTypeError("readable_file:'{0}' is not a valid "
                                         "path".format(prospective_file))
    if not os.access(prospective_file, os.R_OK):
        raise argparse.ArgumentTypeError("readable_file:'{0}' is not a "
                                         "readable file".format(prospective_file))


class ReadableFile(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if type(values) == list:
            for prospective_file in values:
                check_file(prospective_file)
        elif type(values) == str:
            check_file(values)
        setattr(namespace, self.dest, values)


def print_msg(content, desc, strformat=True):
    desc = "[%s]" % desc.upper() if desc else ''
    format_content = ''
    if len(content) > 63 and strformat:
        for i, letter in enumerate(content):
            if i % 63 == 0 and i != 0:
                format_content += "%s\n               \t" % letter
            else:
                format_content += letter
        content = format_content
    else:
        for letter in content:
            if letter == "\n":
                format_content += "%s               \t" % letter
            else:
                format_content += letter
        content = format_content
    return '''\
{desc:<15}\t{content}
'''.format(desc=desc, content=content)


def out_init(outpath=None, progname='', desc=''):
    """
    Init log file
    :param logpath:
    :param progname: docstring
    :param desc:
    :return:
    """
    out = '''
================================================================================
{progname}
                                {desc}
================================================================================
'''.format(progname=progname, desc=desc.capitalize())
    if outpath:
        with open(outpath, 'w') as out_file:
            out_file.write(out[1:])
    else:
        return out


def str2bool(string):
    """
    Convert string to bool
    :param string:
    :return:
    """
    if re.search("true", string, re.I):
        return True
    else:
        return False


def get_filename(path):
    """
    Search filename in the given path
    :param path:
    :return:
    """
    return "_".join(path.split("/")[-1].split(".")[:-1])


def print_2d_list(list_2d):
    """
    print 2d python list
    :param 2d_list: 2 dimension list
    :return: lines
    """
    lines = ''
    for row in list_2d:
        lines += '\t'.join(map(str, row)) + '\n'
    return lines


def sort_2dict(unsort_dict, key, reverse=True):
    """
    Sort 2d dict by key
    :return: sorted dict
    """
    sorted_index = sorted(unsort_dict, key=lambda x: float(unsort_dict[x][key]),
                          reverse=reverse)
    sorted_dict = {}

    for rank, ind in enumerate(sorted_index):
        sorted_dict[rank + 1] = unsort_dict[ind]

    return sorted_dict


def poplist_dict(full_dict, poplist):
    """
    pop values in a dict with a list of keys
    :param full_dict:
    :param poplist:
    :poplist: pop keys
    :return: cleaned dict
    """
    for key in poplist:
        if key and key in full_dict:
            full_dict.pop(key)
    return full_dict


def diff(list1, list2):
    """
    List all elements which are not in list1 and list2
    :param list1:
    :param list2:
    :return:
    """
    c = set(list1).union(set(list2))
    d = set(list1).intersection(set(list2))
    return list(c - d)


def get_list(list_arg, index):
    if list_arg:
        try:
            return list_arg[index]
        except IndexError:
            return None
    else:
        return None


def reg_load(regex, filepath, sort=None):
    """

    :param regex:
    :param filepath:
    :param sort:
    :return:
    """

    lines_dict = {}

    with open(filepath) as f:
        for index, line in enumerate(f):
            match = regex.match(line)
            if match:
                lines_dict[index] = match.groupdict()

    if sort:
        lines_dict = sort_2dict(lines_dict, sort)

    return lines_dict


def cart_dist(x, y):
    """
    Evaluate cartesian distance beetween 2 points x, y
    :param x: numpy array (len = n dimensions)
    :param y: numpy array (len = n dimensions)
    :return:
    """
    return np.sqrt(sum(np.power(x - y, 2)))


#                          Matplotlib functions                                #
# ---------------------------------------------------------------------------- #
def tickrot(axes, figure, rotype='horizontal', x=True, y=True):
    """
    Matplot rotation of ticks labels
    :param axes:
    :param figure:
    :param rotype:
    :param x:
    :param y:
    :return:
    """
    if y:
        setp(axes.get_yticklabels(), rotation=rotype)
    if x:
        setp(axes.get_xticklabels(), rotation=rotype)
    figure.canvas.draw()


def tickmin(pandata, ntick=10, shift=0):
    """
    Minimise number of ticks labels for matplotlib or seaborn plot
    :param pandata: pandas dataframe
    :param ntick: number of ticks wanted per axes
    :return:
    """
    yticks = pandata.index + shift
    keptticks = pandata.index[::(len(pandata.index) // int(ntick))]
    yticks = [ _ if _ in keptticks else '' for _ in yticks]
    # If shift != 0, need to initialize first value of ticks
    yticks[0] = min(pandata.index) + shift

    xticks = pandata.columns + shift
    keptticks = pandata.columns[::(len(pandata.columns) // int(ntick))]
    xticks = [_ if _ in keptticks else '' for _ in xticks]
    xticks[0] = min(pandata.columns) + shift

    return xticks, yticks


#                          Configuration file                                  #
# ---------------------------------------------------------------------------- #
def conf_load(conf_path):
    """
    Load configuration file
    :param conf_path:
    :return: dict parameters
    """
    config = SafeConfigParser()
    config.read(conf_path)

    conf_dict = {}

    for param in config.sections():
        conf_dict[param] = dict(config.items(param))

    return conf_dict


def setup_logging(path, outdir=None, default_level=logging.INFO):
    """
    Setup logging configuration
    """
    # TODO: detect path log filenames and makedirs if not exists
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = json.load(f)
            if outdir:
                for hand in config["handlers"]:
                    if "filename" in config["handlers"][hand]:
                        config["handlers"][hand]["filename"] = \
                            os.path.join(outdir, "log",
                                         config["handlers"][hand]["filename"])
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


def update_conf(config, newconfpath):
    """
    Update config dict with new config file
    :param config:
    :param newconfpath:
    :return:
    """
    newconfig = conf_load(newconfpath)
    for section in config.keys():
        if section in newconfig:
            config[section].update(newconfig[section])
    return newconfig
