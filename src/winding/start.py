import numpy as np

# Givet
poles = 4 # [-] nb (number of magnetic poles on rotor)
phases = 5 # [-] nb of electrical fases
RPM = 240 # [rpm]
slots = 38 # [-] nb of slots in stators core 


inner_diameter = 0.3 # [m] 
height = 0.5 # [m]
stator_fill = 0.5 # [-] stator factor filled by copper
airgap = 2 # [mm] clearance between rotor and stator
permanent_magnet_height = 5 # [mm] thickness in the magnetization direction
rotor_fill = 0.5 # [-] fraction of rotor filled by permanent magnet

Frequency = poles*RPM/60 # [Hz] Electrical Frequency at operating speed
remanence = 1.32 # [T] B_r for N45S neodymium magnet material
coercity = 1.04 # [MA/m] H_c (Resistance to magnetation)

# Derived
average_airgap_b_field = remanence/0.8*rotor_fill # [T] Average Airgap Magnetic Flux Density

# Brus i datan
noise = 0.03 # [-] noise parameter

# More derived
electrical_angular_velocity = RPM/60*2*np.pi*poles/2 # [s^-1] rad / sec
pole_pairs = poles/2 # [-]
q = slots/(poles*phases) # [-]  

angle_per_slot = (pole_pairs / slots) * 2 * np.pi # [-]
electric_angles = (np.arange(1,slots+1)*angle_per_slot)%(2*np.pi) # [-]

v_airgap = 2*np.pi*inner_diameter*RPM/60 # [m/s]
induced_e_field = average_airgap_b_field*v_airgap# [V/m]
conductor_U =induced_e_field*height # [V]


winding_matrix = np.zeros(shape=(poles, slots)) # Matrix to encode the windings
# ex nedan
winding_matrix= np.array([
    [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -2,  3,  3,  4, -2, -2,  1, -4,  1],
    [ 1,  1,  1, -3, -3,  2,  2,  2, -1, -1,  3,  3,  3, -2, -2,  1,  1,  1, -3, -3,  5,  5,  2, -1, -1,  3,  3,  3, -5, -5,  3,  3,  4, -2, -2,  1, -4,  1],
    [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3],
    [ 1,  1, -3, -3, -3,  2,  2, -1, -1, -1,  3,  3, -2, -2, -2,  1,  1, -3, -3, -3,  5,  5, -1, -1, -1,  3,  3, -2, -5, -5,  3,  3,  4, -2, -2,  1, -4, -3]
])


Ts = np.arange(0,0.2, 0.002) # [s] Timestamps
angles = Ts*electrical_angular_velocity # [-]
def count_phases_for_slots(poles: float, winding_matrix:np.ndarray):
    poles_arr = np.arange(1, poles+1) # vector, [1,..., poles]

    # Matrix shape: (poles, slots)
    # each row shows number of windings for corresponding phase in each slot
    nb_in_slot_of_phase_up = (np.sum(winding_matrix[:,:,None] == poles_arr[None,None,:], axis = 0).T)
    nb_in_slot_of_phase_down = (np.sum(winding_matrix[:,:,None] == -poles_arr[None,None,:], axis = 0).T)

    phase_count_for_slots = nb_in_slot_of_phase_up-nb_in_slot_of_phase_down
    return phase_count_for_slots


count_phases_for_slots(poles,winding_matrix)

def nb_windings_per_phase(phases:int, winding_matrix:np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, int]:
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
    total = np.sum((up_windings+down_windings))
    return up_windings, down_windings,up_down_windings, total