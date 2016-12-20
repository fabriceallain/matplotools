import sys
import pandas as pd
import numpy as np
import logging

log = logging.getLogger("IO")


def sns_load(filepath, sep=','):
    """

    :param filepath:
    :param sep: field separator
    :return:
    """
    return pd.read_table(filepath, sep=sep, dtype='unicode')


def sns_data_eq(dataframe, sel=None, selec=None):
    sub = None
    try:
        if isinstance(selec, str):
            if "|" in selec:
                if dataframe[sel].dtype == np.int64:
                    selec = [int(x) for x in selec.split("|")]
                elif dataframe[sel].dtype == np.float64:
                    selec = [float(x) for x in selec.split("|")]
                else:
                    selec = selec.split("|")
                sub = dataframe.loc[dataframe[sel].isin(selec)]
            elif ".." in selec:
                selec = selec.split("..")
                selec = range(int(selec[0]), int(selec[1]) + 1)
                log.info("Range selection: %s in %s" % (
                    sel, selec))
                sub = dataframe[dataframe[sel].isin(selec)]
            else:
                log.info("Selection: %s =  %s" % (sel, selec))
                if dataframe[sel].dtype == np.int64:
                    selec = int(selec)
                elif dataframe[sel].dtype == np.float64:
                    selec = float(selec)
                elif dataframe[sel].dtype == np.bool:
                    selec = bool(selec)
                sub = dataframe.loc[dataframe[sel] == selec]
    except AssertionError:
        log.error("Wrong selection for these data.")
        sys.exit(2)
    except KeyError as msg:
        log.error("Selection doesn't exist!\n%s" % msg)
        sys.exit(2)
    except TypeError as msg:
        log.error("Selection type doesn't fit dataframe column type (%s).\n%s" %
                  (dataframe[sel].dtype, msg))
        sys.exit(2)
    return sub


def subdata(dataframe, selec):
    """
    Select submatrix of input panda dataframe
    :param dataframe:
    :param selec:
    :return:
    """
    for sel_str in selec.split(","):
            sel_str = sel_str.split("=")
            sel = sel_str[0]
            val = sel_str[1]
            log.info("Selecting rows where %s = %s" % (sel, val))
            dataframe = sns_data_eq(dataframe, sel, selec=val)
            log.debug("Dataframe selected %s" % dataframe)

    log.debug("""Dataframe selected below
{data}""".format(data=dataframe.to_string()))

    if dataframe.empty:
        log.error("Dataframe selected is empty !")
        sys.exit("Check selection criteria !")

    return dataframe
