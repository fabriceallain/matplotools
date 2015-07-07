import matplotlib.pyplot as plt
import seaborn as sns
import logging
from basictools import *


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

    plt.plot(columns[col1], columns[col2], aplha=ALPHA)

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
                   alpha=ALPHA,
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


def sns_facetplot(dataframe, x, y, hue=None, col=None, plot_type="b",
                  col_wrap=2, join=True, row=None):

    if hue:
        pal_keys = dataframe[hue].unique().tolist()
        pal_val = sns.color_palette("hls", len(pal_keys))
        pal_dict = dict(zip(pal_keys, pal_val))
    else:
        pal_dict = None
    if col:
        g = sns.factorplot(x, y, hue=hue, data=dataframe, col=col, join=join,
                           kind=plot_type, col_wrap=col_wrap,
                           palette=pal_dict, row=row, legend_out=False)
    else:
        g = sns.factorplot(x, y, hue=hue, data=dataframe, join=join, row=row,
                           kind=plot_type)

    g.add_legend()

    return g


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
                  row=None, xlim=None):
    xlim = [int(n) for n in xlim.split()] if xlim else None
    col_wrap = int(config["col_wrap"]) if col else None
    sharex = True if (row and not col) else False
    sharey = True if (col and not row) else False
    grid = sns.FacetGrid(dataframe, col=col, xlim=xlim, size=4, row=row,
                         hue=hue, col_wrap=col_wrap, sharex=sharex,
                         sharey=sharey)

    if kind == "kde":
        log.debug("Kdeplot on array below:\n %s" % dataframe[x].head())
        grid.map(sns.kdeplot, x, shade=str2bool(config["shade"]))

    grid.add_legend()
    grid.fig.tight_layout()
    return grid


def save_plot(out='plot.svg'):
    """

    :param out:
    :return:
    """
    return plt.savefig(out, bbox_inches='tight')
