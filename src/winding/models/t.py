import numpy as np
import matplotlib.pyplot as plt

# --- 1. Skapa en testsignal (Om du redan har din data Y och fs, hoppa över detta) ---
fs = 1000  # Samplingsfrekvens (Hz)
t = np.arange(0, 1.0, 1/fs)  # 1 sekund av data
f0 = 50    # Grundton (Hz)

# Vi bygger en signal med grundton + 3:e, 5:e och 7:e överton
Y = (1.0 * np.sin(2 * np.pi * f0 * t) + 
     0.5 * np.sin(2 * np.pi * 3 * f0 * t) + 
     0.3 * np.sin(2 * np.pi * 5 * f0 * t) + 
     0.1 * np.sin(2 * np.pi * 7 * f0 * t))
# ----------------------------------------------------------------------------------

# 2. Kör FFT och beräkna skalerad magnitud
N = len(Y)
Y_fft = np.fft.fft(Y)
magnituder = (2.0 / N) * np.abs(Y_fft)
frekvenser = np.fft.fftfreq(N, d=1/fs)

# 3. Hämta endast den positiva halvan (FFT är symmetrisk)
pos_index = frekvenser >= 0
frekvenser_pos = frekvenser[pos_index]
magnituder_pos = magnituder[pos_index]

# 4. Definiera övertonernas frekvenser för att rita ut linjer i grafen
overtoner = [1, 3, 5, 7]
mål_frekvenser = [n * f0 for n in overtoner]

# 5. Plotta spektrumet
plt.figure(figsize=(10, 5))
plt.plot(frekvenser_pos, magnituder_pos, label='FFT Spektrum', color='b', linewidth=1.5)

# Rita vertikala linjer där övertonerna *borde* ligga för enkel visuell koll
for f in mål_frekvenser:
    plt.axvline(x=f, color='r', linestyle='--', alpha=0.7, label=f'Överton ({f} Hz)' if f == mål_frekvenser[0] else "")

# Zooma in på det intressanta området (upp till strax förbi 7:e övertonen)
plt.xlim(0, max(mål_frekvenser) * 1.3)
plt.title('Amplitudspektrum (Hitta övertoner)')
plt.xlabel('Frekvens (Hz)')
plt.ylabel('Amplitud')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.show()