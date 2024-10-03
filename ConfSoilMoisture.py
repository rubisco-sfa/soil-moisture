import ILAMB.ilamblib as il
import numpy as np
from cf_units import Unit
from ILAMB.Confrontation import Confrontation
from ILAMB.Variable import Variable


def is_volume_frac(var: Variable) -> bool:
    return (Unit(var.unit) / Unit("m3 m-3")).is_dimensionless()


def is_mass_area_density(var: Variable) -> bool:
    return (Unit(var.unit) / Unit("kg m-2")).is_dimensionless()


def shift_to_volume_frac(var: Variable) -> Variable:
    if not is_mass_area_density(var):
        raise ValueError("Only for mass area density")
    if var.layered:
        thick = var.depth_bnds[:, 1] - var.depth_bnds[:, 0]
        # This won't work for site data or if there isn't a time dimension
        var.data /= thick[np.newaxis, :, np.newaxis, np.newaxis]
        if var.data_bnds is not None:
            var.data_bnds /= thick[np.newaxis, :, np.newaxis, np.newaxis]
    else:
        # we are assuming that this is mrsos
        thick = 0.1
        var.data /= thick
        if var.data_bnds is not None:
            var.data_bnds /= thick
    var.unit = var.unit + " m-1"
    var.convert("1")
    return var


def integrate_depth_range(var: Variable, z0: float, zf: float) -> Variable:
    if var.layered:
        var = var.integrateInDepth(z0=z0, zf=zf, mean=True)
    else:
        # we are assuming that this is mrsos
        scale_factor = (zf - z0) / 0.1
        with np.errstate(all="ignore"):
            var.data *= scale_factor
            if var.data_bnds is not None:
                var.data_bnds *= scale_factor
    return var


class ConfSoilMoisture(Confrontation):

    def stageData(self, m):

        # Each soil moisture comparison needs to have this parameter
        depth_range = self.keywords.get("depth_range", None)
        if depth_range is None:
            raise ValueError(
                "Each SM comparison must have a depth_range given of the form `depth_range = z0,zf"
            )
        depth_range = [float(z.strip()) for z in depth_range.split(",")]

        # Get out observations just like usual
        obs = Variable(
            filename=self.source,
            variable_name=self.variable,
            alternate_vars=self.alternate_vars,
            t0=None if len(self.study_limits) != 2 else self.study_limits[0],
            tf=None if len(self.study_limits) != 2 else self.study_limits[1],
        )
        with np.errstate(all="ignore"):
            obs.data *= self.scale_factor
        if obs.time is None:
            raise il.NotTemporalVariable()
        self.pruneRegions(obs)

        mod = m.extractTimeSeries(
            self.variable,
            alt_vars=self.alternate_vars,
            expression=self.derived,
            initial_time=obs.time_bnds[0, 0],
            final_time=obs.time_bnds[-1, 1],
        )
        obs.trim(t=[mod.time_bnds[0, 0], mod.time_bnds[-1, 1]])

        # Unit conversions
        if is_volume_frac(obs) and is_mass_area_density(mod):
            mod = shift_to_volume_frac(mod)
        mod.convert(obs.unit)

        # Do integrations if needed
        if obs.layered:
            obs = integrate_depth_range(obs, depth_range[0], depth_range[1])
        mod = integrate_depth_range(mod, depth_range[0], depth_range[1])

        return obs, mod
