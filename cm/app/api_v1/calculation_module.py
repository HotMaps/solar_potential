import datetime
import json
import os
import sys
from osgeo import gdal
import numpy as np
import pandas as pd
import warnings
from collections import defaultdict
import reslib.pv as pv
import reslib.st as st
import reslib.plant as plant
import resutils.output as ro
import resutils.unit as ru
import resutils.raster as rr

from .solar_potential.energy_production import get_plants
from ..helper import generate_output_file_tif
from ..constant import CM_NAME

# TODO the token now is null, only 5 requests in one day,
# please set the environemnt variable with a TOKEN
# for renewable ninja
if "RES_NINJA_TOKENS" in os.environ:
    TOKEN = os.environ["RES_NINJA_TOKENS"]
else:
    warnings.warn("RES_NINJA_TOKENS variable not set.")
    TOKEN = None


def get_integral_error(pl, interval):
    """
    Compute the integrale of the production profile and compute
    the error with respect to the total energy production
    obtained by the raster file
    :parameter pl: plant
    :parameter interval: step over computing the integral

    :returns: the relative error
    """
    if pl.prof is not None:
        return (
            pl.energy_production - pl.prof["electricity"].sum() * interval
        ) / pl.energy_production


def run_source(
    kind,
    pl,
    data_in,
    most_suitable,
    n_plant_raster,
    output_suitable,
    discount_rate,
    ds,
    unit="kW",
):
    """
    Run the simulation and get indicators for the single source
    """
    pl.financial = plant.Financial(
        investement_cost=int(data_in["setup_costs"] * pl.peak_power),
        yearly_cost=data_in["tot_cost_year"],
        plant_life=data_in["financing_years"],
    )
    # pl.prof = None

    result = dict()
    if most_suitable.max() > 0:
        result["raster_layers"] = ro.get_raster(
            most_suitable, output_suitable, ds, kind
        )
        result["indicator"] = ro.get_indicators(
            kind, pl, most_suitable, n_plant_raster, discount_rate
        )

        # default profile
        if pl.prof is not None:
            if kind == "PV":
                tot_profile = pl.prof["electricity"].values * pl.n_plants
            else:
                tot_profile = pl.prof["thermal"].values * pl.n_plants
            default_profile, unit, con = ru.best_unit(
                tot_profile, unit, no_data=0, fstat=np.median, powershift=0
            )
            pl.prof[f"{kind} [{unit}]"] = default_profile

            graph = ro.line(
                x=ro.reducelabels(pl.prof.index.strftime("%d-%b %H:%M")),
                y_labels=["{} {} profile [{}]".format(kind, pl.resolution[1], unit)],
                y_values=[default_profile],
                unit=unit,
                xLabel=pl.resolution[0],
                yLabel="{} {} profile [{}]".format(kind, pl.resolution[1], unit),
            )

            # monthly profile of energy production
            df_month = pl.prof.groupby(pd.Grouper(freq="M")).sum()
            if kind == "PV":
                month_data = df_month["electricity"] * pl.n_plants
            else:
                month_data = df_month["thermal"] * pl.n_plants

            monthly_profile, unit, con = ru.best_unit(
                month_data.values, "kWh", no_data=0, fstat=np.median, powershift=0
            )
            graph_month = ro.line(
                x=df_month.index.strftime("%b"),
                y_labels=[
                    """"{} monthly energy
                                            production [{}]""".format(
                        kind, unit
                    )
                ],
                y_values=[monthly_profile],
                unit=unit,
                xLabel="Months",
                yLabel="{} monthly profile [{}]".format(kind, unit),
            )

            graphics = [graph, graph_month]
        else:
            graphics = []
        result["graphics"] = graphics
    return result


def calculation(output_directory, inputs_raster_selection, inputs_parameter_selection):
    """
    Main function
    """
    now = datetime.datetime.now()
    data = dict(output_directory=output_directory, inputs_raster_selection=inputs_raster_selection, inputs_parameter_selection=inputs_parameter_selection)
    with open(f"/tmp/req{now:%y-%m-%d_%H%M%S}.json", "w") as jsn:
        json.dump(data, jsn)

    # list of error messages
    # TODO: to be fixed according to CREM format
    messages = []
    # generate the output raster file
    output_suitable_pv = generate_output_file_tif(output_directory)
    output_suitable_st = generate_output_file_tif(output_directory)
    # retrieve the inputs layes
    ds = gdal.Open(inputs_raster_selection["climate_solar_radiation"])
    ds_geo = ds.GetGeoTransform()
    irradiation_values = ds.ReadAsArray()
    irradiation_values = np.nan_to_num(irradiation_values)

    ds = gdal.Open(inputs_raster_selection["building_footprint_tot_curr"])
    ds_geo = ds.GetGeoTransform()
    building_footprint = ds.ReadAsArray()
    building_footprint = np.nan_to_num(building_footprint)
    # set negative values: e.g. -3.4028235e+38 to 0
    building_footprint[building_footprint < 0] = 0

    # retrieve the inputs all input defined in the signature
    pv_in = {
        "roof_use_factor": float(
            float(inputs_parameter_selection["roof_use_factor_pv"]) / 100.0
        ),
        "target": float(inputs_parameter_selection["PV_target"]),
        "setup_costs": int(inputs_parameter_selection["setup_costs_pv"]),
        "tot_cost_year": (
            float(inputs_parameter_selection["maintenance_percentage_pv"])
            / 100
            * int(inputs_parameter_selection["setup_costs_pv"])
        ),
        "financing_years": int(inputs_parameter_selection["financing_years"]),
        "efficiency": float(inputs_parameter_selection["efficiency_pv"]),
        "peak_power": float(inputs_parameter_selection["peak_power_pv"]),
    }
    st_in = {
        "roof_use_factor": float(
            float(inputs_parameter_selection["roof_use_factor_st"]) / 100.0
        ),
        "target": float(inputs_parameter_selection["ST_target"]),
        "setup_costs": int(inputs_parameter_selection["setup_costs_st"]),
        "tot_cost_year": (
            float(inputs_parameter_selection["maintenance_percentage_st"])
            / 100
            * int(inputs_parameter_selection["setup_costs_st"])
        ),
        "financing_years": int(inputs_parameter_selection["financing_years"]),
        "efficiency": float(inputs_parameter_selection["efficiency_pv"]),
        "area": float(inputs_parameter_selection["area_st"]),
    }

    reduction_factor = float(inputs_parameter_selection["reduction_factor"]) / 100.0
    discount_rate = float(inputs_parameter_selection["discount_rate"])

    if (pv_in["roof_use_factor"] + st_in["roof_use_factor"]) > 1:
        st_in["roof_use_factor"] = 1.0 - pv_in["roof_use_factor"]
        message = (
            "Sum of roof use factors greater than 100. "
            "The roof use factor of the solar thermal has been "
            "reduced to {:2.1f}".format(st_in["roof_use_factor"] * 100.0)
        )
        warnings.warn(message)
        messages.append((message, "–", "–"))

    # define a pv plant with input features
    pv_plant = pv.PvPlant(
        id_plant="PV",
        peak_power=pv_in["peak_power"],
        k_pv=float(inputs_parameter_selection["k_pv"]),
        efficiency=pv_in["efficiency"],
    )
    # add information to get the time profile
    pv_plant_raster, most_suitable, pv_plant = get_plants(
        pv_plant,
        pv_in["target"],
        irradiation_values,
        building_footprint,
        pv_in["roof_use_factor"],
        reduction_factor,
    )
    
    pv_plant.prof = None
    pv_plant.n_plants = pv_plant_raster.sum()
    if pv_plant.n_plants > 0:
        pv_plant.lat, pv_plant.lon = rr.get_lat_long(ds, most_suitable)
        try:
            pv_plant.prof = pv_plant.profile()
            # check consistency betwen raster irradiation map and renewable.ninja
            error = get_integral_error(pv_plant, 1)
            if error > 0.05:
                msgtxt = (
                    f"Difference between raster value sum and {pv_plant.id} "
                    "profile total energy is:"
                )
                msgval = f"{error * 100.0:5.2}"
                msgunt = "%"
                message = f"{msgtxt}: {msgval} {msgunt}"
                warnings.warn(message)
                messages.append((msgtxt, msgval, msgunt))

            # fix profile to force consistency
            pv_plant.prof["electricity"] = pv_plant.prof["electricity"] / (1 - error)
            assert round(pv_plant.prof["electricity"].sum()) == round(
                pv_plant.energy_production
            )

            pv_plant.resolution = ["Hours", "hourly"]
        except Exception:
            messages.append(
                (
                    "Not able to reach the RenewableNinja website to retrieve the hourly values",
                    "-",
                    "-",
                )
            )

        res_pv = run_source(
            "PV",
            pv_plant,
            pv_in,
            most_suitable,
            pv_plant_raster,
            output_suitable_pv,
            discount_rate,
            ds,
            unit="kW",
        )
    else:
        # TODO: How to manage message
        res_pv = dict()
        message = "Not suitable pixels have been identified."
        warnings.warn(message)
        messages.append((message, "–", "–"))

    building_available = building_footprint - pv_plant_raster * pv_plant.area
    st_plant = st.StPlant(
        id_plant="ST",
        area=st_in["area"],
        efficiency=st_in["efficiency"],
        # add a default peak power of 1kW
        # in order to get raw data from ninja
        peak_power=1,
    )
    st_plant_raster, most_suitable, st_plant = get_plants(
        st_plant,
        st_in["target"],
        irradiation_values,
        building_available,
        st_in["roof_use_factor"],
        reduction_factor,
    )
    
    st_plant.prof = None
    st_plant.n_plants = st_plant_raster.sum()
    if st_plant.n_plants > 0:
        st_plant.lat, st_plant.lon = rr.get_lat_long(ds, most_suitable)
        try:
            hprof = st_plant.profile()
            # hourly profile to daily profile
            st_plant.prof = hprof.groupby(pd.Grouper(freq="D")).sum()
            st_plant.resolution = ["Days", "daily"]
        except Exception:
            messages.append(
                (
                    "Not able to reach the RenewableNinja website to retrieve the hourly values",
                    "-",
                    "-",
                )
            )

        res_st = run_source(
            "ST",
            st_plant,
            st_in,
            most_suitable,
            st_plant_raster,
            output_suitable_st,
            discount_rate,
            ds,
            unit="kWh",
        )
    else:
        # TODO: How to manage message
        res_st = dict()
        message = "Not suitable pixels have been identified."
        warnings.warn(message)
        messages.append((message, "-", "-"))
    dd = defaultdict(list)
    dd["name"] = CM_NAME
    dd["indicator"] = [
        {"unit": msgunt, "name": "WARNING: " + msgtxt, "value": msgval}
        for msgtxt, msgval, msgunt in messages
    ]
    # merge of the results
    for dic in [res_pv, res_st]:
        for d in dic:
            for u in dic[d]:
                dd[d].append(u)
    return dd
