import re
import os
import sys

path = os.path.abspath(os.path.join(__file__,"..","..","..","..",".."));

print "Path: "+str(path)

results = {}
plots = {}

def findModel(*frags):
    rfrags = map(lambda x: re.compile(x), frags)
    res = []
    root = os.path.join(path, "ModelicaByExample")
    for ent in os.walk(root):
        for f in ent[2]:
            if f=="package.mo":
                continue
            match = True
            full = os.path.join(ent[0], f)
            rel = full[(len(path)+1):]
            modname = rel[:-3].replace("/",".")
            for rfrag in rfrags:
                if len(rfrag.findall(modname))==0:
                    match = False
            if match:
                entry = (full, rel, modname)
                res.append(entry)
    if len(res)==1:
        return res[0]
    else:
        print "Unable to find a unique match for "+str(frags)+" matches include:"
        for r in res:
            print str(r)
        sys.exit(1)

def add_case(frags, res, stopTime=1.0, tol=1e-3, ncp=500, mods={}):
    mod = findModel(*frags)
    if res in results:
        raise NameError("Result %s already exists!" % (res,))
    data = {
        "name": mod[2],
        "stopTime": stopTime,
        "tol": tol,
        "ncp": ncp,
        "mods": mods
    };
    results[res] = data

class Var(object):
    def __init__(self, name, legend=None, style="-"):
        self.name = name
        self.style = style
        if legend==None:
            self.legend = name
        else:
            self.legend = legend
    def dict(self):
        return {"name": self.name, "legend": self.legend, "style": self.style}
    def __repr__(self):
        return repr(self.dict())

simple_plot_tmpl = """
# Autogenerated script to plot named %s using results: %s
from xogeny.plot_utils import render_simple_plot
render_simple_plot(name=%s, vars=%s, title=%s, legloc=%s, ylabel=%s)
""";

comp_plot_tmpl = """
# Autogenerated script to plot results for model
# %s
from xogeny.plot_utils import render_comp_plot
render_comp_plot(%s, %s, %s, %s, title=%s, legloc=%s, ylabel=%s)
""";

def add_simple_plot(plot, vars, title, legloc="upper right", ylabel="", res=None):
    if plot in plots:
        raise NameError("Plot named "+plot+" already exists");
    if res==None:
        res = plot
    if not res in results:
        raise NameError("Unable to find result "+res+" for plot "+plot)
    r = results[res]

    plots[plot] = {
        "type": "simple",
        "vars": vars,
        "title": title,
        "legloc": legloc,
        "ylabel": ylabel,
        "res": res
    };

def add_compare_plot(plot, res1, v1, res2, v2, title, legloc="lower right", ylabel=""):
    if plot in plots:
        raise NameError("Plot "+plot+" already exists")
    if not res1 in results:
        raise NameError("Unable to find result "+res1+" in plot "+plot)
    if not res2 in results:
        raise NameError("Unable to find result "+res2+" in plot "+plot)

    plots[plot] = {
        "type": "compare",
        "res1": res1,
        "v1": v1,
        "res2": res2,
        "v2": v2,
        "title": title,
        "legloc": legloc,
        "ylabel": ylabel
    };

def _generate_plots():
    for plot in plots:
        pdata = plots[plot]
        with open(os.path.join(path, "text", "plots", plot+".py"), "w+") as ofp:
            if pdata["type"]=="simple":
                ofp.write(simple_plot_tmpl % (repr(plot), repr(pdata["res"]),
                                              repr(pdata["res"]),
                                              repr(pdata["vars"]), repr(pdata["title"]),
                                              repr(pdata["legloc"]), repr(pdata["ylabel"])))
            elif pdata["type"]=="compare":
                ofp.write(comp_plot_tmpl % (repr(plot),
                                            repr(pdata["res1"]), repr(pdata["v1"]),
                                            repr(pdata["res2"]), repr(pdata["v2"]),
                                            repr(pdata["title"]),
                                            repr(pdata["legloc"]), repr(pdata["ylabel"])))
            else:
                raise ValueError("Unknown plot type: "+str(pdata["type"]))

script_tmpl = """
loadModel(ModelicaServices);
loadModel(Modelica);
setModelicaPath(getModelicaPath()+":"+"%s");
loadModel(ModelicaByExample);
    
simulate(%s, stopTime=%g, tolerance=%g, numberOfIntervals=%d, fileNamePrefix="%s", simflags="%s");
"""

def _generate_makefile():
    with open(os.path.join(path, "text", "results", "Makefile"), "w+") as ofp:
        ofp.write("all: ");
        for res in results:
            ofp.write("%s_res.mat " % (res,));
        ofp.write("\n\n");
        for res in results:
            data = results[res]
            mods = data["mods"]
            if len(mods)==0:
                simflags = ""
            else:
                simflags = "-override "+(",".join(map(lambda x: str(x)+"="+str(mods[x]), mods)))
            with open(os.path.join(path, "text", "results", res+".mos"), "w+") as sfp:
                args = (path, data["name"], data["stopTime"],
                        data["tol"], data["ncp"], res, simflags)
                sfp.write(script_tmpl % args);
            ofp.write("%s_res.mat:\n" % (res,));
            ofp.write("\tomc %s.mos\n" % (res,));

        ofp.write("tidy:\n");
        ofp.write("\t-rm *.o *.c *.xml *.h *.libs *.log *.makefile\n");
        for res in results:
            ofp.write("\t-rm %s\n" % (res,));

def generate():
    _generate_plots()
    _generate_makefile()
