# -*- coding: utf-8 -*-
"""
Created on Tue Sep 29 10:02:36 2026

@author: justin bal
"""
import numpy as np
import scipy as sp
import matplotlib.pyplot as mpl

def numaric_work(t_vec, a_top_vec, a_bottom_vec, m=1, g=9.81, v0=0):
    v_top_vec = sp.integrate.cumulative_trapezoid((a_top_vec), t_vec, initial = 0)
    v_bottom_vec = sp.integrate.cumulative_trapezoid((a_bottom_vec), t_vec, initial = 0)
    work_vec = [0]
    work_top_vec = [0]
    work_bottom_vec = [0]
    for i in range(len(t_vec)-1):
        dx_top = (t_vec[i+1] - t_vec[i])*( (1/2)*(v_top_vec[i+1]+v_top_vec[i]) + v0)
        dx_bottom = (t_vec[i+1] - t_vec[i])*( (1/2)*(v_bottom_vec[i+1]+v_bottom_vec[i]) + v0)
        
        work = work_vec[i] + m*(g + a_top_vec[i+1])*(dx_top - dx_bottom)
        work_vec.append(work)
        
        work_top = work_top_vec[i] + m*(g + a_top_vec[i+1])*(dx_top)
        work_top_vec.append(work_top)
        
        work_bottom = work_bottom_vec[i] + m*(g + a_top_vec[i+1])*(-dx_bottom)
        work_bottom_vec.append(work_bottom)
        
    return np.array(work_vec), np.array(work_top_vec), np.array(work_bottom_vec)


data = np.loadtxt('corny7_waveforms_50kHz.csv', delimiter="," , skiprows=1)
data1 = data[data[:, 0] == 2]
time = data1[:,1]*1E-3
top1_x = data1[:,2]*9.81
top1_y = data1[:,3]*9.81
top1_z = data1[:,4]*9.81
bottom1_z = data1[:,5]*9.81


work_z, work_z_top, work_z_bottom = numaric_work(time, top1_x, bottom1_z)
mpl.plot(time, work_z, label = 'total')
mpl.plot(time, work_z_top,"--", label = 'top work')
mpl.plot(time, work_z_bottom,"--", label = 'bottom work')
mpl.xlabel("time [s]")
mpl.ylabel("work [j/kg]")
mpl.grid()
mpl.legend()

print(f"{work_z[-1]} jouls per kilogam")