import matplotlib.pyplot as plt
import numpy as np

epsilon = 0.95
sigma = 5.67e-8
Tinf, Tsur = 283, 283
q = 100 
A = 1.8
def hr(Ts):
    return epsilon*sigma*(Ts+Tsur)*(Ts**2+Tsur**2)

def solve(h):
    T = np.linspace(273, 300, 100)
    f1 = T*(h + hr(T))
    f2 = q/A + h*Tinf + hr(T)*Tsur
    plt.plot(T-273, f1, 'r')
    plt.plot(T-273, f2 , 'b')
    plt.title(f'h={h}')
    plt.ylabel('$W m^{-2}$')
    plt.xlabel('$T$ (°C)')
    plt.grid()
    plt.show()
    i_min = np.argmin(np.abs(f1 - f2))
    Ts = T[i_min]-273
    print(f'T= {Ts:.2f} °C')
        
h = 2
solve(h)

