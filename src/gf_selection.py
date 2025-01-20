import os
import sys
import math
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from multiprocessing import Pool, cpu_count

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

def get_standair_tdt(D, T, pdcs):
    D_feet = D * 3.2808399
    logit = math.log(pdcs / (1 - pdcs))
    numerator = b*(D_feet-c)*(1-np.exp(-d * T**f))
    TDT = numerator / (logit - a) + g

    # Negative values correspond to no deco. Set TDT to 0.
    TDT = np.clip(TDT, a_min=0, a_max = np.inf)
    
    return TDT

def standair_plot(D, T_ref, pdcs_ref):    
    T = np.linspace(0,T_ref*2,100)
    ax = plt.gca()
    for pdcs in [0.01, 0.016, 0.02, 0.026, 0.03]:
        TDT = get_standair_tdt(D, T, pdcs)
        
        plt.plot(T,TDT, label=f'pDCS ={pdcs}')
    plt.title(f'StandardAir model for {D:.1f}m')
    
    TDT_ref = get_standair_tdt(D, T_ref, pdcs_ref)
    ax.plot(T_ref, TDT_ref, label="Your plan", marker="o", linewidth=0)
    ax.set_ylim([0, TDT_ref*2])
    plt.legend()

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
        plt.plot([x.time/60 for x in dive_plan.profileSampled], [-x.depth for x in dive_plan.profileSampled])
        plt.title(f"Dive profile. Gas: {o2}/{he} GF: {dive_plan.GFlow*100:.0f}/{dive_plan.GFhigh*100:.0f}")
    
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
    df_split = np.array_split(df, num_cores)
    with Pool(num_cores) as pool:
        df = pd.concat(pool.map(func, df_split))
    return df


def fit_gf_to_tdt_df(df):
    df['gf_high'] = df.apply(lambda row: fit_gf_to_tdt(row['T'], row['D'], row['TDT']), axis=1)
    return df
