from cmath import pi
from multiprocessing import Process, Queue
from data_intake import data_sender
from Saver import data_saver
from EMonitor import run as emonitor_run
from GUI import launchGUI as gui_run
from dataclasses import dataclass, field
from typing import List
from collections import deque
from plotter import animation_control
from threading import Timer
import numpy as np
from numpy import *
import math


@dataclass
class MainExperiment:
    # Experimental state and control
    experiment_mode: str = "DEFAULT"
    mode_state: str = "SHOULDER ELBOW"
    trial_state: str = "Prepare" 
    state_section: str = "AUTO"
    paused: bool = False

    # Experimental variables for controlling the output
    target_EL_tor: float = 1.0
    low_lim_EL_tor: float = 0.8
    up_lim_EL_tor: float = 1.2
    match_EL_tor: float = 1.0

    target_SH_tor: float = 1.0
    low_lim_SH_tor: float = 0.8
    up_lim_SH_tor: float = 1.2
    match_SH_tor: float = 1.0

    max_torque: float = 1.0

    EMG_1: float = 1.0
    EMG_2: float = 1.0
    EMG_3: float = 1.0
    EMG_4: float = 1.0
    EMG_5: float = 1.0
    EMG_6: float = 1.0
    EMG_7: float = 1.0
    EMG_8: float = 1.0

    Fx: float = 1.0
    Fy: float = 1.0
    Fz: float = 1.0
    Mx: float = 1.0
    My: float = 1.0
    Mz: float = 1.0


    timestep: float = 0

    current_trial: str = "Prepare"
    current_status: str = "Prepare"
    task: str = "Prepare"

    # Info about the participants
    subject_number: float = 0
    participant_age: float = 0
    participant_gender: str = "UNSPECIFIED"
    participant_years_since_stroke: int = 0
    participant_dominant_arm: str = "RIGHT"
    participant_paretic_arm: str = "NONE"
    participant_diabetes: str = "NO"
    
    shoulder_aduction_angle: float = 0
    elbow_flexion_angle: float = 0
    arm_length: float = 0
    midloadcell_to_elbowjoint: float = 0

    subject_type: str = "UNSPECIFIED"


    trial_toggle: str = "Testing"
    testing_arm: str = "Default"

    cache_tor: List[float] = field(default_factory=list)
    cacheF: List[float] = field(default_factory=list)

    mvt_tor: float = 0.0
    mvt_f: float = 0.0

    tare_tor: float = 0.0
    tare_f: float = 0.0

    max_flex_tor: float = 0.0
    max_exten_tor: float = 0.0
    maxF: float = 0.0

    prev_time: float = 0.0

    sound_trigger: List[str] = field(default_factory=str)

    stop_trigger: bool = False

    def __post_init__(self):
        if not self.sound_trigger:
            self.sound_trigger = []

        if not self.cache_tor:
            self.cache_tor = list()

        if not self.cacheF:
            self.cacheF = list()

# Jacobian calculate
def Px(r):
    P = [[0, -r[2], r[1]],
        [r[2],0, -r[0]],
        [-r[1], r[0], 0]]
    return P

def rotx(th):
    Rx = np.zeros([3,3])
    Rx[0][0] = 1
    Rx[1][1] = cos(th)
    Rx[1][2] = -sin(th)
    Rx[2][1] = sin(th)
    Rx[2][2] = cos(th)

    return Rx

def roty(th):
    Ry = np.zeros([3,3])
    Ry[0][0] = cos(th)
    Ry[0][2] = sin(th)
    Ry[1][1] = 1
    Ry[2][0] = -sin(th)
    Ry[2][2] = cos(th)

    return Ry

def rotz(th):
    Rz = np.zeros([3,3])
    Rz[0][0] = cos(th)
    Rz[0][1] = -sin(th)
    Rz[1][0] = sin(th)
    Rz[1][1] = cos(th)
    Rz[2][2] = 1

    return Rz
    
def Jac_convert(FMraw, abd_angle, elb_angle, arm_length, z_offset, arm):
    # Inputs:
    #   FMjr: [nsamp x 6] matrix with the raw forces and torques
    #   abd_angle: arm abduction angle in degrees.
    #   elb_angle: elbow flexion angle in degrees (from full flexion).
    #   arm_length: distance from elbow center of rotation to humerus center of rotation
    #   z_offset: distance from middle of load cell to pro-supination axis of the forearm
    #   arm: 1 - 'right' or 0 - 'left'
    #   JR3mat: JR3 calibration matrix
    #   JR3toPlate: 1 - JR3 is rotated 90 deg 0 - JR3 is aligned with plate
    if arm == "Right":
        arm = 1
    else:
        arm = 0

    # change angles from degrees to radians
    abd_angle = math.radians(float(abd_angle))
    elb_angle = math.radians(float(elb_angle))

    JR3mat = [[1,1,1,1,1,1],
              [1,1,1,1,1,1],
              [1,1,1,1,1,1],
              [1,1,1,1,1,1],
              [1,1,1,1,1,1],
              [1,1,1,1,1,1]]

    FMjr = FMraw*JR3mat

    # convert to N and Nm
    Lb_N = 1
    Lbin_Nm = 1

    for i in range(3):
        FMjr[i][0] = float(FMjr[i][0])*Lb_N

    for i in range(3,6):
        FMjr[i][0] = float(FMjr[i][0])*Lbin_Nm

    # Convert to right hand coordinate system
    for i in range(6):
        FMjr[2][i] = -FMjr[2][i]
        FMjr[5][i] = -FMjr[5][i]
        
    # check if 90 deg rotation needed
    if arm == 1:
        JR3toPlate = 1
    else:
        JR3toPlate = 0

    # Calculate the Jacobian to translate the forces from the center of the JR3 to the middle
    # of the epicondyles by distance z_offset. Rotate 90 deg about z axis to account for load cell
    # rotation with respect to the plate, otherwise don't rotate (R=I).
    if JR3toPlate:
        R_1 = rotz(pi/2)
    else:
        R_1 = rotz(-pi/2)
    P_1 = np.dot(Px([0, 0, -float(z_offset)]),R_1)
    Jjtoe = np.append(np.append(R_1,P_1,axis=1),np.append(zeros([3,3]),R_1,axis=1),axis=0)
    FMjr = np.dot(np.transpose(Jjtoe), FMjr)

    # Calculate the jacobian from elbow coordinates to JR3 coordinates
    # JR3 coordinates: x - on metal plate plane away from trunk, y - along forearm away from hand, 
    #                  z - perpendicular to metal plate to the shoulder
    # Elbow coordinates: y - supination (column 5), x - flexion 
    # Shoulder coordinates: x - extension, y - abduction, z - internal rotation
    if arm == 0:
        abd_angle = -abd_angle
    R_2 = roty(abd_angle)
    P_2 = np.dot(Px([0, 0, 0]),R_2)
    J = np.append(np.append(R_2,P_2,axis=1),np.append(zeros([3,3]),R_2,axis=1),axis=0)
    FMe = np.dot(np.transpose(J), FMjr)

    EFx = FMe[0][0]
    EFy = FMe[1][0]
    EFz = FMe[2][0]
    EMx = FMe[3][0]
    EMy = FMe[4][0]
    EMz = FMe[5][0]

    # Calculate the jacobian from shoulder coordinates to elbow coordinates
    # Shoulder coordinates: x - flexion, y - abduction, z - external rotation   
    R_3 = rotx(elb_angle - (pi/2))
    if arm == 1:
        E_3 = np.dot(Px([0, float(arm_length)*sin(elb_angle-(pi/2)), float(arm_length)*math.cos(elb_angle-(pi/2))]),R_3)

        J_1 = np.append(np.append(R_3,E_3,axis=1),np.append(zeros([3,3]),R_3,axis=1),axis=0)
    elif arm == 0:
        E_3 = np.dot(Px([0, float(arm_length)*sin(elb_angle-(pi/2)), -float(arm_length)*math.cos(elb_angle-(pi/2))]),R_3)

        J_1 = np.append(np.append(R_3,E_3,axis=1),np.append(zeros([3,3]),R_3,axis=1),axis=0)
    
    FMsh = np.dot(np.transpose(J_1), FMe)

    SFx = FMsh[0][0]
    SFy = FMsh[1][0]
    SFz = FMsh[2][0]
    SMx = FMsh[3][0]
    SMy = FMsh[4][0] # Change the sign for moment around y (abd/add) so that abd is positive and add is negative
    SMz = FMsh[5][0]

    result = [EFx, EFy, EFz, EMx, EMy, EMz, SFx, SFy, SFz, SMx, SMy, SMz]

    return result



def main():
    # Emonitor section, delegating the subprocess and connection
    QUEUES = []

    # Process for monitor and monitor queue

    emonitor_queue = Queue()

    QUEUES.append(emonitor_queue)
    em_p = Process(target=emonitor_run, args=(1 / 60, emonitor_queue))
    em_p.start()

    # Process and queues for the GUI

    gui_queue = Queue()
    gui_out_queue = Queue()
    QUEUES.append(gui_queue)
    QUEUES.append(gui_out_queue)

    gui_p = Process(target=gui_run, args=(gui_queue, gui_out_queue))
    gui_p.start()

    # Initialize data collection
    HZ = 1000

    data_intake_queue = Queue()
    data_intake_comm_queue = Queue()
    QUEUES.append(data_intake_queue)
    QUEUES.append(data_intake_comm_queue)
    data_intake_p = Process(
        target=data_sender, args=(1 / HZ, data_intake_queue, data_intake_comm_queue)
    )
    data_intake_p.start()

    # Initialize plotting
    plotting_comm_queue = Queue()
    QUEUES.append(plotting_comm_queue)
    plotting_p = Process(target=animation_control, args=(plotting_comm_queue,))
    plotting_p.start()

    # Initialize the experiment dataclass
    experiment = MainExperiment()

    TRANSMIT_KEYS = [
        "target_EL_tor",
        "low_lim_EL_tor",
        "up_lim_EL_tor",
        "match_EL_tor",
        "target_SH_tor",
        "low_lim_SH_tor",
        "up_lim_SH_tor",
        "match_SH_tor",
        "sound_trigger",
        "stop_trigger",
    ]

    is_saved = False
    is_saved_folder = False
    is_ending = False
    is_plotting = False

    is_saved_trial2 = True
    is_saved_trial3 = True
    is_saved_trial4 = True
    is_saved_trial5 = True
    is_saved_trial6 = True


    is_ending_trial2 = False
    is_ending_trial3 = False
    is_ending_trial4 = False
    is_ending_trial5 = False
    is_ending_trial6 = False

    is_break = False
    

    data_buffer = deque()


    while em_p.is_alive():
        transfer = dict.fromkeys(TRANSMIT_KEYS, 0)

        transfer["sound_trigger"] = []

        def start_sound(string):
            transfer["sound_trigger"] = [string]

        data = None

        while not data_intake_queue.empty():
            data_seq = data_intake_queue.get()
            for point in data_seq:
                data_buffer.append(point)

        if data_buffer:
            data = data_buffer.popleft()
            experiment.Fz, experiment.Fy, experiment.Fx, experiment.Mz, experiment.My, experiment.Mx, experiment.EMG_1, experiment.EMG_2, experiment.EMG_3, experiment.EMG_4, experiment.EMG_5, experiment.EMG_6, experiment.EMG_7, experiment.EMG_8, experiment.timestep = data

        # Get the data from the remote controls
        while not gui_queue.empty():
            header, gui_data = gui_queue.get()

            if header == "Trial0":
                # Subject information
                experiment.subject_number = gui_data["Subject Number"]
                experiment.participant_age = gui_data["Age"]
                experiment.subject_type = gui_data["Subject Type"]
                experiment.participant_gender = gui_data["Gender"]
                experiment.participant_diabetes = gui_data["Diabetes"]
                experiment.participant_years_since_stroke = gui_data["Years since Stroke"]
                experiment.participant_dominant_arm = gui_data["Dominant Arm"]
                experiment.participant_paretic_arm = gui_data["Testing Arm"]

                # Jacobian information
                experiment.shoulder_aduction_angle = gui_data["Shoulder Abduction Angle (degree)"]
                experiment.elbow_flexion_angle = gui_data["Elbow Flexion Angle (degree)"]
                experiment.arm_length = gui_data["Arm Length (m)"]
                experiment.midloadcell_to_elbowjoint = gui_data["z_offset Midload cell to elbow joint (m)"]

                # save the data
                is_saved_folder = True
                if int(experiment.subject_number) < 10:
                    subject_saver = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                elif int(experiment.subject_number) < 0 and int(experiment.subject_number) > 99:
                    print("It is an Error")
                else:
                    subject_saver = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)

                subject_saver.add_header(
                    [
                        "Subject Number",
                        "Age",
                        "Gender",
                        "Subject Type",
                        "Diabetes",
                        "Years since Stroke",
                        "Dominant Arm",
                        "Testing Arm",
                        "Shoulder Abduction Angle (degree)",
                        "Elbow Flexion Angle (degree)",
                        "Arm Length (m)",
                        "Midload cell to elbow joint (m)",

                    ]
                )   

                # Create 6 files to save data for 6 tasks
                saver_trial1 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                saver_trial2 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                saver_trial3 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                saver_trial4 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                saver_trial5 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                saver_trial6 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)

                saver_matrix = [saver_trial1, saver_trial2, saver_trial3, saver_trial4, saver_trial5, saver_trial6]
                for i in range(6):
                    saver_matrix[i].add_header(
                        [
                            "Time",
                            "Target torque",
                            "Current elbow Torque(N)",
                            "Target force",
                            "Current shoulder Torque (N)",
                            "EMG_1 (Bicep)",
                            "EMG_2 (Tricep lateral)",
                            "EMG_3 (Anterior Deltoid)",
                            "EMG_4 (Medial Deltoid)",
                            "EMG_5 (Posterior Deltoid)",
                            "EMG_6 (Pectoralis Major)",
                            "EMG_7 (Lower Trapezius)",
                            "EMG_8 (Middle Trapezius)",
                            "Sensor Fx",
                            "Sensor Fy",
                            "Sensor Fz",
                            "Sensor Mx",
                            "Sensor My",
                            "Sensor Mz"
                        ]
                    )

                # add data in the subject file
                subject_saver.add_data(
                    [
                        experiment.subject_number,
                        experiment.participant_age,
                        experiment.participant_gender,
                        experiment.subject_type,
                        experiment.participant_diabetes,
                        experiment.participant_years_since_stroke,
                        experiment.participant_dominant_arm,
                        experiment.participant_paretic_arm,
                        experiment.shoulder_aduction_angle,
                        experiment.elbow_flexion_angle,
                        experiment.arm_length,
                        experiment.midloadcell_to_elbowjoint
                    ]
                )
                subject_saver.save_data("Subject_Information", "Sub")
                subject_saver.clear()

            elif header == "Trial1":
                # At present, the task is Trial 1 MAX Measurement
                experiment.task = "Trial1"

                # get the experiment mode (Set 1, Set 2 ... Set 8)
                experiment.mode_state = gui_data["Experiment Mode"]

                # Set 6: Elbow flexion maximum    Set 7: Elbow extension maximum     Set 8: Shoulder abduction torque
                if experiment.mode_state == "Set 6" or experiment.mode_state == "Set 7":
                    experiment.target_EL_tor = gui_data["Initial Value"]
                    experiment.target_SH_tor = 1000000
                elif experiment.mode_state == "Set 8":
                    experiment.target_EL_tor = 1000000
                    experiment.target_SH_tor = gui_data["Initial Value"]

                # get the start time when the trial 1 is starting
                initial_time_trial1 = experiment.timestep

                # if the data in trial 1 has been saved, then delete the old data
                if is_saved:
                    saver_trial1.clear()
                
                is_saved = True
                is_plotting = False

            elif header == "Trial2":
                experiment.task = "Trial2"

                # 25% MVT_EF   20% MVT_Shoulder_abduction
                experiment.target_EL_tor = float(gui_data["Maximum Elbow Flexion (N)"])*0.25
                experiment.target_SH_tor = float(gui_data["Max Shoulder Abduction (Nm)"])*0.2

                # Mode: Automatic, Up direction, In direction, Up and In direction
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial 2 is starting
                initial_time_trial2 = experiment.timestep

                if is_saved_trial2:
                    saver_trial2.clear()
                
                is_saved_trial2 = False
                

            elif header == "Trial3":
                experiment.task = "Trial3"

                # 25% MVT_EF   10%, 30%, 50% MVT_Shoulder_abduction
                experiment.target_EL_tor = float(gui_data["Maximum Elbow Flexion (N)"])*0.25

                # Mode: Set 1, Set 2, Set 3
                experiment.mode_state = gui_data["Experiment Mode"]
                experiment.trial_state = gui_data["Experiment trial"]

                if experiment.mode_state == "Set 1":
                    experiment.target_SH_tor = float(gui_data["Max Shoulder Abduction (Nm)"])*0.1
                
                elif experiment.mode_state == "Set 2":
                    experiment.target_SH_tor = float(gui_data["Max Shoulder Abduction (Nm)"])*0.3
                
                elif experiment.mode_state == "Set 3":
                    experiment.target_SH_tor = float(gui_data["Max Shoulder Abduction (Nm)"])*0.5

                # get the start time when the trial 3 is starting
                initial_time_trial3 = experiment.timestep

                if is_saved_trial3:
                    saver_trial3.clear()
                
                is_saved_trial3 = False

            elif header == "Trial4":
                experiment.task = "Trial4"

                # Mode: Set 1
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial 4 is starting
                initial_time_trial4 = experiment.timestep

                if is_saved_trial4:
                    saver_trial4.clear()
                
                is_saved_trial4 = False

            elif header == "Trial5":
                experiment.task = "Trial5"

                # 25% MVT_EF   20% MVT_Shoulder_abduction
                experiment.target_EL_tor = float(gui_data["Maximum Elbow Flexion (N)"])*0.25
                experiment.target_SH_tor = float(gui_data["Max Shoulder Abduction (Nm)"])*0.2

                # Mode: Automatic, Up direction, In direction, Up and In direction
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial 5 is starting
                initial_time_trial5 = experiment.timestep

                if is_saved_trial5:
                    saver_trial5.clear()
                
                is_saved_trial5 = False
            
            elif header == "Trial6":
                experiment.task = "Trial6"

                # Mode: Set 1 Set 2 Set 3 Set 4
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial6 is starting
                initial_time_trial6 = experiment.timestep

                if is_saved_trial6:
                    saver_trial6.clear()
                
                is_saved_trial6 = False

            elif header == "Stop":
                experiment.task = "Stop"


            elif header == "Close":
                gui_p.terminate()
                em_p.terminate()

        if not data:
            continue

        # Sound Time
        Hold_time = 1.0
        Match_time = 1.0    
        Relax_time = 1.3

        Starting_time = 1.2
        TrigBuzzStop_timer_time = 0.2
        Ending_time = 1.0
        Z_force_out_of_range_time = 1.5
        wrong_direction_time = 1.5   

        In_time = 1.0
        Out_time = 1.0
        Up_time = 1.0
        Down_time = 1.0

        # start to save the data
        if is_saved_folder:
            for i in range(6):
                saver_matrix[i].add_data(
                    [
                        experiment.timestep,
                        experiment.target_EL_tor,
                        experiment.match_EL_tor,
                        experiment.target_SH_tor,
                        experiment.match_SH_tor,
                        experiment.EMG_1,
                        experiment.EMG_2,
                        experiment.EMG_3,
                        experiment.EMG_4,
                        experiment.EMG_5,
                        experiment.EMG_6,
                        experiment.EMG_7,
                        experiment.EMG_8,
                        Jac_result[0],
                        Jac_result[1],
                        Jac_result[2],
                        Jac_result[3],
                        Jac_result[4],
                        Jac_result[5],
                    ]
                )
        # --------------------------------------------------------Jacobian calculate---------------------------------------------------
        FMraw = np.transpose([experiment.Fx, 
                              experiment.Fy,
                              experiment.Fz,
                              experiment.Mx,
                              experiment.My,
                              experiment.Mz])
        Jac_result = Jac_convert(FMraw, experiment.shoulder_aduction_angle, experiment.elbow_flexion_angle, experiment.arm_length, experiment.midloadcell_to_elbowjoint, experiment.participant_paretic_arm)
        # experiment.match_EL_tor = Jac_result[2] # EFz
        # experiment.match_SH_tor = Jac_result[10] # SMy
        experiment.match_EL_tor = experiment.Fz # EFz
        experiment.match_SH_tor = experiment.Fy # SMy

        # --------------------------------------------------------Trial Type 1: MAX Measurement-------------------------------------------------
        if experiment.task == "Trial1":

            # get the time in the trail 1
            trial1_time = experiment.timestep - initial_time_trial1

            # set 1 to set 5 will only have "starting" and "ending" sound
            if experiment.mode_state == "Set 1" or experiment.mode_state == "Set 2" or experiment.mode_state == "Set 3" or experiment.mode_state == "Set 4" or experiment.mode_state == "Set 5":
                
                start = Starting_time+0.6              
                end = start+Ending_time+5.0     
                stop = end+0.5       

                if trial1_time < 0.1:
                    start_sound("starting")

                elif trial1_time >= end and trial1_time <= stop:
                    start_sound("ending")

                elif trial1_time >= stop and is_plotting == False:
                    is_ending = True
                    is_plotting = True
            
            # set 6 (elbow flextion) will have "starting", "in" and "ending" sounds
            elif experiment.mode_state == "Set 6":

                start = Starting_time+0.6  
                in_time = start+In_time+5.0
                relax_time = in_time+Relax_time+0.2
                end = relax_time+Ending_time+0.2
                stop = end+0.5  

                if trial1_time < 0.1:
                    start_sound("starting")

                elif trial1_time >= start and trial1_time <= in_time:
                    start_sound("in")

                elif trial1_time >= in_time and trial1_time <= relax_time:
                    start_sound("relax")

                elif trial1_time >= relax_time and trial1_time <= end:
                    start_sound("ending")

                elif trial1_time >= stop and is_plotting == False:
                    is_ending = True
                    is_plotting = True

            # set 7 (elbow extension) will have "starting", "out" and "ending" sounds
            elif experiment.mode_state == "Set 7":

                start = Starting_time+0.6  
                out_time = start+Out_time+5.0
                relax_time = out_time+Relax_time+0.2
                end = relax_time+Ending_time+0.2
                stop = end+0.5  

                if trial1_time < 0.1:
                    start_sound("starting")

                elif trial1_time >= start and trial1_time <= out_time:
                    start_sound("out")

                elif trial1_time >= out_time and trial1_time <= relax_time:
                    start_sound("relax")

                elif trial1_time >= relax_time and trial1_time <= end:
                    start_sound("ending")

                elif trial1_time >= stop and is_plotting == False:
                    is_ending = True
                    is_plotting = True

            # set 8 (shoulder abduction) will have "starting", "up" and "ending" sounds
            elif experiment.mode_state == "Set 8":

                start = Starting_time+0.6  
                up_time = start+Up_time+5.0
                relax_time = up_time+Relax_time+0.2
                end = relax_time+Ending_time+0.2
                stop = end+0.5  

                if trial1_time < 0.1:
                    start_sound("starting")

                elif trial1_time >= start and trial1_time <= up_time:
                    start_sound("up")

                elif trial1_time >= up_time and trial1_time <= relax_time:
                    start_sound("relax")

                elif trial1_time >= relax_time and trial1_time <= end:
                    start_sound("ending")

                elif trial1_time >= stop and is_plotting == False:
                    is_ending = True
                    is_plotting = True

            if is_ending:
                is_ending = False
                experiment.max_torque = saver_trial1.save_and_plot_data("MAX_Measurement", experiment.mode_state)

                print('Maximum value is ')
                print(experiment.max_torque)
                gui_data = [
                    experiment.timestep,
                    experiment.target_EL_tor,
                    experiment.match_EL_tor,
                    experiment.max_torque,
                    experiment.mode_state
                ]
                if not gui_out_queue.full():
                    gui_out_queue.put((gui_data))
                is_get_max_torque = True
            
        
        # --------------------------------------------------------Trial Type 2: pre-motor task-------------------------------------------------

        if experiment.task == "Trial2":
    
            # get the time in the trail 2
            trial2_time = experiment.timestep - initial_time_trial2

            if experiment.mode_state == "Up direction":

                is_ending_trial2 = trial2_up(trial2_time, 0, is_break, False)
            
            elif experiment.mode_state == "In direction":

                is_ending_trial2 = trial2_in(trial2_time, 0, is_break, False)
            
            elif experiment.mode_state == "Up and In direction":

                is_ending_trial2 = trial2_together(trial2_time, 0, is_break, False)


            if is_ending_trial2 and is_saved_trial2 == False:
                    saver_trial2.save_data("Pre-motor assessment", experiment.mode_state)
                    is_saved_trial2 = True

        def trial2_up(SimTime, start_time, is_break, is_ending_trial2):
            start = Starting_time+0.6+start_time              # 0 - 1.8
            up = start+Up_time+2.0                 # 1.8 - 4.8
            hold = up+Hold_time+1.5                # 4.8 - 7.3
            relax = hold+Relax_time+0.5            # 7.3 - 9.1
            end = relax+Ending_time                # 9.1 - 10.1
            stop = end+2.0

            # Up trial
            if SimTime < 0.1+start_time and is_break == False:
                start_sound("starting")

            elif SimTime >= start and SimTime <= up and is_break == False:
                    start_sound("up")

            elif SimTime >= up and SimTime <= hold and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                else:
                    is_break = True
                    break_time = hold

            # hold for 1.5 second 
            elif SimTime >= hold and SimTime <= relax and is_break == False:
                start_sound("relax")

            elif SimTime >= relax and SimTime <= end and is_break == False:
                start_sound("ending")

            elif is_break and SimTime <= break_time:
                start_sound("out of range")
            
            elif is_break and SimTime >= break_time:
                start_sound("ending")
                is_ending_trial2 = True
            
            elif SimTime >= end and SimTime <= stop and is_break == False:
                is_ending_trial2 = True
            
            return is_ending_trial2

        def trial2_in(SimTime, start_time, is_break, is_ending_trial2):
            # bar time
            start = Starting_time+0.6+start_time              # 0 - 1.8
            in_time = start+In_time+2.0                 # 1.8 - 4.8
            hold = in_time+Hold_time+1.5                # 4.8 - 7.3
            relax_1 = hold+Relax_time+0.5            # 7.3 - 9.1
            out = relax_1+Out_time+0.2
            relax_2 = out+Relax_time+0.5           
            end = relax_2+Ending_time  
            stop = end+5.0

            # Up trial
            if SimTime < 0.1+start_time and is_break == False:
                start_sound("starting")

            elif SimTime >= start and SimTime <= in_time and is_break == False:
                    start_sound("in")

            elif SimTime >= in_time and SimTime <= hold and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                else:
                    is_break = True
                    break_time = hold

            # hold for 1.5 second 
            elif SimTime >= hold and SimTime <= relax_1 and is_break == False:
                start_sound("relax")

            elif SimTime >= relax_1 and SimTime <= out and is_break == False:
                start_sound("out")

            elif SimTime >= out and SimTime <= relax_2 and is_break == False:
                start_sound("relax")

            elif SimTime >= relax_2 and SimTime <= end and is_break == False:
                start_sound("ending")

            elif is_break and SimTime <= break_time:
                start_sound("out of range")
            
            elif is_break and SimTime >= break_time:
                start_sound("ending")
                is_ending_trial2 = True
            
            elif SimTime >= end and SimTime <= stop and is_break == False:
                is_ending_trial2 = True
            
            return is_ending_trial2

        def trial2_together(SimTime, start_time, is_break, is_ending_trial2):

            # bar time
            start = Starting_time+0.6+start_time              
            up = start+Up_time+2.0                 
            hold_1 = up+Hold_time+1.5               
            in_time = hold_1+In_time+2.0
            hold_2 = in_time+Hold_time+1.5                
            relax_1 = hold_2+Relax_time+0.5  
            out = relax_1+Out_time+0.2
            relax_2 = out+Relax_time+0.5           
            end = relax_2+Ending_time  
            stop = end + 2.0 

            # upin trial
            if SimTime < 0.1+start_time and is_break == False:
                start_sound("starting")
            elif SimTime >= start and SimTime <= up  and is_break == False:
                start_sound("up")

            elif SimTime >= up and SimTime <= hold_1 and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                else:
                    is_break = True

            elif SimTime >= hold_1 and SimTime <= in_time and is_break == False:
                start_sound("in")

            elif SimTime >= in_time and SimTime <= hold_2 and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                else:
                    is_break = True

            # hold for 1.5 second 
            elif SimTime >= hold_2 and SimTime <= relax_1 and is_break == False:
                start_sound("relax")

            elif SimTime >= relax_1 and SimTime <= out and is_break == False:
                start_sound("out")

            elif SimTime >= out and SimTime <= relax_2 and is_break == False:
                start_sound("relax")

            elif SimTime >= relax_2 and SimTime <= end and is_break == False:
                start_sound("ending")

            elif SimTime >= end and SimTime <= stop and is_break == False:
                is_ending_trial2 = True

            elif is_break:
                start_sound("out of range")
                is_ending_trial2 = True

            return is_ending_trial2

        # --------------------------------------------------------Trial Type 3: Matching Tasks-------------------------------------------------

        def trial3_sound(SimTime, start_time, is_break, is_ending_trial3):
            # Trial3

            # Start : start_time(0) - 1.7(0+1.2+0.5)

            # up: “Up” + 0.2+2
            start_time_1 = start_time+Starting_time+0.5
            end_time_1 = start_time_1+Up_time

            # hold: “hold” + 1.0
            end_time_2 = end_time_1+Hold_time+1.0

            # in: “In”+0.2+2
            end_time_3 = end_time_2+Relax_time+2.2

            # hold: “hold”+2 
            end_time_4 = end_time_3+Hold_time+2.0

            # relax: “Relax” + 6
            end_time_5 = end_time_4+Relax_time+5.0

            # match: “Match” +2
            end_time_6 = end_time_5+Match_time+2.0

            # hold: “Hold” + 1
            end_time_7 = end_time_6+Hold_time+1.0

            # relax: “Relax” + 0.5
            end_time_8 = end_time_7+Relax_time+0.5

            # out: “Out”+0.2
            end_time_9 = end_time_8+Out_time+0.2

            # relax: “Relax”+0.5
            end_time_10 = end_time_9+Relax_time+0.5

            # End: “End” +2
            end_time_11 = end_time_10+Ending_time+2.0

            end_time_12 = end_time_11+0.5


            # Trial3

            if SimTime < 0.1+start_time and is_break == False:
                start_sound("starting")

            elif SimTime >= start_time_1 and SimTime <= end_time_1  and is_break == False:
                start_sound("up")

            elif SimTime >= end_time_1 and SimTime <= end_time_2 and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                elif experiment.match_EL_tor < 0:
                    start_sound("wrong direction")
                    is_break = True
                else:
                    is_break = True

            elif SimTime >= end_time_2 and SimTime <= end_time_3 and is_break == False:
                start_sound("in")

            elif SimTime >= end_time_3 and SimTime <= end_time_4 and is_break == False:
                if experiment.match_EL_tor >= float(experiment.target_EL_tor) * 0.8 and experiment.match_EL_tor <= float(experiment.target_EL_tor) * 1.2:
                    start_sound("hold")
                elif experiment.match_EL_tor < 0:
                    start_sound("wrong direction")
                    is_break = True
                else:
                    is_break = True

            # relax
            elif SimTime >= end_time_4 and SimTime <= end_time_5 and is_break == False:
                start_sound("relax")


            elif SimTime >= end_time_5 and SimTime <= end_time_6 and is_break == False:
                start_sound("match")
                experiment.target_EL_tor = 1000000
            elif SimTime >= end_time_6 and SimTime <= end_time_7 and is_break == False:
                start_sound("hold")
            
            elif SimTime >= end_time_7 and SimTime <= end_time_8 and is_break == False:
                start_sound("relax")

            elif SimTime >= end_time_8 and SimTime <= end_time_9 and is_break == False:
                start_sound("out")

            elif SimTime >= end_time_9 and SimTime <= end_time_10 and is_break == False:
                start_sound("relax")

            elif SimTime >= end_time_10 and SimTime <= end_time_11 and is_break == False:
                start_sound("ending")
            elif SimTime >= end_time_11 and SimTime <= end_time_12 and is_break == False:
                is_ending_trial3 = True

            elif is_break:
                start_sound("out of range")
                is_ending_trial3 = True

            return is_ending_trial3

        if experiment.task == "Trial3":

            # get the time in the trail 3
            trial3_time = experiment.timestep - initial_time_trial3

            is_ending_trial3 = trial3_sound(trial3_time, 0, is_break, False)
            
            if is_ending_trial3 and is_saved_trial3 == False:
                saver_trial3.save_data("Matching_Task", experiment.mode_state)
                is_saved_trial3 = True
        
        # --------------------------------------------------------Trial Type 4: Baseline EMG-------------------------------------------------

        if experiment.task == "Trial4":
    
            # get the time in the trail 4
            trial4_time = experiment.timestep - initial_time_trial4

            # set 1 will only have "starting" and "ending" sound
            if experiment.mode_state == "Set 1":
                
                start = Starting_time+0.6              
                end = start+Ending_time+5.0     
                stop = end+0.5       

                if trial4_time < 0.1:
                    start_sound("starting")

                elif trial4_time >= end and trial4_time <= stop:
                    start_sound("ending")

                elif trial4_time >= stop:
                    is_ending_trial4 = True

            # save the data in the trial 4
            if is_ending_trial4 and is_saved_trial4 == False:
                    saver_trial4.save_data("Baseline_EMG", experiment.mode_state)
                    is_saved_trial4 = True


        # --------------------------------------------------------Trial Type 5: Post-motor assessment-------------------------------------------------
        if experiment.task == "Trial5":
        
            # get the time in the trail 5
            trial5_time = experiment.timestep - initial_time_trial5

            if experiment.mode_state == "Up direction":

                is_ending_trial5 = trial2_up(trial5_time, 0, is_break, False)
            
            elif experiment.mode_state == "In direction":

                is_ending_trial5 = trial2_in(trial5_time, 0, is_break, False)
            
            elif experiment.mode_state == "Up and In direction":

                is_ending_trial5 = trial2_together(trial5_time, 0, is_break, False)

            # save the data in the trial 5
            if is_ending_trial5 and is_saved_trial5 == False:
                saver_trial5.save_data("Post-motor_assessment", experiment.mode_state)
                is_saved_trial5 = True

        # --------------------------------------------------------Trial Type 6: Working Memory trials-------------------------------------------------

        def trial6_sound(SimTime, start_time, is_ending_trial6, is_break, experiment_mode):
            start = Starting_time+0.6            
            in_time = start+In_time+0.5                 
            out = in_time+Out_time+0.5
            up = out+Up_time+0.5 
            down = up+Down_time+0.5                          
            end = down+Ending_time+0.6
            stop = end+1.0

            if experiment_mode == "Set 1":
                sound_matrix = ["in", "out", "up", "down"]
            elif experiment_mode == "Set 2":
                sound_matrix = ["out", "up", "down", "in"]
            elif experiment_mode == "Set 3":
                sound_matrix = ["up", "down", "in", "out"]
            elif experiment_mode == "Set 4":
                sound_matrix = ["down", "in", "out", "up"]

            # Up trial
            if SimTime < 0.1+start_time and is_break == False:
                start_sound("starting")

            elif SimTime >= start and SimTime <= in_time and is_break == False:
                    start_sound(sound_matrix[0])
            elif SimTime >= in_time and SimTime <= out and is_break == False:
                    start_sound(sound_matrix[1])
            elif SimTime >= out and SimTime <= up and is_break == False:
                    start_sound(sound_matrix[2])
            elif SimTime >= up and SimTime <= down and is_break == False:
                    start_sound(sound_matrix[3])
            elif SimTime >= down and SimTime <= end and is_break == False:
                    start_sound("ending")
            
            elif SimTime >= end and SimTime <= stop and is_break == False:
                is_ending_trial6 = True
            
            return is_ending_trial6

        if experiment.task == "Trial6":
            # get the time in the trail 6
            trial6_time = experiment.timestep - initial_time_trial6

            is_ending_trial6 = trial6_sound(trial6_time, 0, False, is_break, experiment.mode_state)


            if is_ending_trial6 and is_saved_trial6 == False:
                    saver_trial6.save_data("Working_Memory", experiment.mode_state)
                    is_saved_trial6 = True

        # --------------------------------------------------------input data into monitor and plotter-------------------------------------------------
        # Initializes the dict of outputs with zeros
        # Care should be taken S.T. dict is initialized with valid, legal
        # arguments
        transfer["stop_trigger"] = False

        transfer["target_EL_tor"] = experiment.target_EL_tor
        transfer["low_lim_EL_tor"] = str(float(experiment.target_EL_tor) * 0.9)
        transfer["up_lim_EL_tor"] = str(float(experiment.target_EL_tor) * 1.1)
        transfer["match_EL_tor"] = experiment.match_EL_tor

        transfer["target_SH_tor"] = experiment.target_SH_tor
        transfer["low_lim_SH_tor"] = str(float(experiment.target_SH_tor) * 0.9)
        transfer["up_lim_SH_tor"] = str(float(experiment.target_SH_tor) * 1.1)
        transfer["match_SH_tor"] = experiment.match_SH_tor

        # This runs slowly, so we can run the emonitor whenever it's convenient
        if not emonitor_queue.full():
            emonitor_queue.put(transfer)

        if not plotting_comm_queue.full():
            # These are the values to be plotted. The first value MUST be the
            # timestep, but the rest may be changed
            graph_titles = [
                "Elbow Torque(Nm)",
                "Shoulder Torque (Nm)",
                "Bicep (EMG_1)",
                "Tricep lateral (EMG_2)",
                "Anterior Deltoid (EMG_3)",
                "Medial Deltoid (EMG_4)",
                "Posterior Deltoid (EMG_5)",
                "Pectoralis Major (EMG_6)",
                "Lower Trapezius (EMG_7)",
                "Middle Trapezius (EMG_8)",
            ]

            graph_data = [
                experiment.timestep,
                experiment.match_EL_tor,
                experiment.match_SH_tor,
                experiment.EMG_1,
                experiment.EMG_2,
                experiment.EMG_3,
                experiment.EMG_4,
                experiment.EMG_5,
                experiment.EMG_6,
                experiment.EMG_7,
                experiment.EMG_8,
            ]
            plotting_comm_queue.put((graph_data, graph_titles))

    # Exit all processes

    # Exit the DAQ
    data_intake_comm_queue.put("EXIT")
    plotting_comm_queue.put("EXIT")
    data_intake_p.join()
    plotting_p.join()

    # Clear the queues
    for queue in QUEUES:
        while not queue.empty():
            queue.get_nowait()


if __name__ == "__main__":
    main()