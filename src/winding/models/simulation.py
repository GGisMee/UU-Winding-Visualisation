from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

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

    winding_matrix: np.ndarray = None # type: ignore

    def __post_init__(self):
        """Validates pole count and initializes the winding matrix if not provided."""
        assert self.poles % 2 == 0, f"poles must be an even number, got {self.poles}"
        if self.winding_matrix is None:
            if self.poles == 4 and self.slots == 38: # Boot up example
                self.winding_matrix = np.array([
                    [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -2,  3,  3,  4, -2, -2,  1, -4,  1],
                    [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -5,  3,  3,  4, -2, -2,  1, -4,  1],
                    [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3],
                    [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3]
                ])
            else:
                self.winding_matrix = np.zeros((self.poles, self.slots), dtype=int)

    def resize_matrix(self):
        """Resizes winding_matrix to match (poles, slots), padding with zeros or truncating."""
        old_poles, old_slots = self.winding_matrix.shape
        new_matrix = np.zeros((self.poles, self.slots), dtype=int)
        
        copy_poles = min(self.poles, old_poles)
        copy_slots = min(self.slots, old_slots)
        
        new_matrix[:copy_poles, :copy_slots] = self.winding_matrix[:copy_poles, :copy_slots]
        self.winding_matrix = new_matrix

        # Ensure no winding phase is higher than the available phases
        self.winding_matrix[np.abs(self.winding_matrix) > self.phases] = 0

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
    """Current operating state of the generator."""
    RPM: int = 240  # [rpm]
    noise: float = 0.03  # [-] noise parameter


# --- Beräkningar ---

@dataclass
class Generator:
    """
    Represents the full generator assembly and state.
    Provides calculated properties for physical, mechanical, and electrical characteristics.
    """
    geom:Geometry
    wind:Winding
    material: Material
    state:OperatingState

    # -- 1. Geometri & Mekanik --
    @property
    def v_airgap(self) -> float:
        """Calculates the linear velocity in the airgap based on rotor RPM and diameter."""
        return 2 * np.pi * self.geom.inner_diameter * self.state.RPM / 60  # [m/s]

    # -- 2. Spår & Lindningar --
    @property
    def pole_pairs(self) -> int:
        """Returns the number of magnetic pole pairs."""
        return self.wind.poles // 2  # [-]

    @property
    def q(self) -> float:
        """Calculates the number of slots per pole and phase."""
        return self.wind.slots / (self.wind.poles * self.wind.phases)  # [-] 

    @property
    def angle_per_slot(self) -> float:
        """Calculates the electrical angle displacement between adjacent slots."""
        return (self.pole_pairs / self.wind.slots) * 2 * np.pi  # [-]

    @property
    def electric_angles(self) -> np.ndarray:
        """Calculates the electrical angle position for each slot."""
        return (np.arange(1, self.wind.slots + 1) * self.angle_per_slot) % (2 * np.pi)  # [-]

    # -- 3. Elektricitet & Magnetism --
    @property
    def frequency(self) -> float:
        """Calculates the electrical frequency at the current operating RPM."""
        return self.wind.poles * self.state.RPM / 60  # [Hz] Electrical Frequency at operating speed

    @property
    def electrical_angular_velocity(self) -> float:
        """Calculates the electrical angular velocity in radians per second."""
        return (self.state.RPM / 60) * 2 * np.pi * self.pole_pairs  # [s^-1] rad / sec

    @property
    def average_airgap_b_field(self) -> float:
        """Calculates the average magnetic flux density in the airgap."""
        return (self.material.remanence / 0.8) * self.wind.rotor_fill  # [T] Average Airgap Magnetic Flux Density

    @property
    def induced_e_field(self) -> float:
        """Calculates the induced electric field strength in the airgap."""
        return self.average_airgap_b_field * self.v_airgap  # [V/m]

    @property
    def conductor_U(self) -> float:
        """Calculates the induced voltage per conductor."""
        return self.induced_e_field * self.geom.height  # [V]

    @property
    def nominal_max_voltage(self) -> float:
        """Calculates the nominal maximum phase voltage."""
        return self.conductor_U*self.wind.total_winding_positions/self.wind.phases




def get_total_windings_per_phase(phases: int, winding_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculates the number of windings (up + down, up, down) for each phase over all slots.
    Returns a three vector all with shape (phases,)
    """
    phases_arr = np.arange(1, phases + 1)
    
    up_windings = np.sum(winding_matrix.ravel()[:, None] == phases_arr, axis=0)
    down_windings = np.sum(winding_matrix.ravel()[:, None] == -phases_arr, axis=0)
    return up_windings+down_windings, up_windings, down_windings, 

def get_net_windings_per_slot(phases: int, winding_matrix: np.ndarray) -> np.ndarray:
    """
    Calculates the net windings (up - down) for each phase in each slot.
    Returns a matrix of shape (phases, slots).
    """
    phases_arr = np.arange(1, phases + 1)

    # Matrix shape: (poles, slots)
    # We want to count the number of up/down windings per phase for each slot
    nb_up = np.sum(winding_matrix[:, :, None] == phases_arr[None, None, :], axis=0).T
    nb_down = np.sum(winding_matrix[:, :, None] == -phases_arr[None, None, :], axis=0).T

    net_windings = nb_up - nb_down
    return net_windings

def magnet(arg: np.ndarray) -> np.ndarray:
    """Evaluates the magnetic field pattern"""
    return (np.sign(np.sin(arg)) * (np.sin(arg) ** 2) + 0.228 * np.sin(3 * arg)) / 0.7724

def simulate_generator(generator: Generator, time_steps: np.ndarray) -> np.ndarray:
    """
    Simulates the generator voltages over time.
    Returns a 2D array of voltages with shape (phases, len(time_steps)).
    """
    net_windings_per_slot = get_net_windings_per_slot(generator.wind.phases, generator.wind.winding_matrix)
    total_windings_per_phase = get_total_windings_per_phase(generator.wind.phases, generator.wind.winding_matrix)[0]
    
    num_phases = generator.wind.phases
    num_steps = len(time_steps)
    phase_voltages = np.zeros((num_phases, num_steps))
    
    # 1. Calculate relative angles for time steps and slots
    # rotor_electrical_angles has shape (Time,)
    # generator.electric_angles has shape (Slots,)
    rotor_electrical_angles = time_steps * generator.electrical_angular_velocity
    
    # Broadcasting: create a (Time, Slots) matrix of relative angles
    relative_angles = rotor_electrical_angles[:, np.newaxis] + generator.electric_angles[np.newaxis, :]
    
    # 2. Evaluate magnetic field. Output shape: (Time, Slots)
    magnet_field_at_slots = magnet(relative_angles)
    
    # 3. Calculate voltages for each phase
    for phase_idx in range(num_phases):
        net_windings_in_phase = net_windings_per_slot[phase_idx, :]
        windings_in_this_phase = total_windings_per_phase[phase_idx] # Over all slots
        noise_amplitude = windings_in_this_phase * generator.conductor_U * generator.state.noise
        
        # Get volate: (Time, Slots) @ (Slots,) -> (Time,)
        induced_voltage = (magnet_field_at_slots @ net_windings_in_phase) * generator.conductor_U
        
        # Add a vector of strictly positive uniform noise (uncentered)
        noise = np.random.rand(num_steps) * noise_amplitude
        
        phase_voltages[phase_idx, :] = induced_voltage + noise
            
    return phase_voltages

def plot_phase_voltages(time_steps: np.ndarray, phase_voltages: np.ndarray):
    """Plots the simulated voltages."""
    plt.figure(figsize=(10, 6))
    plt.title("Phase Voltages Over Time")
    plt.xlabel("Time [s]")
    plt.ylabel("Voltage [V]")
    
    for phase_idx in range(phase_voltages.shape[0]):
        plt.plot(time_steps, phase_voltages[phase_idx, :], label=f"Phase {phase_idx + 1}")

    # Plot sum
    plt.plot(time_steps, np.sum(phase_voltages, axis=0), "--", label="Sum of phase voltages", color="Black")
        
    plt.legend()
    plt.grid(True)
    plt.show()

def calculate():
    """
    Main execution routine for the generator simulation.
    Sets up the machine parameters, runs the simulation over a defined time period,
    and visualizes the phase voltages.
    """
    # 1. Setup 
    geometry = Geometry()
    winding = Winding()
    state = OperatingState()
    material = Material()
    generator = Generator(geometry, winding, material, state)

    # 2. Simulate
    time_steps = np.linspace(0, 0.2, 100) # [s]
    phase_voltages = simulate_generator(generator, time_steps)

    
    # 3. Visualize
    plot_phase_voltages(time_steps, phase_voltages)

if __name__ == "__main__":
    calculate()