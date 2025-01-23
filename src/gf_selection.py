import os
import sys
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from multiprocessing import Pool, cpu_count
import plotly.graph_objects as go
import plotly.express as px

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "pydplan"))
sys.path.insert(0, project_root)

from pydplan_profiletools import calculatePlan, DivePlan, TankType


# Source: Van Liew, H. D., and E. T. Flynn. A simple probabilistic model for estimating the risk of standard air dives. NEDU TR 04-42, Navy Experimental Diving Unit, 2004.
a = -6.022169
b = 86.596315
c = 25.091718
d = 0.002929
f = 0.918547
g = -170.304442

FEET_IN_METER = 3.2808399

# These are based on PADI tables Product No. 66054 Ver 1.2 (Rev. 02/03)
# https://www.a1scubadiving.com/wp-content/uploads/2018/06/PADI-Recreational-Dive-Table-Planner.pdf
btt = pd.read_csv("../data/bottom_time.csv")
sfi = pd.read_csv("../data/surface_interval.csv")
rnt = pd.read_csv("../data/residual_nitrogen_time.csv")


def get_standair_tdt(D, T, pdcs):
    D_feet = D * FEET_IN_METER
    logit = math.log(pdcs / (1 - pdcs))
    numerator = b*(D_feet-c)*(1-np.exp(-d * T**f))
    TDT = numerator / (logit - a) + g

    # Negative values correspond to no deco. Set TDT to 0.
    TDT = np.clip(TDT, a_min=0, a_max = np.inf)
    
    return TDT

def standair_plot(D, T_ref, pdcs_ref):
    T = np.linspace(0, T_ref * 2, 100)
    fig = go.Figure()

    for pdcs in [0.01, 0.015, 0.02, 0.025, 0.03,]:
        TDT = get_standair_tdt(D, T, pdcs)
        fig.add_trace(go.Scatter(
            x=T,
            y=TDT,
            mode='lines',
            name=f'pDCS = {pdcs}'
        ))

    TDT_ref = get_standair_tdt(D, T_ref, pdcs_ref)
    fig.add_trace(go.Scatter(
        x=[T_ref],
        y=[TDT_ref],
        mode='markers',
        name='Your plan',
        marker=dict(size=10, color='red', symbol='circle')
    ))

    fig.update_layout(
        title=f'StandardAir Model for {D:.1f}m',
        xaxis_title='T',
        yaxis_title='TDT',
        yaxis=dict(range=[0, max(10, TDT_ref * 2)]),
        legend=dict(title='Legend'),
        template='plotly_white'
    )
    fig.show()


def get_gf_tdt(T, D, gf_high, he, o2, plot_figure=False):
    dive_plan = DivePlan()
    dive_plan.setDefaults()

    dive_plan.bottomTime = T*60
    dive_plan.bottomDepth = D
    
    dive_plan.maxDepth = dive_plan.bottomDepth
    dive_plan.descRate  =        99 / 60.0
    dive_plan.ascRateToDeco =    10 / 60.0
    dive_plan.ascRateAtDeco =    3  / 60.0
    dive_plan.ascRateToSurface = 1  / 60.0
    dive_plan.descTime = dive_plan.bottomDepth / dive_plan.descRate

    dive_plan.GFhigh = gf_high/100
    dive_plan.GFlow = gf_high/100

    # Set gasses for just air
    dive_plan.tankList[TankType.BOTTOM].o2 = o2
    dive_plan.tankList[TankType.BOTTOM].he = he
    dive_plan.tankList[TankType.DECO1].use = False
    dive_plan.tankList[TankType.DECO2].use = False
    dive_plan.tankList[TankType.TRAVEL].use = False

    try:
        model_run = calculatePlan(dive_plan)
    except ValueError:
        return -1

    dive_time = dive_plan.profileSampled[-1].time/60
    tdt_gf = dive_time-T
    
    if plot_figure:
        fig = px.line(
            x=[x.time/60 for x in dive_plan.profileSampled], 
            y=[-x.depth for x in dive_plan.profileSampled], 
        )
        
        fig.update_layout(
        title=f"Dive profile. Gas: {o2}/{he} GF: {dive_plan.GFlow*100:.0f}/{dive_plan.GFhigh*100:.0f}",
            xaxis_title='Time',
            yaxis_title='Depth',
            legend=dict(title='Legend'),
            template='plotly_white'
        )
        fig.show()
        
    return tdt_gf

def fit_gf_to_tdt(T, D, TDT, he=0, o2=21, verbose=False):
    for gf_high in range(100, 5, -1):
        if get_gf_tdt(T, D, gf_high, he, o2) > TDT:
            if verbose:
                print(f"Found {gf_high} for {T} min and {D}m")
            break
    return gf_high


def parallelize_dataframe(df, func):
    num_cores = cpu_count()
    df_split = [df.iloc[i::num_cores] for i in range(num_cores)]
    with Pool(num_cores) as pool:
        df = pd.concat(pool.map(func, df_split))
    return df


def fit_gf_to_tdt_df(df):
    df['gf_high'] = df.apply(lambda row: fit_gf_to_tdt(row['T'], row['D'], row['TDT']), axis=1)
    return df


def second_dive_no_dec_time(first_dive_time, surface_time, D_feet):
    """Determine of the maximum no decompression time for a second dive, based on the PADI dive table."""
    depths = btt.columns[1:].astype(int)
    planned_depth = depths[depths >= D_feet].values[0]
    possible_pressure_groups = btt.loc[btt[planned_depth.astype(str)] >= first_dive_time, 'Pressure group'].values
    if len(possible_pressure_groups) == 0:
        # The first dive to {D_feet} feet for {first_dive_time} minutes is not a no deco dive.
        return 0
    pressure_group = btt.loc[btt[planned_depth.astype(str)] >= first_dive_time, 'Pressure group'].values[0]
    
    next_pressure_group = sfi.loc[sfi[pressure_group] >= surface_time,'Next pressure group'].values[0]

    residual_nitrogen = rnt.loc[rnt['Depth (fsw)'] == planned_depth, next_pressure_group].values[0]
    
    no_deco_time = (btt[planned_depth.astype(str)] - residual_nitrogen).max()
    return no_deco_time

def get_max_ceiling(d_meters, dive_durations, surface_time, gf_high, plot_figure=False):
    """Determine the maximum ceiling for the second dive, based on ZHL-16C model with symmetric gradient factors."""
    first_dive_gf = 115

    dive_plan = DivePlan()
    dive_plan.setDefaults()
    
    dive_plan.bottomTime = 60*dive_durations[0]
    dive_plan.bottomDepth = d_meters
    
    dive_plan.maxDepth = dive_plan.bottomDepth
    dive_plan.descRate  =        99 / 60.0
    dive_plan.ascRateToDeco =    10 / 60.0
    dive_plan.ascRateAtDeco =    3  / 60.0
    dive_plan.ascRateToSurface = 1  / 60.0
    dive_plan.descTime = dive_plan.bottomDepth / dive_plan.descRate
    
    dive_plan.GFhigh = first_dive_gf/100
    dive_plan.GFlow = first_dive_gf/100
    
    # Set gasses for just air
    dive_plan.tankList[TankType.BOTTOM].o2 = 21
    dive_plan.tankList[TankType.BOTTOM].he = 0
    dive_plan.tankList[TankType.DECO1].use = False
    dive_plan.tankList[TankType.DECO2].use = False
    dive_plan.tankList[TankType.TRAVEL].use = False
    
    dive_plan.nDives = len(dive_durations)
    dive_plan.surfaceTime = surface_time
    dive_plan.diveDurations = [60*t for t in dive_durations]
    dive_plan.diveGFs = [first_dive_gf/100, gf_high/100]

    try:
        model_run = calculatePlan(dive_plan)
    except ValueError:
        # This is probably a deco dive because of going over the iteration limit
        return -100
    
    if plot_figure:
        plt.plot([x.time/60 for x in dive_plan.profileSampled], [-x.depth for x in dive_plan.profileSampled])
        plt.title(f"Dive profile. GF: {dive_plan.GFlow*100:.0f}/{dive_plan.GFhigh*100:.0f}")
    
    max_ceiling = max([max(mp.ceilings) for mp in model_run])
    return max_ceiling

def def_find_no_deco_gf_high(d_meters, dive_times, surface_time):
    """Find out the high GF which barely allow doing the second dive without decompression stops."""
    for gf_high in range(120,50,-1):
        max_ceiling = get_max_ceiling(d_meters, dive_times, surface_time, gf_high, plot_figure=False)
        if max_ceiling > 0:
            get_max_ceiling(d_meters, dive_times, surface_time, gf_high, plot_figure=True)
            return gf_high
            
    print("Error: Dive is not possible to do with out deco with gf_high <= 120")
    return -1

def get_gf_to_repetative_dives(df):
    """Process a dataframe with def_find_no_deco_gf_high"""
    df['gf_high'] = df.apply(lambda x: def_find_no_deco_gf_high(x['depth'], [x['first_dive_time'], x['no_deco_time']], x['surface_time']), axis=1)
    return df
