#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
                        Seaborn plot command line tool
"""

# TODO: Lire sphinx (generateur de doc)
# TODO: class Dat
# TODO: class PlotSettings
# TODO: pour les options spécifiques a certains graphes, faire des classes
# qui etendent PlotSettings
# TODO: class Plot -> contient les méthodes save, show, ...
# TODO: class AccuracyPlot(Plot)
# TODO: class PrecisionPlot(Plot)
# TODO: utiliser parsers aria pour faire un fichier d'options du graphe en xml ?


import sys

if sys.version_info < (2, 7):
    sys.exit("This program need Python version 2.7 !")

import pandas as pd
import seaplot.iodata as io
from seaplot.graphics import *
from seaplot.basictools import *
from os import makedirs
from os.path import exists


log = logging.getLogger(os.path.basename(__file__))


#                                 Main                                         #
# ---------------------------------------------------------------------------- #
def settings(desc=None):
    """
    Parse args and options
    :return: 2-tuple (opts, args)
    """
    argparser = argparse.ArgumentParser(description=desc,
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argparser.add_argument("plot_type", default="facetbar", help="Type of plot")
    argparser.add_argument("file", metavar="FILE",
                           help="input file (.dat)")
    argparser.add_argument("x", help="index x col")
    argparser.add_argument("y", nargs="?",
                           help="index y col. Can be a string for more than 1 "
                                "var separated by comma")

    # Options
    argparser.add_argument("-c", "--conf", dest="conf_file",
                           default='matplotools.conf', help="configuration file")
    argparser.add_argument("-o", "--output", dest="output",
                           default='plot.png', help="output file")
    argparser.add_argument("-t", "--title", dest="title",
                           default='Plot', help="graph title")
    argparser.add_argument("--hue", dest="hue", default=None,
                           help="grouping factor")
    argparser.add_argument("--select", dest="select",
                           default=None,
                           help="select rows. Syntax : 'field1=value1,"
                                "field2=value2, ...'")
    argparser.add_argument("--col", dest="col", default=None,
                           help="col dimension for facet plots")
    argparser.add_argument("--row", dest="row", default=None,
                           help="row dimension for facet plots")
    argparser.add_argument("--extra", dest="extra", default=None,
                           help="extra field on the same plot (poinplot)")
    argparser.add_argument("--xlim", dest='xlim', default=0,
                           help="x lim")

    options = argparser.parse_args()

    try:
        assert os.path.isfile(options.file)
    except AssertionError:
        argparser.error("Invalid Filename %s" % options.file)
    except TypeError:
        argparser.error("Input file %s  not set" % options.file)

    if not exists(os.path.abspath(os.path.join(os.path.dirname(options.output),
                                               "log"))):
        makedirs(os.path.abspath(os.path.join(os.path.dirname(options.output),
                                              "log")))

    return options, argparser.prog


def main():

    args, prog = settings(u"Script to generate seaborn plots")

    progname = prog[:-3]
    progdir = os.path.dirname(os.path.realpath(__file__))

    setup_logging('%s/seaplot/logging.json' % progdir,
                  outdir=os.path.dirname(args.output))

    log.info(out_init(progname=__doc__, desc='%s' % args.plot_type))
    log.info("""{plot} plot settings:
      x: {x}
      y: {y}
    hue: {hue}
    col: {col}
    row: {row}\
""".format(plot=args.plot_type, x=args.x, y=args.y, col=args.col, hue=args.hue,
           row=args.row))

    try:
        # Load default configuration file
        config = conf_load("%s/%s.conf" % (progdir, progname))
    except AssertionError:
        sys.exit("No valid configuration file found. Please check if default "
                 "file in %s directory exist !" % progname)
    if args.conf_file:
        config = update_conf(config, args.conf_file)

    config = config['matplotools parameters']

    # -------------------------------- Input --------------------------------- #
    log.info("Loading Data from %s" % args.file)
    data = pd.read_table(args.file, sep=',')

    if args.select:
        log.info("Filtering rows using selection string")
        data = io.subdata(data, args.select)

    if len(data[args.x].unique()) <= 1:
        log.error("Not enough unique values in %s axis !" % args.x)
        exit("Change x axis !")
    else:
        log.info("%d unique values in %s axis" % (len(data[args.x].unique()), args.x))

    if args.y:
        if len(data[args.y].unique()) <= 1:
            log.error("Not enough unique values in %s axis !" % args.y)
            exit("Change y axis !")
        else:
            log.info("%d unique values in %s axis" % (len(data[args.y].unique()),
                                                      args.y))

    # -------------------------------- Plot ---------------------------------- #
    if args.plot_type == "seabar":
        g = sns_facetplot(data, x=args.x, y=args.y, hue=args.hue,
                          col=args.col, row=args.row,
                          plot_type="bar", join=config["joinpoint"])
        g.fig.tight_layout()

    elif args.plot_type == "seabox":
        g = sns_facetplot(data, x=args.x, y=args.y, hue=args.hue, row=args.row,
                          col=args.col, join=config["joinpoint"],
                          plot_type="box")
        g.fig.tight_layout()
    elif args.plot_type == "seapoint":
        # TODO: pb avec seapoint !
        g = sns_facetplot(data, x=args.x, y=args.y, hue=args.hue,
                          col=args.col, join=args.joinpoint,
                          plot_type="point")
        g.fig.tight_layout()
    elif args.plot_type == "seaviolin":
        # TODO verifier lequel des deux est la variable discrete. Elle doit
        # etre fournit en deuxieme argument !
        g = sns.violinplot(data[args.y], data[args.x],
                           hue=args.col, scale_hue=False)
        g.fig.tight_layout()
    elif args.plot_type == "seafacetviolin":

        if args.xlim:
            xlim = [int(n) for n in args.xlim.split()]
        else:
            xlim = None

        g = sns.FacetGrid(data, col=args.col,
                             xlim=xlim, size=4,
                             row=args.row,
                             hue=args.hue)
        g.map(sns.violinplot, args.x, args.y)
        g.fig.tight_layout()
    elif args.plot_type == "facethist":
        # Compare number of observations for each distribution, if uneven =>
        # normed = True (See seaborn hist)
        if args.xlim:
            xlim = [int(n) for n in args.xlim.split()]
        else:
            xlim = None

        grid = sns.FacetGrid(data, col=args.col,
                             xlim=xlim, size=5, sharey=False, sharex=False,
                             row=args.row,
                             hue=args.hue)

        grid.map(sns.distplot, args.x, hist_kws=dict(alpha=0.5))
        grid.fig.tight_layout()
        grid.add_legend()
        # plt.hist(data[args.x])
        # plt.title(args.title)
        # plt.xlabel(args.x)
        # sns.distplot(data[arguments.x], 100, axlabel=arguments.x.capitalize())

    elif args.plot_type == "facetscatterplot":
        grid = sns.FacetGrid(data, col=args.col, size=4,
                             row=args.row,
                             hue=args.hue)
        grid.map(plt.scatter, args.x, args.y)
        grid.fig.tight_layout()
        grid.add_legend()
    elif args.plot_type == "kde":
        grid = sns_facetgrid(data, args.x, config, kind=args.plot_type,
                             y=args.y, hue=args.hue, col=args.col, row=args.row,
                             xlim=args.xlim)

    plt.savefig(args.output, bbox_inches='tight')

    return data


if __name__ == '__main__':
    main()
