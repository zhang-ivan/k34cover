from verify_gdd_45 import verify_gdd_45, summary
import importlib.util, sys

# load your bibd.py
spec = importlib.util.spec_from_file_location("bibd_mod", "bibd.py")
mod = importlib.util.module_from_spec(spec); sys.modules["bibd_mod"] = mod
spec.loader.exec_module(mod)

exceptlist = [52, 53, 56, 57, 60, 61, 64, 65, 68, 69, 72, 73, 76, 77, 101, 104, 105, 108, 109]

# for v in exceptlist:
#
#     design, groups = mod.u45(v)
#     ok, rep = verify_gdd_45(v, design, groups)
#     print(summary(rep))



u = 96

design, groups = mod.u45(u)
ok, rep = verify_gdd_45(u, design, groups)
print(summary(rep))