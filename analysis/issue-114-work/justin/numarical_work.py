# -*- coding: utf-8 -*-
"""
Created on Sun Sep 27 10:07:07 2026

@author: justin bal
"""
import numpy as np
import matplotlib.pyplot as mpl
import scipy as sp

def test_fun(x):
    return -x**5 + 9*x**4 - 15*x**3 - 6*x**2 + 7*x + 1


def true_solution(x):
    return 0.81147276783173 + 5.405*x**2 + 14.945*x**3 - 0.78*x**4 - 18.1074999999999*x**5 - 6.382*x**6 + 13.3997619047619*x**7 + 2.84791666666666*x**8 - 6.41666666666666*x**9 + 2.245*x**10 - 0.3*x**11 + 0.0138888888888888*x**12

def test_fun2(x):
    return -3*x**3 + 2*x**2 + 2*x - 1

def true_solution2(x):
    return 2.330451557823571 - 4.405*x**2 + 2.27*x**3 + 1.4683333333333333*x**4 - 0.05483333333333338*x**5 - 0.5277777777777777*x**6 - 0.5*x**7 + 0.28125*x**8

def numaric_work(t_vec, a, m=1, g=9.81, u=0, v=0):
    v_vec = sp.integrate.cumulative_trapezoid(a(t_vec), t_vec, initial = 0)
    dx_vec = [0]
    work_vec = [0]
    for i in range(len(t_vec)-1):

        dx = (1/2)*(t_vec[i+1]-t_vec[i])*(v_vec[i+1]+v_vec[i])
        dx_vec.append(dx)
        
    for i in range(len(t_vec)-1):
        error = u*a(t_vec[i+1]) + v
        work = work_vec[i] + m*(g + a(t_vec[i+1]))*dx_vec[i+1] + error
        work_vec.append(work)
        
    return np.array(work_vec)

def get_err_fun(true_vec, num_vec, a, t_vec):
    """err(t) = u*a(t) + v
       d_err(t) / d_a(t) = u
       err(t) - u*a(t) = v"""
    a_vec = a(t_vec)
    d_true_d_num = np.append(np.array([0]), np.diff(true_vec - num_vec))
    u_vec =  np.diff(d_true_d_num) / np.diff(a_vec)
    u = np.mean(u_vec[1:])
    v_vec = d_true_d_num - u*a_vec
    v = np.mean(v_vec[1:])
    
    mpl.plot(t_vec, d_true_d_num, label = "d_true - d_num")
    mpl.legend()
    mpl.twinx()
    mpl.plot(t_vec, a_vec, "r--", label = "a(t)")
    mpl.legend()
    mpl.show()
    
    return u, v
    

t_vec = np.arange(-0.66543, 2.49149, 8*10**-6)
true_vec = true_solution(t_vec)
num_vec = numaric_work(t_vec, test_fun)

u_par, v_par = get_err_fun(true_vec, num_vec, test_fun, t_vec)

adj_num_vec = numaric_work(t_vec, test_fun, u = u_par, v = v_par)
print(u_par, v_par)

mpl.plot(t_vec, num_vec, label = "num")
mpl.plot(t_vec, adj_num_vec, label = "adj_num")
mpl.plot(t_vec, true_vec, "--", label = "true")
mpl.legend()
mpl.ylabel("work [J]")
# mpl.twinx()
# mpl.plot(t_vec[10000:], abs(100*(true_vec-adj_num_vec)/true_vec)[10000:], "r", label = "adj %err")
# mpl.legend()
# mpl.ylabel("error %")
mpl.xlabel("time [s]")
