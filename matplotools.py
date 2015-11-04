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
# TODO: utiliser parsers aria pour faire un fichier d'options du graphe en xml ?


import sys

if sys.version_info < (2, 7):
    sys.exit("This program need Python version 2.7 !")

import pandas as pd
import numpy as np
import seaplot.iodata as io
from seaplot.graphics import *
from seaplot.basictools import *
from os import makedirs
from os.path import exists


#                                 Main                                         #
# ---------------------------------------------------------------------------- #
def settings(desc=None):
    """
    Parse args and options
    :return: 2-tuple (opts, args)
    """
    argparser = argparse.ArgumentParser(description=desc,
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argparser.add_argument("plot_type", default=None, help="Type of plot")
    argparser.add_argument("file", metavar="FILE",
                           help="input file (.dat)")
    argparser.add_argument("x", help="index x col")
    argparser.add_argument("y", nargs="?",
                           help="index y col. Can be a string for more than 1 "
                                "var separated by comma")

    # Options
    argparser.add_argument("-c", "--conf", dest="conf_file",
                           default=None, help="configuration file")
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
    argparser.add_argument("--xrot", dest='xrot', action='store_true',
                           default=False,
                           help="Rotate xtick labels")
    argparser.add_argument("--noerrbar", dest='errbar', action='store_false',
                           default=True,
                           help="Don't draw errors bars")
    argparser.add_argument("--order", dest='order', default=None,
                           help="Level used to order data")

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
    progdir = os.path.dirname(os.path.abspath(__file__))
    setup_logging('%s/logging.json' % progdir,
                  outdir=os.path.dirname(args.output))
    logger = logging.getLogger()
    logger.info(out_init(progname=__doc__, desc='%s' % args.plot_type))
    logger.info("""{plot} plot settings:
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
        logger.info("Loading default configuration file (%s/%s.conf)" % (
            progdir, progname))
        logger.debug(json.dumps(config, indent=4))
    except AssertionError:
        sys.exit("No valid configuration file found. Please check if default "
                 "file in %s directory exist !" % progname)
    if args.conf_file:
        config = update_conf(config, args.conf_file)
        logger.info("Update configuration dict")
        logger.debug(json.dumps(config, indent=4))

    config = config['matplotools parameters']

    sns.set_style(config["style"])
    sns.set_context(config["context"])
    sns.set_palette(config["palette"])

    # -------------------------------- Input --------------------------------- #
    logger.info("Loading Data from %s" % args.file)
    data = pd.read_table(args.file, sep=',')
    grid = None

    if args.select:
        logger.info("Filtering rows using selection string")
        data = io.subdata(data, args.select)

    if len(data[args.x].unique()) <= 1:
        logger.error("Not enough unique values in %s axis !" % args.x)
        exit("Change x axis !")
    else:
        logger.info("%d unique values in %s axis" % (len(data[args.x].unique()), args.x))

    if args.y:
        if len(data[args.y].unique()) <= 1:
            logger.error("Not enough unique values in %s axis !" % args.y)
            exit("Change y axis !")
        else:
            logger.info("%d unique values in %s axis" % (len(data[args.y].unique()),
                                                         args.y))

    if args.xlim:
        xlim = [int(n) for n in args.xlim.split()]
    else:
        xlim = None

    # -------------------------------- Plot ---------------------------------- #
    if args.plot_type == "gridbar":
        grid = sns_facetplot(data, x=args.x, y=args.y, config=config,
                             hue=args.hue, col=args.col, row=args.row,
                             plot_type="bar", join=config["joinpoint"],
                             errbar=args.errbar, order=args.order)
    elif args.plot_type == "gridbox":
        grid = sns_facetplot(data, x=args.x, y=args.y, config=config,
                             hue=args.hue, row=args.row, col=args.col,
                             join=config["joinpoint"], order=args.order,
                             plot_type="box")
    elif args.plot_type == "gridpoint":
        grid = sns_facetplot(data, x=args.x, y=args.y, config=config,
                             hue=args.hue, row=args.row, col=args.col,
                             join=config["joinpoint"], plot_type="point",
                             errbar=args.errbar)
    elif args.plot_type == "violin":
        # TODO check which one is discrete var
        grid = sns.violinplot(data[args.y], data[args.x], hue=args.hue,
                              scale_hue=False)
    elif args.plot_type == "gridviolin":
        grid = sns.FacetGrid(data, col=args.col, hue=args.hue,
                             xlim=xlim, size=5, sharex=config["sharex"],
                             row=args.row, sharey=config["sharey"])
        grid.map(sns.violinplot, args.x, args.y)
    elif args.plot_type == "gridhist":
        # Compare number of observations for each distribution, if uneven =>
        # normed = True (See seaborn hist)
        grid = sns.FacetGrid(data, col=args.col,
                             xlim=xlim, size=5, sharey=False, sharex=False,
                             row=args.row,
                             hue=args.hue)
        grid.map(sns.distplot, args.x, hist_kws=dict(alpha=0.5))
    elif args.plot_type == "gridscatterplot":
        grid = sns.FacetGrid(data, col=args.col, size=4,
                             row=args.row,
                             hue=args.hue)
        grid.map(plt.scatter, x=args.x, y=args.y)
    elif args.plot_type == "gridkde":
        logger.info("Drawing KDE plot on grid")
        grid = sns_facetgrid(data, args.x, config, kind="kde",
                             y=args.y, hue=args.hue, col=args.col, row=args.row,
                             xlim=args.xlim)
    elif args.plot_type == "gridkdejoin":
        grid = sns.FacetGrid(data, col=args.col, size=4,
                             row=args.row, sharex=config["sharex"],
                             sharey=config["sharey"], hue=args.hue)
        grid.map(sns.kdeplot, args.x, args.y)
    else:
        logger.error("%s plot type isn't supported" % args.plot_type)

    if issubclass(grid.__class__, sns.Grid):
        # if args.hue and hasattr(grid, "add_legend"):
        #     grid.add_legend()
        # grid.fig.tight_layout()
        if config["xrot"]\
                and isinstance(grid, np.ndarray) \
                and len(grid.axes) > 1 \
                and args.xrot:
            for ax in grid.axes.flat:
                _ = plt.setp(ax.get_xticklabels(), rotation=config["xrot"])
        elif args.xrot:
            grid.set_xticklabels(rotation=config["xrot"])
        grid.fig.canvas.draw()
    elif config["xrot"] and args.xrot:
        plt.xticks(rotation=config["xrot"])
        plt.tight_layout()
        plt.draw()

    logger.info("Saving plot in %s" % args.output)
    plt.savefig(args.output, bbox_inches='tight', pad_inches=.5)


if __name__ == '__main__':
    main()
