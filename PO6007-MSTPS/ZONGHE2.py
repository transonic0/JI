# Sat Dec 21 19:09:07 CST 2019
# ZONG HE ZUO YE 2
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import fsolve
import matplotlib as mpl
# Configurations
mpl.rcParams['font.family'] = 'serif'
mpl.rcParams['font.size'] = 14
mpl.rcParams['font.weight'] = 'medium'
mpl.rcParams['font.style'] = 'normal'
mpl.rcParams['font.serif'] = 'DejaVu Serif'
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['mathtext.fallback_to_cm'] = True
mpl.rcParams['lines.linewidth'] = 2
mpl.rcParams['savefig.dpi'] = 300
mpl.rcParams['savefig.bbox'] = 'tight'

# Constants
PATM =  101.3e03       # Pa
CP   =  1004.0         # J/kg K
RG   =  287.0          # J/kg K
K    =  1.4            # -
PCR  =  0.528          # -
P0   =  150000.0       # Pa
P1   =  109074.07373321# Initial Pressure of the Chamber
PO1  =  76300.0
PO2  =  76300.0
PO3  =  76300.0
T0   =  373.0          # K
T1   =  T0             # Initial Temperature of the Chamber
H0   =  T0 * CP        # J/kg
H1   =  T1 * CP        # J/kg
RHO0 =  P0 / (T0 * RG) # kg/m3
RHO1 =  P1 / (T1 * RG) # kg/m3
CVA  =  5.158e-7       # VA
CV1  =  4.1452e-8      # VA1
CV2  =  6.356e-7       # VA2
CV3  =  1.325e-8       # VA3
VCB1 =  0.02           # m3
VCB2 =  0.01           # m3
LV   =  351e3          # J/kg
TINJ =  273.0          # K
HINJ =  CP * TINJ      # J/kg

# initial yst
YST_VA  =  0.9
YST_VA1 =  0.89945679
YST_VA2 =  0.89945301
YST_VA3 =  0.93796938


def func(yst, x):
    VA = Valve(CV3, 0.5)
    VA.setYst(yst)
    return VA.calcVolFlux(RHO1, P1, x) - 0.001e-3


def main():
    # ys = np.arange(0.4,1.01,0.01)
    # ps = []
    # for y in ys:
    #     X = fsolve(func, [100000.0], args=y)
    #     ps.append(X)
    # plt.plot(ys,ps)
    # plt.show()
    # print(fsolve(func, [0.9], args=PO3))

    t, pcbs1 = helper(VCB1, 0.0, 0.0, 0.0, 0)
    t, pcbs2 = helper(VCB1, -0.02, -0.01, -0.002, 1)
    t, pcbs3 = helper(VCB1, 0.02, 0.02, 0.002, 2)
    t, pcbs4 = helper(VCB2, 0.0, 0.0, 0.0, 0)
    t, pcbs5 = helper(VCB2, -0.01, -0.01, -0.001, 1)
    t, pcbs6 = helper(VCB2, 0.01, 0.01, 0.001, 2)


    fig = plt.figure(figsize=(9,5))
    ax = plt.subplot(111)
    ax.plot(t, pcbs1, label='No control, V = 0.02')
    ax.plot(t, pcbs2, label='PID control of VA, V = 0.02')
    ax.plot(t, pcbs3, label='PID control of VA1, V = 0.02')
    ax.plot(t, pcbs4, label='No control, V = 0.01')
    ax.plot(t, pcbs5, label='PID control of VA, V = 0.01')
    ax.plot(t, pcbs6, label='PID control of VA1, V = 0.01')
    ax.legend()
    ax.set_xlim(0.0, 100.0)
    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Pressure (Pa)')
    ax.set_ylim(109050, 109170)
    plt.tight_layout()
    plt.show()

    # fig = plt.figure(figsize=(9,9))
    # ax1 = plt.subplot(411)
    # ax2 = plt.subplot(412)
    # ax3 = plt.subplot(413)
    # ax4 = plt.subplot(414)
    # ax1.plot(t, mvas, label='m_VA', c='k')
    # ax2.plot(t, mv1s, label='m_VA1', c='k')
    # ax3.plot(t, mv2s, label='m_VA2', c='k')
    # ax4.plot(t, mv3s, label='m_VA3', c='k')
    # ax1.legend();ax2.legend();ax3.legend();ax4.legend()
    # ax4.set_xlabel('Time (s)')
    # ax1.set_ylabel(r'$\dot{m} \ (kg/s)$');ax2.set_ylabel(r'$\dot{m} \ (kg/s)$')
    # ax3.set_ylabel(r'$\dot{m} \ (kg/s)$');ax4.set_ylabel(r'$\dot{m} \ (kg/s)$')
    # plt.tight_layout()
    # plt.show()

def helper(Vol, Kp, Ki, Kd, control):
    VA = Valve(CVA, YST_VA)
    VA1 = Valve(CV1, YST_VA1)
    VA2 = Valve(CV2, YST_VA2)
    VA3 = Valve(CV3, YST_VA3)
    cb = Chamber(Vol, P1, T1*CP)
    pidva = PID(Kp, Ki, Kd)
    dt = 0.01
    t = np.arange(0, 100+dt, dt)
    pcbs = []
    pcb = cb.getPressure()
    rhocb = cb.getRho()
    Tcb = cb.getTemperature()
    hcb = cb.getEnthalpy()
    print(cb)
    for i in range(len(t)):
        mva = VA.calcVolFlux(RHO0, P0, pcb)
        mva1 = VA1.calcVolFlux(rhocb, pcb, PO1)
        mva2 = VA2.calcVolFlux(rhocb, pcb, PO2)
        mva3 = VA3.calcVolFlux(rhocb, pcb, PO3)
        cb.updateState(mva, inject(t[i]), mva1, mva2, mva3, H0, HINJ, hcb, dt)

        if control == 0:
            pass
        elif control == 1:
            mtva = pidva.calcOutput(cb.getPressure() - pcb, dt)
            VA.setYst(VA.getYst() + mtva)
        elif control == 2:
            mtva1 = pidva.calcOutput(cb.getPressure() - pcb, dt)
            VA1.setYst(VA1.getYst() + mtva1)
        else:
            print("Error", control)
        pcb = cb.getPressure()
        Tcb = cb.getTemperature()
        rhocb = cb.getRho()
        hcb = cb.getEnthalpy()
        pcbs.append(pcb)
    return (t, pcbs)
 
# Valve module
class Valve:
    def __init__(self, Cv=0.01, Yst=0.5):
        self._Cv = Cv
        self._Yst = Yst

    def __str__(self):
        return ("|VALVE|\n\tCv: " + str(self._Cv) + "\n" +
                "\tYst: " + str(self._Yst))

    def setYst(self, Yst):
        self._Yst = Yst

    def getYst(self):
        return self._Yst

    def calcVolFlux(self, rho1=1.184, p1=PATM, p2=PATM):
        pRatio = p2 / p1
        kRecip = 1.0 / K
        if pRatio > PCR:
            temp = rho1 * p1 * (pRatio**(2.0*kRecip) - pRatio**(1.0+kRecip))
            temp = temp**0.5
            volFlux = self._Yst * self._Cv * temp
        else:
            temp = rho1 * p1 * (PCR**(2.0*kRecip) - PCR**(1.0+kRecip))
            temp = temp**0.5
            volFlux = self._Yst * self._Cv * temp
        return volFlux


# Chamber module
class Chamber:
    def __init__(self, vol=0.25, p=PATM, h=H1):
        self._V = vol
        self._P = p
        self._H = h
        self._T = h / CP
        self._Rho = p / (RG * self._T)

    def __str__(self):
        return ("|CHAMBER|\n\tVolume: " + str(self._V) + "\n" +
                "\tPressure: " + str(self._P) + "\n" +
                "\tEnthalpy: " + str(self._H) + "\n" +
                "\tTemperature: " + str(self._T) + "\n" +
                "\tDensity: " + str(self._Rho))

    def updateState(self, G1, G2, G3, G4, G5, h1, h2, h3, dt):
        # update pressure
        temp = (G1*h1 + G2*h2 - (G3+G4+G5)*h3) / (self._V * (CP/RG - 1.0))
        temp = temp * dt
        self._P = self._P + temp
        # update enthalpy
        temp = G1*h1 + G2*h2 - (G3+G4+G5)*h3 + (1.0 - RG/CP)*(G3+G4+G5-G1-G2)*h3
        temp = temp - G2 * LV
        temp = temp / (self._Rho * self._V * (1.0 - RG/CP))
        temp = temp * dt
        self._H = self._H + temp
        self._T = self._H / CP
        self._Rho = self._P / (RG * self._T)

    def getPressure(self):
        return self._P

    def getRho(self):
        return self._Rho

    def getEnthalpy(self):
        return self._H

    def getTemperature(self):
        return self._T

class PID:
    """docstring for PID"""
    def __init__(self, Kp=0.1, Ki=0.1, Kd=0.01):
        self._Kp = Kp
        self._Ki = Ki
        self._Kd = Kd
        self._err = 0.0
        self._pt1 = 0.0
        self._pt2 = 0.0
        self._pt3 = 0.0

    def calcOutput(self, err=0.0, dt=0.01):
        self._pt1 = self._Kp * err
        self._pt2 = self._pt2 + self._Ki*0.5*(self._err + err)*dt
        self._pt3 = self._Kd * (err - self._err) / dt
        self._err = err
        ret = self._pt1 + self._pt2 + self._pt3
        return ret

def inject(t):
    if t < 20:
        return 0.0
    elif t < 22:
        return 0.0025e-3
    else:
        return 0.0

main()
