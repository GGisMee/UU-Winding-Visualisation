from dataclasses import dataclass
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

import numpy as np


import numpy as np
from dataclasses import dataclass

# --- Databurkar ---

@dataclass
class Geometry:
    """
    Physical Dimensions.

    Attributes
    ----------
    inner_diameter : float
        Inner diameter of the stator [m].
    height : float
        Active height of the machine [m].
    airgap : float
        Clearance between rotor and stator [mm].
    pm_height : float
        Thickness of the permanent magnets in the magnetization direction [mm].
    """
    inner_diameter: float = 0.3
    height: float = 0.5
    airgap: float = 2.0
    pm_height: float = 5.0

@dataclass
class Winding:
    """
    Slots, poles and winding data.

    Attributes
    ----------
    poles : int
        Number of magnetic poles on the rotor [-].
    phases : int
        Number of electrical phases [-].
    slots : int
        Number of slots in the stator core [-].
    stator_fill : float
        Stator factor filled by copper [-].
    rotor_fill : float
        Fraction of rotor filled by permanent magnet [-].
    winding_matrix : np.ndarray of shape (poles, slots)
        Matrix containing the winding layout.
    """
    poles: int = 4
    phases: int = 5
    slots: int = 38
    stator_fill: float = 0.5
    rotor_fill: float = 0.5

    winding_matrix: np.ndarray = None # type: ignore

    def __post_init__(self):
        """
        Validates pole count and initializes the winding matrix if not provided.
        """
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
        """
        Resizes winding_matrix to match (poles, slots), padding with zeros or truncating.
        """
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
        """Sum of all up and down windings [-]."""
        return np.sum(self.winding_matrix != 0) # 0 here is empty

@dataclass
class Material:
    """
    Material data.

    Attributes
    ----------
    remanence : float
        Remanence magnetic flux density (B_r) for the magnet material [T].
    coercivity : float
        Coercivity (H_c), resistance to magnetization [MA/m].
    """
    remanence: float = 1.32
    coercivity: float = 1.04

@dataclass
class OperatingState:
    """
    Current operating state of the generator.

    Attributes
    ----------
    RPM : int
        Mechanical rotational speed of the rotor [rpm].
    noise : float
        Noise parameter for simulations [-].
    """
    RPM: int = 240
    noise: float = 0.02


# --- Beräkningar ---

@dataclass
class Generator:
    """
    Represents the full generator assembly and state.
    Provides calculated properties for physical, mechanical, and electrical characteristics.

    Attributes
    ----------
    geom : Geometry
        The geometric dimensions of the generator.
    wind : Winding
        The winding configuration and layout.
    material : Material
        The material properties of the generator.
    state : OperatingState
        The current operating state.
    """
    geom:Geometry
    wind:Winding
    material: Material
    state:OperatingState

    # -- 1. Geometri & Mekanik --
    @property
    def v_airgap(self) -> float:
        """Linear velocity in the airgap based on rotor RPM and diameter [m/s]."""
        return 2 * np.pi * self.geom.inner_diameter * self.state.RPM / 60

    # -- 2. Spår & Lindningar --
    @property
    def pole_pairs(self) -> int:
        """Number of magnetic pole pairs [-]."""
        return self.wind.poles // 2

    @property
    def q(self) -> float:
        """Number of slots per pole and phase [-]."""
        return self.wind.slots / (self.wind.poles * self.wind.phases)

    @property
    def angle_per_slot(self) -> float:
        """Electrical angle displacement between adjacent slots [rad]."""
        return (self.pole_pairs / self.wind.slots) * 2 * np.pi

    @property
    def electric_angles(self) -> np.ndarray:
        """Electrical angle position for each slot [rad] as a np.ndarray of shape (slots,)."""
        return (np.arange(1, self.wind.slots + 1) * self.angle_per_slot) % (2 * np.pi)

    # -- 3. Elektricitet & Magnetism --
    @property
    def frequency(self) -> float:
        """Electrical frequency at the current operating RPM [Hz]."""
        return self.pole_pairs * self.state.RPM / 60

    @property
    def electrical_angular_velocity(self) -> float:
        """Electrical angular velocity [rad/s]."""
        return (self.state.RPM / 60) * 2 * np.pi * self.pole_pairs

    @property
    def average_airgap_b_field(self) -> float:
        """Average magnetic flux density in the airgap [T]."""
        return (self.material.remanence / 0.8) * self.wind.rotor_fill

    @property
    def induced_e_field(self) -> float:
        """Induced electric field strength in the airgap [V/m]."""
        return self.average_airgap_b_field * self.v_airgap

    @property
    def conductor_U(self) -> float:
        """Induced voltage per conductor [V]."""
        return self.induced_e_field * self.geom.height

    @property
    def nominal_max_voltage(self) -> float:
        """Nominal maximum phase voltage [V]."""
        return self.conductor_U*self.wind.total_winding_positions/self.wind.phases



class SimulateGenerator:
    """A class for creating generating phase voltage graphs."""
    
    @staticmethod
    def get_total_windings_per_phase(phases: int, winding_matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Calculates the number of windings for each phase over all slots.

        Parameters
        ----------
        phases : int
            Number of electrical phases.
        winding_matrix : np.ndarray of shape (poles, slots)
            Winding matrix.

        Returns
        -------
        tuple of np.ndarray
            A tuple containing three np.ndarray of shape (phases,), representing:
            - Total windings (up + down)
            - Up windings
            - Down windings
        """
        phases_arr = np.arange(1, phases + 1)
        
        up_windings = np.sum(winding_matrix.ravel()[:, None] == phases_arr, axis=0)
        down_windings = np.sum(winding_matrix.ravel()[:, None] == -phases_arr, axis=0)
        return up_windings+down_windings, up_windings, down_windings, 
        
    @staticmethod
    def get_net_windings_per_slot(phases: int, winding_matrix: np.ndarray) -> np.ndarray:
        """
        Calculates the net windings (up - down) for each phase in each slot.

        Parameters
        ----------
        phases : int
            Number of electrical phases.
        winding_matrix : np.ndarray of shape (poles, slots)
            Winding matrix.

        Returns
        -------
        np.ndarray of shape (phases, slots)
            A matrix containing net windings.
        """
        phases_arr = np.arange(1, phases + 1)

        # Matrix shape: (poles, slots)
        # We want to count the number of up/down windings per phase for each slot
        nb_up = np.sum(winding_matrix[:, :, None] == phases_arr[None, None, :], axis=0).T
        nb_down = np.sum(winding_matrix[:, :, None] == -phases_arr[None, None, :], axis=0).T

        net_windings = nb_up - nb_down
        return net_windings

    @staticmethod
    def magnet(arg: np.ndarray) -> np.ndarray:
        """
        Evaluates the magnetic field pattern.

        Parameters
        ----------
        arg : np.ndarray of any shape
            Input array of electrical angles [rad].

        Returns
        -------
        np.ndarray of same shape as arg
            Normalized magnetic field profile [-].
        """
        return (np.sign(np.sin(arg)) * (np.sin(arg) ** 2) + 0.228 * np.sin(3 * arg)) / 0.7724

    @staticmethod
    def apply_noise(generator:Generator, phase_voltages: np.ndarray) -> np.ndarray:
        """
        Applies noise to the phase voltages.
        
        Parameters
        ----------
        phase_voltages : np.ndarray of shape (phases, time_steps)
        noise_amplitudes : np.ndarray of shape (phases,)
        """


        total_windings_per_phase = SimulateGenerator.get_total_windings_per_phase(generator.wind.phases, generator.wind.winding_matrix)[0]
        noise_amplitudes = total_windings_per_phase * generator.conductor_U * generator.state.noise
        num_phases, num_steps = phase_voltages.shape


        noise = np.random.normal(0.0, 1.0, (num_phases, num_steps)) * noise_amplitudes[:, np.newaxis]

        return phase_voltages + noise

    @staticmethod
    def simulate(generator: Generator, time_steps: np.ndarray) -> np.ndarray:
        """
        Simulates the generator voltages over time.

        Parameters
        ----------
        generator : Generator
            The configured generator object.
        time_steps : np.ndarray of shape (len(time_steps),)
            Array of simulation time steps [s].

        Returns
        -------
        np.ndarray of shape (phases, len(time_steps))
            A 2D array of phase voltages [V].
        """
        net_windings_per_slot =SimulateGenerator.get_net_windings_per_slot(generator.wind.phases, generator.wind.winding_matrix)
        
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
        magnet_field_at_slots = SimulateGenerator.magnet(relative_angles)
        
        # 3. Calculate voltages for each phase
        for phase_idx in range(num_phases):
            net_windings_in_phase = net_windings_per_slot[phase_idx, :]
            
            # Get volate: (Time, Slots) @ (Slots,) -> (Time,)
            induced_voltage = (magnet_field_at_slots @ net_windings_in_phase) * generator.conductor_U
            
            phase_voltages[phase_idx, :] = induced_voltage
            
        return phase_voltages

    @staticmethod
    def plot_phase_voltages(time_steps: np.ndarray, phase_voltages: np.ndarray):
        """
        Plots the simulated voltages.

        Parameters
        ----------
        time_steps : np.ndarray of shape (len(time_steps),)
            Array of simulation time steps [s].
        phase_voltages : np.ndarray of shape (phases, len(time_steps))
            Array of phase voltages [V].
        """
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


class PostProcess:
    """Processes generator voltage curves and data to get further information about result."""
    
    @staticmethod
    def overtones(dt:float,fundamental_frequency:float, phase_voltages:np.ndarray):
        """
        Calculates and plots the FFT spectrum to find overtones.

        Parameters
        ----------
        dt : float
            Time step between samples [s].
        fundamental_frequency : float
            The fundamental electrical frequency of the signal [Hz].
        phase_voltages : np.ndarray of shape (phases, len(time_steps))
            Array of phase voltages [V].
        """
        N = phase_voltages.shape[-1] # number of datapoints
        voltage_fft = np.fft.rfft(phase_voltages)
        frequencies = np.fft.rfftfreq(N, d=dt)


        magnitudes = np.abs(voltage_fft)/N
        magnitudes[...,1:] *= 2 # den på 0 är dubbelskalas i början

        # 4. Definiera övertonernas frekvenser för att rita ut linjer i grafen
        goal_frequencies = np.arange(1,8,2)*fundamental_frequency
        goal_idx = [np.argmin(np.abs(frequencies-goal_frequency)) for goal_frequency in goal_frequencies]

        overtone_magnitudes = magnitudes[:, goal_idx]
        print("Frekvenser: ", frequencies[goal_idx])
        print("Magnitudes per phase:\n", overtone_magnitudes)

        PostProcess.plot_spectrum(frequencies, magnitudes, goal_frequencies, phases=phase_voltages.shape[0])

        return overtone_magnitudes


    @staticmethod
    def plot_spectrum(frequencies:np.ndarray, magnitudes:np.ndarray, goal_frequencies:np.ndarray, phases:int):
        # 5. Plotta spektrumet
        plt.figure(figsize=(10, 5))
        for phase_idx in range(phases):
            plt.plot(frequencies, magnitudes[phase_idx, :], label=f'spectrum phase {phase_idx+1}', linewidth=1.5)

        # Rita vertikala linjer där övertonerna *borde* ligga för enkel visuell koll
        for f in goal_frequencies:
            plt.axvline(x=f, color='r', linestyle='--', alpha=0.7, label=f'Överton ({f} Hz)' if f == goal_frequencies[0] else "")

        # Zooma in på det intressanta området (upp till strax förbi 7:e övertonen)
        plt.xlim(0, max(goal_frequencies) * 1.3)
        plt.title('Amplitudspektrum (Hitta övertoner)')
        plt.xlabel('Frekvens (Hz)')
        plt.ylabel('Amplitud')
        plt.grid(True, linestyle=':', alpha=0.6)
        plt.legend()
        plt.show()


def create_steps(frequency:float, nb_periods: int, points_per_period: int) -> tuple[float, np.ndarray]:
    """Returns step distance and steps array"""
    N = nb_periods*points_per_period
    period = 1/frequency
    time_steps = np.linspace(0, nb_periods*period, N, endpoint=False) # [s]
    dt = time_steps[1] - time_steps[0]
    return dt, time_steps

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
    dt, time_steps = create_steps(frequency=generator.frequency, nb_periods=1,points_per_period=64)

    phase_voltages = SimulateGenerator.simulate(generator, time_steps)
    noised_phase_voltages = SimulateGenerator.apply_noise(generator, phase_voltages)

    
    # 3. Visualize
    SimulateGenerator.plot_phase_voltages(time_steps, noised_phase_voltages)

    PostProcess.overtones(dt, generator.frequency, phase_voltages)

if __name__ == "__main__":
    calculate()