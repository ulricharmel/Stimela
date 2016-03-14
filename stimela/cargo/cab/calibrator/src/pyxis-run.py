import Pyxis
import ms
import lsm
import mqt
import std
import stefcal
from Pyxis.ModSupport import *
import os
import json


mqt.MULTITHREAD = 16
INDIR = os.environ["INPUT"]
v.OUTDIR = os.environ["OUTPUT"]
CONFIG = os.environ["CONFIG"]
MSDIR = os.environ["MSDIR"]

LOG = II("${OUTDIR>/}log-calibrator.txt")


def readJson(conf):

    with open(conf) as _std:
        jdict = json.load(_std)

    for key,val in jdict.iteritems():
        if isinstance(val, unicode):
            jdict[key] = str(val)

    return jdict



def calibrate(jdict):

    x.sh("addbitflagcol $MS")

    prefix = jdict.get("prefix", None)

    for item in [INDIR, "/data/skymodels/"]:
        lsmname = "{:s}/{:s}".format(item, jdict["skymodel"])
        if os.path.exists(lsmname):
            break

    v.LSM = lsmname

    column = jdict.get("column", "DATA")

    ms.DDID = jdict.get("spw_id", 0)
    ms.FIELD = jdict.get("field_id", 0)

    options = {}
    options["tiggerlsm.lsm_subset"] = jdict.get("subset", "all")
    gtimeint, gfreqint = jdict.get("gjones_intervals", (1,1))

    options["stefcal_gain.timeint"] = gtimeint
    options["stefcal_gain.freqint"] = gfreqint
    options["stefcal_gain.flag_chisq_threshold"] = jdict.get("gjones_thresh_sigma", 10)
    options["stefcal_gain.flag_ampl_low"] = jdict.get("gjones_flag_ampl_low", 0.5)
    options["stefcal_gain.flag_ampl_high"] = jdict.get("gjones_flag_ampl_high", 2)

    stefcal.STEFCAL_DIFFGAIN_INTERVALS = jdict.get("ejones_intervals", None)
    stefcal.STEFCAL_DIFFGAIN_SMOOTHING = jdict.get("ejones_smoothing", None)
    stefcal.STEFCAL_GAIN_SMOOTHING = jdict.get("gjones_smoothing", None)

    ejones = jdict.get("ejones", False)
    options["ms_sel.input_column"] = column

    stefcal.stefcal(section="stefcal", gain_plot_prefix=prefix,
                    reset=True, dirty=False, 
                    diffgains=ejones,
                    options=options,
                    output=jdict.get("output_column", "CORR_RES"))

 
def azishe():
    jdict = readJson(CONFIG)

    msnames = jdict.get("msnames", jdict["msname"])

    if isinstance(msnames, (str, unicode)):
        msnames = [str(msnames)]


    v.MS_List = ["{:s}/{:s}".format(MSDIR, msname) for msname in msnames]

    cores = jdict.get("cpus", 1)
    Pyxis.Context["JOBS"] = cores

    per_ms(lambda: calibrate(jdict))
