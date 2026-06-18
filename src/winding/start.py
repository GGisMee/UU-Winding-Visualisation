from dataclasses import dataclass
import matplotlib.pyplot as plt

import numpy as np


import numpy as np
from dataclasses import dataclass

# --- Databurkar ---

@dataclass
class Geometry:
    """Physical Dimensions"""
    inner_diameter: float = 0.3  # [m]
    height: float = 0.5  # [m]
    airgap: float = 2.0  # [mm] clearance between rotor and stator
    pm_height: float = 5.0  # [mm] thickness in the magnetization direction

@dataclass
class Winding:
    """Slots, poles and winding data"""
    poles: int = 4  # [-] nb (number of magnetic poles on rotor)
    phases: int = 5  # [-] nb of electrical fases
    slots: int = 38  # [-] nb of slots in stators core
    stator_fill: float = 0.5  # [-] stator factor filled by copper
    rotor_fill: float = 0.5  # [-] fraction of rotor filled by permanent magnet

    # winding_matrix:np.ndarray = np.zeros(shape=(poles, slots)) # Matrix to encode the windings
    # ex nedan
    winding_matrix= np.array([
        [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -2,  3,  3,  4, -2, -2,  1, -4,  1],
        [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -5,  3,  3,  4, -2, -2,  1, -4,  1],
        [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3],
        [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3]
    ])

    def __post_init__(self):
        assert self.poles % 2 == 0, f"poles must be an even number, got {self.poles}"

    @property
    def total_winding_positions(self):
        """Sum of all up and down windings"""
        return np.sum(self.winding_matrix != 0) # 0 here is empty

@dataclass
class Material:
    """Material data"""
    remanence: float = 1.32  # [T] B_r for N45S neodymium magnet material
    coercivity: float = 1.04  # [MA/m] H_c (Resistance to magnetation)

@dataclass
class OperatingState:
    """Aktuellt driftläge."""
    RPM: int = 240  # [rpm]
    noise: float = 0.03  # [-] noise parameter


# --- Beräkningar ---

@dataclass
class Generator:
    geom:Geometry
    wind:Winding
    material: Material
    state:OperatingState

    # -- 1. Geometri & Mekanik --
    @property
    def v_airgap(self) -> float:
        return 2 * np.pi * self.geom.inner_diameter * self.state.RPM / 60  # [m/s]

    # -- 2. Spår & Lindningar --
    @property
    def pole_pairs(self) -> int:
        return self.wind.poles // 2  # [-]

    @property
    def q(self) -> float:
        return self.wind.slots / (self.wind.poles * self.wind.phases)  # [-] 

    @property
    def angle_per_slot(self) -> float:
        return (self.pole_pairs / self.wind.slots) * 2 * np.pi  # [-]

    @property
    def electric_angles(self) -> np.ndarray:
        return (np.arange(1, self.wind.slots + 1) * self.angle_per_slot) % (2 * np.pi)  # [-]

    # -- 3. Elektricitet & Magnetism --
    @property
    def frequency(self) -> float:
        return self.wind.poles * self.state.RPM / 60  # [Hz] Electrical Frequency at operating speed

    @property
    def electrical_angular_velocity(self) -> float:
        return (self.state.RPM / 60) * 2 * np.pi * self.pole_pairs  # [s^-1] rad / sec

    @property
    def average_airgap_b_field(self) -> float:
        return (self.material.remanence / 0.8) * self.wind.rotor_fill  # [T] Average Airgap Magnetic Flux Density

    @property
    def induced_e_field(self) -> float:
        return self.average_airgap_b_field * self.v_airgap  # [V/m]

    @property
    def conductor_U(self) -> float:
        return self.induced_e_field * self.geom.height  # [V]

    @property
    def nominal_max_voltage(self) -> float:
        return self.conductor_U*self.wind.total_winding_positions/self.wind.phases




def count_windings_per_phase(phases:int, winding_matrix:np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates number of up and down windings for each phase.

    Parameters
    ----------
    phases : int
        Number of phases.
    winding_matrix : np.ndarray
        Matrix of windings encoded with + for up, - for down.
        1 or -1 means it belongs to phase 1.

    Returns
    -------
    up_windings : np.ndarray
        Number of up-windings for each phase. Index 0 is phase 1.
    down_windings : np.ndarray
        Number of down-windings for each phase. Index 0 is phase 1.
    """
    phases_arr= np.arange(1,phases+1) # [1,...,phases]
    
    up_windings= np.sum(winding_matrix.ravel()[:, None] == phases_arr, axis=0)
    down_windings = np.sum(winding_matrix.ravel()[:, None] == -phases_arr, axis=0)
    up_down_windings = up_windings+down_windings
    return up_windings, down_windings,up_down_windings

def count_phases_for_slots(poles: float, winding_matrix:np.ndarray):
    poles_arr = np.arange(1, poles+1) # vector, [1,..., poles]

    # Matrix shape: (poles, slots)
    # each row shows number of windings for corresponding phase in each slot
    nb_in_slot_of_phase_up = (np.sum(winding_matrix[:,:,None] == poles_arr[None,None,:], axis = 0).T)
    nb_in_slot_of_phase_down = (np.sum(winding_matrix[:,:,None] == -poles_arr[None,None,:], axis = 0).T)

    phase_count_for_slots = nb_in_slot_of_phase_up-nb_in_slot_of_phase_down
    return phase_count_for_slots

def magnet(arg):
    # np.sign är ekvivalent med VBA:s Sgn()
    return (np.sign(np.sin(arg)) * (np.sin(arg) ** 2) + 0.228 * np.sin(3 * arg)) / 0.7724

def phases_at_angles(generator:Generator, phase_count_for_slots:np.ndarray):
    N = 100
    Ts = np.linspace(0,0.2, 100) # [s] Timestamps
    beta_T = Ts*generator.electrical_angular_velocity # [-]
    windings_per_phase = count_windings_per_phase(generator.wind.phases, generator.wind.winding_matrix)[-1]
    noise_offset = windings_per_phase*generator.conductor_U*generator.state.noise
    # Z5 = U_pos
    # BB15 = angles
    # BC13 = fas brusad
    phase_curve = np.zeros(N)
    for i,beta in enumerate(beta_T):
        magnet_results = magnet(beta+generator.electric_angles)
        print(generator.conductor_U)
        print(beta, phase_count_for_slots)
        phase_curve[i] = magnet_results@phase_count_for_slots*generator.conductor_U+ (np.random.rand() * noise_offset[0])
    plt.plot(Ts, phase_curve)





def calculate():
    geometry = Geometry()
    winding = Winding()
    state = OperatingState()
    material = Material()
    generator = Generator(geometry, winding,material, state)
    poles = winding.poles
    slots = winding.slots

    phase_count_for_slots = count_phases_for_slots(poles,winding.winding_matrix)
    #! phase_count_for_slots should have 5 phases
    for i in np.arange(generator.wind.phases):
        phases_at_angles(generator, phase_count_for_slots[i,:])
    
    plt.show()

calculate()