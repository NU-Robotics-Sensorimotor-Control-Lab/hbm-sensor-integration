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


@dataclass
class MainExperiment:
    # Experimental state and control
    experiment_mode: str = "DEFAULT"
    mode_state: str = "SHOULDER ELBOW"
    state_section: str = "AUTO"
    paused: bool = False

    # Experimental variables for controlling the output
    target_tor: float = 1.0
    low_lim_tor: float = 0.8
    up_lim_tor: float = 1.2
    match_tor: float = 1.0

    targetF: float = 1.0
    low_limF: float = 0.8
    up_limF: float = 1.2
    matchF: float = 1.0

    max_torque: float = 1.0

    EMG_1: float = 1.0
    EMG_2: float = 1.0
    EMG_3: float = 1.0
    EMG_4: float = 1.0
    EMG_5: float = 1.0
    EMG_6: float = 1.0
    EMG_7: float = 1.0
    EMG_8: float = 1.0

    timestep: float = 0

    # Info about the participants
    subject_number: float = 0
    participant_age: float = 0
    participant_gender: str = "UNSPECIFIED"
    participant_years_since_stroke: int = 0
    participant_dominant_arm: str = "RIGHT"
    participant_paretic_arm: str = "NONE"
    participant_disabetes: str = "NO"
    
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
        "target_tor",
        "low_lim_tor",
        "up_lim_tor",
        "match_tor",
        "targetF",
        "low_limF",
        "up_limF",
        "matchF",
        "sound_trigger",
        "stop_trigger",
    ]

    is_saved = False
    is_saved_folder = False
    is_ending = False
    is_plotting = False

    is_ending_trial2 = False

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
            experiment.match_tor, experiment.matchF, experiment.EMG_1, experiment.EMG_2, experiment.EMG_3, experiment.EMG_4, experiment.EMG_5, experiment.EMG_6, experiment.EMG_7, experiment.EMG_8, experiment.timestep = data

        # Get the data from the remote controls
        while not gui_queue.empty():
            header, gui_data = gui_queue.get()

            if header == "Subject Info":
                experiment.subject_number = gui_data["Subject Number"]
                experiment.participant_age = gui_data["Age"]
                experiment.subject_type = gui_data["Subject Type"]
                experiment.participant_gender = gui_data["Gender"]
                experiment.participant_disabetes = gui_data["Disabetes"]
                experiment.participant_years_since_stroke = gui_data["Years since stroke"]
                experiment.participant_dominant_arm = gui_data["Dominant Arm"]
                experiment.participant_paretic_arm = gui_data["Testing Arm"]

                print(experiment.participant_gender)

            # elif header == "Sub_Save":
            elif header == "Jacobean Constants":
                experiment.shoulder_aduction_angle = gui_data["Shoulder Abduction Angle (degree)"]
                experiment.elbow_flexion_angle = gui_data["Elbow Flexion Angle (degree)"]
                experiment.arm_length = gui_data["Arm Length (m)"]
                experiment.midloadcell_to_elbowjoint = gui_data["Midload cell to elbow joint (m)"]

                print(experiment.shoulder_aduction_angle)

                is_saved_folder = True
                if int(experiment.subject_number) < 10:
                    subject_saver = data_saver(experiment.subject_type+" Subject0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)
                elif int(experiment.subject_number) < 0 and int(experiment.subject_number) > 99:
                    print("It is an Error")
                else:
                    subject_saver = data_saver(experiment.subject_type+" Subject0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)

                subject_saver.add_header(
                    [
                        "Subject Number",
                        "Age",
                        "Gender",
                        "Subject Type",
                        "Disabetes",
                        "Years since stroke",
                        "Dominant Arm",
                        "Testing Arm",
                        "Shoulder Abduction Angle (degree)",
                        "Elbow Flexion Angle (degree)",
                        "Arm Length (m)",
                        "Midload cell to elbow joint (m)",

                    ]
                )
                saver = data_saver(experiment.subject_type+" Subject0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)

                saver.add_header(
                    [
                        "Time",
                        "Target torque",
                        "Current elbow Torque(N)",
                        "Target force",
                        "Current shoulder Torque (N)",
                        "Bicep (EMG_1)",
                        "Tricep lateral (EMG_2)",
                        "Anterior Deltoid (EMG_3)",
                        "Medial Deltoid (EMG_4)",
                        "Posterior Deltoid (EMG_5)",
                        "Pectoralis Major (EMG_6)",
                        "Lower Trapezius (EMG_7)",
                        "Middle Trapezius (EMG_8)",
                    ]
                )

                saver_trial2 = data_saver(experiment.subject_type+" Subject0"+str(int(experiment.subject_number))+"/"+experiment.participant_paretic_arm)

                saver_trial2.add_header(
                    [
                        "Time",
                        "Target torque",
                        "Current elbow Torque(N)",
                        "Target force",
                        "Current shoulder Torque (N)",
                        "Bicep (EMG_1)",
                        "Tricep lateral (EMG_2)",
                        "Anterior Deltoid (EMG_3)",
                        "Medial Deltoid (EMG_4)",
                        "Posterior Deltoid (EMG_5)",
                        "Pectoralis Major (EMG_6)",
                        "Lower Trapezius (EMG_7)",
                        "Middle Trapezius (EMG_8)",
                    ]
                )

                experiment.subject_saver = subject_saver
                subject_saver.add_data(
                    [
                        experiment.subject_number,
                        experiment.participant_age,
                        experiment.participant_gender,
                        experiment.subject_type,
                        experiment.participant_disabetes,
                        experiment.participant_years_since_stroke,
                        experiment.participant_dominant_arm,
                        experiment.participant_paretic_arm,
                        experiment.shoulder_aduction_angle,
                        experiment.elbow_flexion_angle,
                        experiment.arm_length,
                        experiment.midloadcell_to_elbowjoint
                    ]
                )
                subject_saver.save_data("Subject Information")
                subject_saver.clear()


            elif header == "Close":
                gui_p.terminate()
                em_p.terminate()

            elif header == "EF_max":
                experiment.target_tor = gui_data["Input a initial value of MVT_EF (elbow flexion)"]
                experiment.mode_state = "Trial Type 1: MAX Measurement"
                initial_time = experiment.timestep
                if is_saved:
                    saver.clear()
                
                is_saved = True
                is_plotting = False

            elif header == "trial2_max":
                experiment.target_tor = gui_data["Maximum elbow flexion value"]
                experiment.mode_state = "Trial Type 2: Pre-motor assessment"
                initial_time_trial2 = experiment.timestep

        if not data:
            continue
        
        # If the mode state is Trial Type 1: max measurement
        if experiment.mode_state == "Trial Type 1: MAX Measurement":
            if experiment.timestep - initial_time < 0.1:
                start_sound("starting")

            elif experiment.timestep - initial_time >= 5.1 and experiment.timestep - initial_time <= 7.1:
                start_sound("ending")
            elif experiment.timestep - initial_time >= 7.1 and is_plotting == False:
                is_ending = True
                is_plotting = True

        if is_ending:
            is_ending = False
            experiment.max_torque = saver.save_and_plot_data("MAX Measurement")
            print('max_torque is ')
            print(experiment.max_torque)
            gui_data = [
                experiment.timestep,
                experiment.target_tor,
                experiment.match_tor,
                experiment.max_torque
            ]
            if not gui_out_queue.full():
                gui_out_queue.put((gui_data))
            is_get_max_torque = True
        

        if is_saved_folder:
            saver.add_data(
                [
                    experiment.timestep,
                    experiment.target_tor,
                    experiment.match_tor,
                    experiment.targetF,
                    experiment.matchF,
                    experiment.EMG_1,
                    experiment.EMG_2,
                    experiment.EMG_3,
                    experiment.EMG_4,
                    experiment.EMG_5,
                    experiment.EMG_6,
                    experiment.EMG_7,
                    experiment.EMG_8,
                ]
            )

            saver_trial2.add_data(
                [
                    experiment.timestep,
                    experiment.target_tor,
                    experiment.match_tor,
                    experiment.targetF,
                    experiment.matchF,
                    experiment.EMG_1,
                    experiment.EMG_2,
                    experiment.EMG_3,
                    experiment.EMG_4,
                    experiment.EMG_5,
                    experiment.EMG_6,
                    experiment.EMG_7,
                    experiment.EMG_8,
                ]
            )

        # If the mode state is Trial Type 2: Pre-motor assessment
        if experiment.mode_state == "Trial Type 2: Pre-motor assessment":
            if experiment.timestep - initial_time_trial2 < 0.1:
                start_sound("starting")

            elif experiment.timestep - initial_time_trial2 >= 5.1 and experiment.timestep - initial_time_trial2 <= 7.1:
                start_sound("ending")
            elif experiment.timestep - initial_time_trial2 >= 7.1:
                is_ending_trial2 = True
    
        if is_ending_trial2:
            is_ending_trial2 = False
            experiment.max_torque = saver.save_data("Pre-motor assessment")

        # Initializes the dict of outputs with zeros
        # Care should be taken S.T. dict is initialized with valid, legal
        # arguments
        transfer["stop_trigger"] = False

        transfer["target_tor"] = experiment.target_tor
        transfer["low_lim_tor"] = str(float(experiment.target_tor) * 0.9)
        transfer["up_lim_tor"] = str(float(experiment.target_tor) * 1.1)
        transfer["match_tor"] = experiment.match_tor

        transfer["targetF"] = experiment.targetF
        transfer["low_limF"] = str(float(experiment.targetF) * 0.9)
        transfer["up_limF"] = str(float(experiment.targetF) * 1.1)
        transfer["matchF"] = experiment.matchF

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
                experiment.match_tor,
                experiment.matchF,
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