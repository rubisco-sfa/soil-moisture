import intake_esgf
from pathlib import Path
import re
import matplotlib.pyplot as plt

intake_esgf.conf.set(
    all_indices=True, local_cache="/lustre/orion/cli137/world-shared/ESGF-data"
)

cat = intake_esgf.ESGFCatalog()
cat.search(
    source_id=[
        "ACCESS-ESM1-5",
        "AWI-ESM-1-1-LR",
        "BCC-ESM1",
        "CanESM5-1",
        "CESM2",
        "CMCC-ESM2",
        "CNRM-ESM2-1",
        "EC-Earth3-CC",
        "GFDL-ESM4",
        "GISS-E3-G",
        "IPSL-CM6A-LR",
        "MPI-ESM1-2-LR",
        "MRI-ESM2-0",
        "NorESM2-LM",
        "SAM0-UNICON",
        "TaiESM1",
        "UKESM1-0-LL",
    ],
    experiment_id="historical",
    variable_id=["mrsos", "mrsol", "gpp", "lai", "evspsbl"],
    frequency="mon",
).remove_incomplete(lambda df: True if len(df) == 5 else False).remove_ensembles()


setup = ""
i = 0
for s, m, g in cat.model_groups().index:
    sub_cat = intake_esgf.ESGFCatalog()
    sub_cat.search(
        experiment_id="historical",
        source_id=s,
        member_id=m,
        grid_label=g,
        variable_id=["mrsos", "mrsol", "gpp", "lai", "evspsbl"],
        frequency="mon",
    )
    try:
        ds = sub_cat.to_dataset_dict()
    except:
        print(f"{s=} {m=} {g=} Error")
        continue
    paths = sorted(
        list(
            set(
                [
                    str(Path(p).parent)
                    for p in re.findall(r"accessed\s(.*)\n", sub_cat.session_log())
                ]
            )
        )
    )
    paths = [p for p in paths if s in p]
    clr = plt.get_cmap("tab20").colors[i]
    clr = "#%02x%02x%02x" % (int(255 * clr[0]), int(255 * clr[1]), int(255 * clr[2]))
    i += 1
    model = f"""
{s}:
  modelname: {s}
  color: "{clr}"
  path: None
  paths:
{"\n".join([f"    - {path}" for path in paths])}
"""
    print(model)
    setup += model

with open("models.yaml", mode="w") as out:
    out.write(setup)
