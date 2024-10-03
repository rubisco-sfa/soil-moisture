import ilamb3.dataset as dset
import xarray as xr
from ilamb3.analysis import bias_analysis
from ilamb3.compare import trim_time
from ilamb3.models import ModelESGF
from ilamb3.regions import Regions

# Register the Koppen climate regions into ILAMB system
ilamb_regions = Regions()
regions = [
    None,
] + ilamb_regions.add_netcdf("data/regions/Koppen.nc")
regions.pop(regions.index("polar"))

# Initialize the bias methodology
analysis = bias_analysis("mrsos")

# Read in and take a time mean of the reference mrsos data
ref = xr.open_dataset("data/Wang2021/mrsol_olc.nc").isel(dict(depth=0))
ref_mean = (
    ref.drop_vars("time_bnds")
    .weighted(dset.compute_time_measures(ref).pint.dequantify())
    .mean(dim="time")
).rename_vars({"mrsol": "mrsos"})

# Initialize a model, later we will loop over them
m = ModelESGF("CanESM5-1", "r1i1p1f1", "gn")
com = m.get_variable("mrsos")

# Trim the comparison to the time span of the reference
_, com = trim_time(ref, com)

# Now we take a time mean of the comparison
com_mean = (
    com.drop_vars("time_bnds")
    .weighted(dset.compute_time_measures(com).pint.dequantify())
    .mean(dim="time")
)

# Apply the bias analysis as it exists in ILAMB 2.7.2
df, ds_ref, ds_com = analysis(
    ref_mean,
    com_mean,
    method="Collier2018",
    regions=regions,
    use_uncertainty=False,
)

# Apply the bias analysis using the uncertainty to discount error
df_uncer, ds_ref_uncer, ds_com_uncer = analysis(
    ref_mean,
    com_mean,
    method="Collier2018",
    regions=regions,
    use_uncertainty=True,
)
