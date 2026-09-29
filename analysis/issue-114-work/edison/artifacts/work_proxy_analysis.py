#!/usr/bin/env python3
"""Impact-work *proxy*, not a calibrated dissipation measurement. Inputs in /workspace."""
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt
from scipy.integrate import cumulative_trapezoid, trapezoid
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
G=9.80665; FS=50000
DATA=Path('/workspace')
OUT=DATA/'work_review'; OUT.mkdir(exist_ok=True)
w=pd.read_csv(DATA/'corny7_waveforms_50kHz.csv')
drops=pd.read_csv(DATA/'corny7_drops.csv').set_index('drop_number')
series={k:z.reset_index(drop=True) for k,z in w.groupby('drop_number')}
def calc(k,end_ms=15,fc=300,tail=(70,100),v0=0,gravity=True,clamp_end=False):
    z=series[k]; t=z.time_ms.to_numpy()/1000
    sl=(t>=0)&(t<=end_ms/1000+1.e-10); t1=t[sl]
    a=[]
    for channel in ['ch4_g','ch5_g']:
        x=z[channel].to_numpy()
        base=np.median(x[(z.time_ms>=tail[0])&(z.time_ms<tail[1])])
        x=(x-base)*G
        if fc: x=sosfiltfilt(butter(2,fc,fs=FS,output='sos'),x)
        a.append(x[sl])
    atop,abottom=a
    relv=cumulative_trapezoid(atop-abottom,t1,initial=0)+v0
    if clamp_end: relv-=np.linspace(0,relv[-1],len(relv))
    relative=cumulative_trapezoid(relv,t1,initial=0)
    force=atop+(G if gravity else 0)  # N per kg assumed effective top mass; NOT calibrated force
    work=trapezoid(force*relv,t1)
    return dict(t=t1,atop=atop,abottom=abottom,v=relv,L=relative,F=force,
                work=work,displacement_mm=relative[-1]*1000,
                compression_max_mm=-np.min(relative)*1000,vrel_end=relv[-1])
results=[]
for k in range(3,21):
    r=calc(k);rr=calc(k,end_ms=30)
    sens=[]
    # Deliberate ANALYSIS sensitivity envelope; not a statistical CI or all physical errors.
    for fc in (300,1650):
        for tail in ((60,90),(70,100),(80,100)):
            for end_ms in (10,15,30):
                for v0 in (-.1,0,.1):
                    for gravity in (False,True):
                        sens.append(-calc(k,end_ms,fc,tail,v0,gravity)['work'])
    result={'drop_number':k,'T180':drops.loc[k,'T180'],
            'input_delta_v_m_s':drops.loc[k,'input_delta_v_m_s'],
            'apparent_loss_J_per_kg_15ms':-r['work'],
            'sensitivity_min_J_per_kg':min(sens),'sensitivity_max_J_per_kg':max(sens),
            'work_signed_J_per_kg_15ms':r['work'],
            'apparent_loss_J_per_kg_30ms':-rr['work'],
            'compression_15ms_mm':r['compression_max_mm'],
            'relative_v_15ms_m_s':r['vrel_end'],
            'relative_v_30ms_m_s':rr['vrel_end'],
            'effective_top_mass_kg':np.nan,
            'specimen_mass_kg':.01962,
            'specimen_share_example_1over3_J':-r['work']*.01962/3,
            'specimen_share_example_1_J':-r['work']*.01962,
            }
    results.append(result)
rdf=pd.DataFrame(results);rdf.to_csv(OUT/'drop_03_20_work_proxy.csv',index=False,float_format='%.8g')
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'savefig.dpi':320,'axes.labelsize':10})
# Data series trajectory including recovery, avoiding next collision at ~42-45 ms.
k=10;r=calc(k,end_ms=40)
fig,ax=plt.subplots(figsize=(6.1,4.3),layout='constrained')
C=-r['L']*1000
turn=np.argmin(r['L'])
ax.plot(C[:turn+1],r['F'][:turn+1],color='#295a7c',lw=1.7,label='Compression, 0–25 ms')
ax.plot(C[turn:],r['F'][turn:],color='#b55831',lw=1.5,label='Partial recovery, 25–40 ms')
ax.scatter([C[turn]],[r['F'][turn]],s=24,color='#263e47',zorder=3)
ax.legend(frameon=False,loc='upper right',fontsize=8)
ax.axhline(0,c='#666666',lw=.6)
ax.set(xlabel='Relative compression, −(x_top − x_base) (mm)',ylabel='Inferred axial force / assumed top mass (N kg⁻¹)',
       title='Drop 10: inferred force–deflection trajectory')
ax.text(.33,.82,'Open path: no calibrated hysteresis area',transform=ax.transAxes,va='top',fontsize=8,
        bbox=dict(facecolor='white',alpha=.85,edgecolor='none'))
fig.savefig(OUT/'drop10_force_deflection.png');fig.savefig(OUT/'drop10_force_deflection.pdf');plt.close(fig)
fig,axes=plt.subplots(2,1,figsize=(6.3,5.9),sharex=True,layout='constrained')
rr=calc(10,end_ms=99.98)
axes[0].plot(rr['t']*1000,rr['L']*1000,c='#295a7c',label='CH4−CH5, zeroed, 300 Hz')
axes[0].axhline(-67.12,c='#ae493c',lw=1,ls=':',label='specimen initial height (scale)')
axes[0].set(ylabel='Relative displacement (mm)',title='Drop 10: integration across both impacts');axes[0].legend(loc='lower left',fontsize=8)
axes[1].plot(rr['t']*1000,rr['v'],c='#295a7c');axes[1].axhline(0,c='0.3',lw=.8)
axes[1].set(xlabel='Time in recorded waveform (ms)',ylabel='Relative velocity (m s⁻¹)')
for ax in axes: ax.axvline(15,c='#b55831',ls='--',lw=.9)
fig.savefig(OUT/'drop10_velocity_displacement.png');fig.savefig(OUT/'drop10_velocity_displacement.pdf');plt.close(fig)
fig,ax=plt.subplots(figsize=(7.0,3.8),layout='constrained')
ax.vlines(rdf.drop_number,rdf.sensitivity_min_J_per_kg,rdf.sensitivity_max_J_per_kg,color='#999999',lw=2,label='analysis sensitivity envelope')
ax.scatter(rdf.drop_number,rdf.apparent_loss_J_per_kg_15ms,c='#295a7c',s=24,zorder=3,label='15 ms primary-impact proxy')
ax.set(xlabel='Drop number (warm-up drops 1–2 excluded)',ylabel='Apparent loss / assumed effective mass (J kg⁻¹)',
       xticks=list(range(3,21,2)),title='Corny7: proxy work is not measured absorbed energy')
ax.legend(frameon=False,fontsize=8)
fig.savefig(OUT/'drop_work_sensitivity.png');fig.savefig(OUT/'drop_work_sensitivity.pdf');plt.close(fig)
print(rdf.to_string(index=False,float_format=lambda x:f'{x:.4f}'))
print('median',rdf.apparent_loss_J_per_kg_15ms.median(),'range',rdf.apparent_loss_J_per_kg_15ms.min(),rdf.apparent_loss_J_per_kg_15ms.max(),
      'sensitivity all',rdf.sensitivity_min_J_per_kg.min(),rdf.sensitivity_max_J_per_kg.max())
