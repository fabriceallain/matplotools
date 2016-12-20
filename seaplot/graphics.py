import matplotlib.pyplot as plt
# import logging
from basictools import *
import seaborn as sns
import numpy as np

log = logging.getLogger("Plot")


def autolabel(rects):
    # attach some text labels
    for rect in rects:
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2., 1.05 * height,
                 '%d' % int(height), ha='center', va='bottom')


def facetgrid_set(grid, title):
    grid.set_titles(title)


def basic_plot(data_dict, col1=0, col2=1):
    """

    :param data_dict:
    :return:
    """
    columns = zip(*data_dict['content'])

    plt.plot(columns[col1], columns[col2], aplha=0.5)

    return


def barv_plot(data_dict, colx=0, coly=1, width=0.25, n_plot=0, label=None):
    """

    :param data_dict:
    :return:
    """
    columns = zip(*data_dict['content'])

    n_groups = len(columns[colx])
    x = np.arange(n_groups)

    ax = plt.subplot(111)
    rect = plt.bar(x + (n_plot * width), columns[coly], width=width,
                   alpha=0.5,
                   label=label, color=plt.rcParams['axes.color_cycle'][n_plot])
    plt.xticks(x + ((n_plot + 1) * width) / 2., columns[colx], rotation=45, size='x-small')

    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * 0.1,
                    box.width, box.height * 0.9])
    plt.legend(bbox_to_anchor=(0., -0.25), loc=2, borderaxespad=0.,
               fancybox=True)
    plt.xlabel('')
    autolabel(rect)

    return


def sns_bar(dataframe, x, y, hue=None):
    return sns.factorplot(x, y, data=dataframe, hue=hue, kind="bar")


def sns_facetplot(dataframe, x, y, config, hue=None, col=None, plot_type="b",
                  col_wrap=None, join=False, row=None, errbar=True,
                  sharex=False, sharey=False, order=None, palette="muted",
                  dodge=False, est="mean"):
    sns.set_palette(palette)
    xorder = dataframe.sort_values(by=order)[x].unique() if order else sorted(
        dataframe[x].unique())
    kw = {}

    if est == "max":
        from numpy import max
        est = max
    else:
        from numpy import mean
        est = mean

    if not errbar and plot_type in ("bar", "point"):
        log.info("Draw plot without err bar")
        kw['ci'] = None
    if plot_type == "point":
        kw['dodge'] = dodge
    if hue:
        pal_keys = dataframe[hue].unique().tolist()
        pal_val = sns.color_palette("hls", len(pal_keys))
        pal_dict = dict(zip(pal_keys, pal_val))
        # pal_dict = None
    else:
        pal_dict = sns.color_palette("hls", len(dataframe[x].unique().tolist()))
    if col:
        # col_wrap = int(config["col_wrap"]) if col and not row else None
        grid = sns.factorplot(x, y, hue=hue, data=dataframe, col=col,
                              kind=plot_type, col_wrap=col_wrap, size=5,
                              order=xorder,
                              sharey=sharey, sharex=sharex,
                              palette=pal_dict, row=row, estimator=est, **kw)
    else:
        grid = sns.factorplot(x, y, hue=hue, data=dataframe, row=row,
                              kind=plot_type, size=5,
                              order=xorder,
                              sharex=sharex,
                              sharey=sharey, estimator=est, **kw)
    return grid


def sns_pairplot(dataframe, x, y, hue=None, plot_type="b"):
    g = sns.PairGrid(data=dataframe, x_vars=x, y_vars=y,
                     size=3,
                     aspect=2)

    if plot_type == "bar":
        g.map(sns.barplot, hue=hue, data=dataframe)
    elif plot_type == "p":
        g.map(sns.pointplot, hue=hue, data=dataframe)

    locs, labels = plt.xticks()
    plt.setp(labels, rotation=30)
    g.fig.tight_layout()
    g.add_legend()
    return g


def sns_facetgrid(dataframe, x, config, kind="hist", y=None, hue=None, col=None,
                  row=None, xlim=None, palette="muted"):
    sns.set_palette(palette)
    xlim = [int(n) for n in xlim.split()] if xlim else None
    col_wrap = int(config["col_wrap"]) if col and not row else None
    sharex = config["sharex"]
    sharey = config["sharey"]
    grid = sns.FacetGrid(dataframe, col=col, xlim=xlim, size=4, row=row,
                         hue=hue, col_wrap=col_wrap, sharex=sharex,
                         sharey=sharey, legend_out=True, aspect=1.5)

    if kind == "kde":
        log.debug("Kdeplot on array below:\n %s" % dataframe[x].head())
        grid.map(sns.kdeplot, x, shade=config["shade"])
        grid.add_legend()

    return grid


def save_plot(out='plot.svg'):
    """

    :param out:
    :return:
    """
    return plt.savefig(out, bbox_inches='tight')
