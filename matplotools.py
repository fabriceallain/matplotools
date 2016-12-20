#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
                        Seaborn plot command line tool
"""
from __future__ import absolute_import, division, print_function

# import matplotlib

# matplotlib.use("Agg")

import sys
import pandas as pd
import seaplot.iodata as io
from seaplot.graphics import *
from seaplot.basictools import *
from os import makedirs
from os.path import exists, dirname


# TODO: Lire sphinx (generateur de doc)
# TODO: class Dat
# TODO: class PlotSettings
# TODO: pour les options spécifiques a certains graphes, faire des classes
# qui etendent PlotSettings
# TODO: class Plot -> contient les méthodes save, show, ...
# TODO: utiliser parsers aria pour faire un fichier d'options du graphe en xml ?

#                                 Main                                         #
# ---------------------------------------------------------------------------- #
def settings(desc=None):
    """
    Parse args and options
    :param desc:
    :return: 2-tuple (opts, args)
    """
    argparser = argparse.ArgumentParser(description=desc,
                                        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    argparser.add_argument("plot_type", default=None, help="Type of plot")
    argparser.add_argument("file", metavar="FILE", help="input file (.dat)")
    argparser.add_argument("vars", metavar="VARS", nargs="*", help="Variables to plot")

    # Options
    argparser.add_argument("-c", "--conf", dest="conf_file", default=None,
                           help="configuration file")
    argparser.add_argument("-o", "--output", dest="output", default='plot.png',
                           help="output file")
    argparser.add_argument("-t", "--title", dest="title", default='Plot',
                           help="graph title")
    argparser.add_argument("--hue", dest="hue", default=None,
                           help="grouping factor")
    argparser.add_argument("--select", dest="select", default=None,
                           help="select rows. Syntax : 'field1=value1,"
                                "field2=value2, ...'")
    argparser.add_argument("--col", dest="col", default=None,
                           help="col dimension for facet plots")
    argparser.add_argument("--row", dest="row", default=None,
                           help="row dimension for facet plots")
    argparser.add_argument("--extra", dest="extra", default=None,
                           help="extra field on the same plot (poinplot)")
    argparser.add_argument("--xlim", dest='xlim', default=0, help="x lim")
    argparser.add_argument("--xrot", dest='xrot', action='store_true',
                           default=False, help="Rotate xtick labels")
    argparser.add_argument("--noerrbar", dest='errbar', action='store_false',
                           default=True, help="Don't draw errors bars")
    argparser.add_argument("--order", dest='order', default=None,
                           help="Level used to order data")
    argparser.add_argument("--estimator", dest='estimator', default="mean")
    argparser.add_argument("--sharex", dest='sharex', default=False, 
                           action='store_true')
    argparser.add_argument("--sharey", dest='sharey', default=False, 
                           action='store_true')
    argparser.add_argument("--joinpoint", dest='joinpoint', default=False,
                           action='store_true')

    options = argparser.parse_args()

    try:
        assert os.path.isfile(options.file)
    except AssertionError:
        argparser.error("Invalid Filename %s" % options.file)
    except TypeError:
        argparser.error("Input file %s  not set" % options.file)

    if not exists(os.path.abspath(
            os.path.join(os.path.dirname(options.output), "log"))):
        makedirs(os.path.abspath(
            os.path.join(os.path.dirname(options.output), "log")))

    return options, argparser.prog


def main():
    args, prog = settings(u"Script to generate seaborn plots")

    progname = prog[:-3]
    progdir = os.path.dirname(os.path.abspath(__file__))
    setup_logging('%s/logging.json' % progdir,
                  outdir=os.path.dirname(args.output))
    LOG = logging.getLogger("MAIN")
    print(out_init(progname=__doc__, desc='%s' % args.plot_type))
    LOG.info("""{plot} plot settings:
    vars: {vars}
    hue: {hue}
    col: {col}
    row: {row}\
""".format(plot=args.plot_type, vars=args.vars, col=args.col, hue=args.hue,
           row=args.row))
    try:
        # Load default configuration file
        config = conf_load("%s/%s.conf" % (progdir, progname))
        LOG.info("Loading default configuration file (%s/%s.conf)" % (
            progdir, progname))
        LOG.debug(json.dumps(config, indent=4))
    except AssertionError:
        sys.exit("No valid configuration file found. Please check if default "
                 "file in %s directory exist !" % progname)
    if args.conf_file:
        config = update_conf(config, args.conf_file)
        LOG.info("Update configuration dict")
        LOG.debug(json.dumps(config, indent=4))

    config = config['matplotools parameters']

    sns.set_style(config["style"])
    sns.set_context(config["context"])
    sns.set_palette(config["palette"])

    # -------------------------------- Input --------------------------------- #
    LOG.info("Loading Data from %s" % args.file)
    dataframe = pd.read_csv(args.file, low_memory=False)
    LOG.debug(dataframe)
    mygrid = None

    if args.select:
        LOG.info("Filtering rows using selection string")
        dataframe = io.subdata(dataframe, args.select)

    LOG.info("Saving dataframe (%s/df.p)" % dirname(args.output))
    dataframe.to_pickle("%s/df.p" % dirname(args.output))

    # logger.debug("X values :\n%s" % str(data[args.x]))
    # if len(data[args.x].unique()) <= 1:
    #     logger.error("Not enough unique values in %s axis !" % args.x)
    #     exit("Change x axis !")
    # else:
    #     logger.info("%d unique values in %s axis" % (
    #         len(data[args.x].unique()), args.x))

    # if args.y:
    #     logger.debug("Y values :\n%s" % str(data[args.y]))
    #     if len(data[args.y].unique()) <= 1:
    #         logger.error("Not enough unique values in %s axis !" % args.y)
    #         exit("Change y axis !")
    #     else:
    #         logger.info("%d unique values in %s axis" % (
    #             len(data[args.y].unique()), args.y))

    if args.xlim:
        xlim = [int(n) for n in args.xlim.split()]
    else:
        xlim = None

    # -------------------------------- Plot ---------------------------------- #
    x = args.vars[0] if len(args.vars) >= 1 else None
    y = args.vars[1] if len(args.vars) >= 2 else None
    if args.plot_type == "gridbar":
        mygrid = sns_facetplot(dataframe, x=x, y=y, config=config,
                               hue=args.hue, col=args.col, row=args.row,
                               plot_type="bar", join=args.joinpoint,
                               errbar=args.errbar, order=args.order,
                               palette=config.get("palette", "muted"), est=args.estimator)
    elif args.plot_type == "gridbox":
        mygrid = sns_facetplot(dataframe, x=x, y=y, config=config,
                               hue=args.hue, row=args.row, col=args.col,
                               join=args.joinpoint, order=args.order,
                               plot_type="box")
    elif args.plot_type == "gridpoint":
        mygrid = sns_facetplot(dataframe, x=x, y=y, config=config,
                               hue=args.hue, row=args.row, col=args.col,
                               join=args.joinpoint, plot_type="point",
                               errbar=args.errbar, dodge=0.3, sharex=args.sharex,
                               sharey=args.sharey)
    elif args.plot_type == "violin":
        # TODO check which one is discrete var
        mygrid = sns.violinplot(dataframe[y], dataframe[x], hue=args.hue,
                                scale_hue=False)
        LOG.info("Adding Legend")
        mygrid.add_legend()
        mygrid.fig.tight_layout()
    elif args.plot_type == "gridviolin":
        mygrid = sns.FacetGrid(dataframe, col=args.col, hue=args.hue, xlim=xlim,
                               size=5, sharex=args.sharex, row=args.row,
                               sharey=args.sharey)
        mygrid.map(sns.violinplot, x, y, scale="area")
        LOG.info("Adding legend")
        mygrid.add_legend()
        mygrid.fig.tight_layout()
    elif args.plot_type == "gridhist":
        # Compare number of observations for each distribution, if uneven =>
        # normed = True (See seaborn hist)
        mygrid = sns.FacetGrid(dataframe, col=args.col, xlim=xlim, size=5,
                               sharey=False, sharex=False, row=args.row,
                               hue=args.hue)
        # grid.map(sns.distplot, x, hist_kws=dict(alpha=0.5))
        mygrid.map(sns.countplot, x)
    elif args.plot_type == "gridswarmplot":
        mygrid = sns.FacetGrid(dataframe, col=args.col, xlim=xlim, size=5,
                               sharey=False, sharex=False, row=args.row,
                               hue=args.hue)
        # grid.map(sns.distplot, x, hist_kws=dict(alpha=0.5))
        mygrid.map(sns.swarmplot, x, y)
    elif args.plot_type == "gridscatterplot":
        mygrid = sns.FacetGrid(dataframe, col=args.col, size=4, row=args.row,
                               hue=args.hue)
        mygrid.map(plt.scatter, x=x, y=y)
    elif args.plot_type == "gridkde":
        LOG.info("Drawing KDE plot on grid")
        mygrid = sns_facetgrid(dataframe, x, config, kind="kde", y=y,
                               hue=args.hue, col=args.col, row=args.row,
                               xlim=args.xlim,
                               palette=config.get("palette", "muted"))
    elif args.plot_type == "gridkdejoin":
        mygrid = sns.FacetGrid(dataframe, col=args.col, size=4, row=args.row,
                               sharex=args.sharex, sharey=args.sharey,
                               hue=args.hue)
        mygrid.map(sns.kdeplot, x, y)
    elif args.plot_type == "gridjoin":
        mygrid = sns.FacetGrid(dataframe, col=args.col, size=4, row=args.row,
                               sharex=args.sharex, sharey=args.sharey,
                               hue=args.hue)
        mygrid.map(sns.jointplot, x, y)
    elif args.plot_type == "lmplot":
        mygrid = sns.lmplot(x=x, y=y, hue=args.hue, col=args.col,
                            row=args.row, data=dataframe, sharex=args.sharex,
                            sharey=args.sharey, logistic=True)
    elif args.plot_type == "pairgrid":
        data = dataframe.replace(np.inf, np.nan)
        mygrid = sns.PairGrid(data.dropna(), vars=args.vars, hue=args.hue)
        mygrid.map_diag(plt.hist)
        mygrid.map_upper(plt.scatter, alpha=config.get('alpha', 0.7))
        mygrid.map_lower(sns.regplot)
        mygrid.add_legend()
    elif args.plot_type == "pairplot":
        data = dataframe.replace(np.inf, np.nan)
        mygrid = sns.pairplot(data.dropna(), vars=args.vars, hue=args.hue)
    elif args.plot_type == 'gridmap':

        if args.col and args.row:
            dataframe = dataframe[[args.col, args.row, x, y, args.hue]]
        elif args.col or args.row:
            dataframe = dataframe[[args.col if args.col else args.row,
                                   x, y, args.hue]]
        else:
            dataframe = dataframe[[x, y, args.hue]]

        def facet_heatmap(data, dim1, dim2, **kws):
            data = data.groupby([dim1, dim2]).aggregate(np.mean).reset_index()
            LOG.debug(data)
            data = data.pivot(index=dim1, columns=dim2,
                              values='ca_rmsd_reference_structure_dsspali_pyfit')

            sns.heatmap(data, cmap='Blues',
                        **kws)  # <-- Pass kwargs to heatmap

        with sns.plotting_context(font_scale=5.5):
            g = sns.FacetGrid(dataframe, col=args.col, row=args.row, aspect=1,
                              sharey=False)

        cbar_ax = g.fig.add_axes(
            [.92, .3, .02, .4])  # <-- Create a colorbar axes

        g = g.map_dataframe(facet_heatmap, dim1=x, dim2=y,
                            cbar_ax=cbar_ax,
                            vmin=0,
                            vmax=10)  # <-- Specify the colorbar axes and limits

        g.set_titles(col_template="{col_name}", row_template="{row_name}",
                     fontweight='bold', fontsize=18)
        # g.set_yticklabels(rotation=0)
        [plt.setp(_.get_yticklabels(), rotation=0) for _ in g.axes.flat]
        g.fig.tight_layout()
        g.fig.subplots_adjust(right=.9)
        g.savefig(args.output, dpi=200)
        return None
    else:
        LOG.error("%s plot type isn't supported" % args.plot_type)

    if issubclass(mygrid.__class__, sns.Grid):
        # if args.hue and hasattr(mygrid, "add_legend"):
        #     mygrid.add_legend()
        # mygrid.fig.tight_layout()
        if config["xrot"] and len(mygrid.axes) > 1 and args.xrot:
            for ax in mygrid.axes.flat:
                _ = plt.setp(ax.get_xticklabels(), rotation=config["xrot"])
        elif args.xrot:
            mygrid.set_xticklabels(rotation=config["xrot"])
        mygrid.fig.canvas.draw()
    elif config["xrot"] and args.xrot:
        plt.xticks(rotation=config["xrot"])
        plt.tight_layout()
        plt.draw()

    LOG.info("Saving plot in %s" % args.output)

    if hasattr(mygrid, 'savefig'):
        mygrid.savefig(args.output, dpi=200)
    else:
        plt.savefig(args.output, bbox_inches='tight', pad_inches=.5)


if __name__ == '__main__':
    main()
