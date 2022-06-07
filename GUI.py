from multiprocessing import Process, Queue
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import time
import numpy as np

class GUI(ttk.Frame):
    def __init__(self, master, conn, in_conn=None):
        super().__init__(master)

        self.running = ttk.BooleanVar(value=False)
        self.running_1 = ttk.BooleanVar(value=False)
        self.running_2 = ttk.BooleanVar(value=False)
        self.is_trial2_auto = False
        self.is_trial2_up = False
        self.is_trial2_in = False
        self.is_trial2_upin = False
        self.is_label = False

        self.is_trial3_status = False
        self.trial3_break = False

        self.is_trial4_status = False
        self.trial4_break = False

        self.is_trial5_auto = False
        self.is_trial5_up = False
        self.is_trial5_in = False
        self.is_trial5_upin = False

        self.is_trial6_set1 = False
        self.is_trial6_set2 = False
        self.is_trial6_set3 = False
        self.is_trial6_set4 = False
        self.trial6_break = False

        self.pause_bar = False
        self.stop_bar = False
        self.has_started_bar = False
        self.trial_finish = False

        # queues for multiprocessing
        self.data_queue = conn
        self.in_queue = in_conn

        self.master = master
        
        self.style = ttk.Style()
        self.style.configure('lefttab.TNotebook',tabposition='wn',
                tabmargins=[5, 5, 2, 5],padding= [0, 0],justify= "left",font=("Calibri", 15, "bold"),foreground='green')
                # tabposition='wn',
                # justify= "left",
                # padding= [20, 10],
                # font=("Calibri", "bold"))

        self.style.element_create('Plain.Notebook.tab', "from", 'default')
        self.style.layout("TNotebook.Tab",
            [('Plain.Notebook.tab', {'children':
                [('Notebook.padding', {'side': 'top', 'children':
                    [('Notebook.focus', {'side': 'top', 'children':
                        [('Notebook.label', {'side': 'top', 'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])

        self.style.configure('TNotebook.Tab', background='green', foreground='green')
        self.style.configure("TNotebook", background='#666666', foreground='green' )
        # self.style.map("TNotebook", background=[("selected", 'green')])
        self.notebk = ttk.Notebook(self.master, style='lefttab.TNotebook')

        # Tabs for each section
        self.frame0 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame1 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame2 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame3 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame4 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame5 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame6 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)

        self.notebk.add(self.frame0, text = 'Constant                              ')
        self.notebk.add(self.frame1, text = 'Maximum measurements   ')
        self.notebk.add(self.frame2, text = 'Pre-motor assessment        ')
        self.notebk.add(self.frame3, text = 'Matching trials                    ')
        self.notebk.add(self.frame4, text = "Baseline sEMG's                  ")
        self.notebk.add(self.frame5, text = 'Post-motor assessment      ')
        self.notebk.add(self.frame6, text = "Working Memory trials       ")
        self.notebk.pack(expand = 1, fill="both")

        self.set_frame0()
        self.set_frame1()
        self.set_frame2()
        self.set_frame3()
        self.set_frame4()
        self.set_frame5()
        self.set_frame6()

        # self.trial_iteration()
 
    # frame functions
    def set_frame0(self):
        # --------------------------- Frame 0 ----------------------------------------------
        self.title = ttk.Label(self.frame0, text="                                                      0. Constant Value", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial0_row = 0

        ######################### Input Constant Information #######################
        self.sub_lf = ttk.Labelframe(self.frame0,text="Constant Information", bootstyle=INFO)
        self.sub_lf.place(x=40,y=50,width=800,height=420)

        self.subjectInfo = ['Subject Number', 'Age', 'Gender', 'Subject Type', 'Diabetes', 'Years since Stroke', 
                             'Dominant Arm', 'Testing Arm']

        self.subject_result = []

        # Text entry fields
        for i in range(len(self.subjectInfo)):
            ttk.Label(self.sub_lf, text=self.subjectInfo[i],font=("Calibri", 10)).grid(row=i+1, column=0, padx=5, pady=5)
            if self.subjectInfo[i] not in ['Gender', 'Diabetes', 'Dominant Arm', 'Testing Arm']:
                e1 = ttk.Entry(self.sub_lf,show=None)
                e1.grid(row=i+1, column=1, padx=5, pady=5)
                self.subject_result.append(e1)


        # Option Menus
        self.subStringVars = ['Gender', 'Diabetes', 'Dominant Arm', 'Testing Arm']
        # Gender
        self.genders_StinngVar = ttk.StringVar(self.master)
        self.genders_First = 'Select a gender'
        self.genders_StinngVar.set(self.genders_First)
        self.genders_Type = ["Male", "Female", "Other"]
        self.genders_Menu = ttk.OptionMenu(self.sub_lf, self.genders_StinngVar, self.genders_Type[0], *self.genders_Type,)
        self.genders_Menu.grid(row=3, column=1, padx=5, pady=5)
    
        # Diabetes
        self.diabetes_StinngVar = ttk.StringVar(self.master)
        self.diabetes_First = 'YES/NO'
        self.diabetes_StinngVar.set(self.diabetes_First)
        self.diabetes_Type = ['YES','NO']
        self.diabetes_Menu = ttk.OptionMenu(self.sub_lf, self.diabetes_StinngVar, self.diabetes_Type[0], *self.diabetes_Type)
        self.diabetes_Menu.grid(row=5, column=1, padx=5, pady=5)

        # Dominant Arm
        self.domArm_StinngVar = ttk.StringVar(self.master)
        self.domArm_First = 'Left/Right'
        self.domArm_StinngVar.set(self.domArm_First)
        self.domArm_Type = ['Left','Right']
        self.domArm_Menu = ttk.OptionMenu(self.sub_lf, self.domArm_StinngVar, self.domArm_Type[0], *self.domArm_Type)
        self.domArm_Menu.grid(row=7, column=1, padx=5, pady=5)

        # Test Arm
        self.TestArm_StinngVar = ttk.StringVar(self.master)
        self.TestArm_First = 'Left/Right'
        self.TestArm_StinngVar.set(self.TestArm_First)
        self.TestArm_Type = ['Left','Right']
        self.TestArm_Menu = ttk.OptionMenu(self.sub_lf, self.TestArm_StinngVar, self.TestArm_Type[0], *self.TestArm_Type)
        self.TestArm_Menu.grid(row=8, column=1, padx=5, pady=5)


        ## Jacobian constant
        self.jacobInfo = ["Shoulder Abduction Angle (degree)","Elbow Flexion Angle (degree)","Arm Length (m)",
                          "z_offset Midload cell to elbow joint (m)"]

        self.jaco_result = []
        for i in range(len(self.jacobInfo)):
            ttk.Label(self.sub_lf, text=self.jacobInfo[i],font=("Calibri", 10)).grid(row=i+1, column=3, padx=5, pady=5)
            e2 = ttk.Entry(self.sub_lf,show=None)
            e2.grid(row=i+1, column=4, padx=5, pady=5)
            self.jaco_result.append(e2)

        # Submit constant information
        self.Constant_Sub = ttk.Button(self.sub_lf, text="Submit and Save", bootstyle=(INFO, OUTLINE), command=self.trial0_start)
        self.Constant_Sub.grid(row=8,column=3, padx=5, pady=5)

        self.Reset_button = ttk.Button(self.sub_lf, text="Reset to zero", bootstyle=(WARNING, OUTLINE), command=self.trial0_reset)
        self.Reset_button.grid(row=7,column=3, padx=5, pady=5)

        # End 
        self.End_lf = ttk.Frame(self.frame0)
        self.End_lf.place(x=700,y=700,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame1(self):

        # Bool number
        self.is_trial1_EMG = False
        self.is_trial1_in = False
        self.is_trial1_out = False
        self.is_trial1_up = False

        self.is_start_trial1 = True

        self.title = ttk.Label(self.frame1, text="               1, Maximum measurements (sEMGs, elbow and shoulder torques)", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial1_row = 0

        ### Description
        # add EF label frame
        self.trial1_lf = ttk.Labelframe(self.frame1,text="Preparation", bootstyle=INFO)
        self.trial1_lf.place(x=10,y=50,width=830,height=300)

        # description
        self.description_2 = ttk.Label(self.trial1_lf, text="Set 1: butterfly to get maximum for the pec          || Set 5: Abduct arm back maximum for posterior deltoid",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial1_lf, text="Set 2: squeeze shoulders or pump your chest for middle trap || Set 6: Elbow flexion maximum for bicep      ",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+2, column=0,columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial1_lf, text="Set 3: Abduct arm front maximum for anterior deltoid        || Set 7: Elbow extension maximum for tricep    ",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+3, column=0,columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial1_lf, text="Set 4: Abduct arm side for medial deltoid and lower trap    || Set 8: Shoulder abduction torque in the setup",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+4, column=0,columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+5, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+5, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+6, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+6, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+7, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+7, column=2, padx=5, pady=5)

        ### Experimental 
        # add trial1 experimental label frame
        self.trial1_exp_lf = ttk.Labelframe(self.frame1,text="Experimental", bootstyle=INFO)
        self.trial1_exp_lf.place(x=10,y=370,width=830,height=365)

        # # UP IN UP&IN
        self.title_1 = ttk.Label(self.trial1_exp_lf, text="Choose Tasks",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_1.grid(row=self.trial1_row+0, column=0, padx=5, pady=5)


        self.trial1_start_StinngVar = ttk.StringVar(self.master)
        self.trial1_start_First = 'Select a task'
        self.trial1_start_StinngVar.set(self.trial1_start_First)
        self.trial1_start_Type = ["Set 1", "Set 2", "Set 3", "Set 4", "Set 5", "Set 6", "Set 7", "Set 8"]
        self.trial1_start_Menu = ttk.OptionMenu(self.trial1_exp_lf, self.trial1_start_StinngVar, self.trial1_start_Type[0], *self.trial1_start_Type,)
        self.trial1_start_Menu.grid(row=self.trial1_row+0,column=1, padx=5, pady=5)

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="Enter initial value in Set 6, Set 7, Set 8",font=("Calibri", 10))
        self.title_1.grid(row=self.trial1_row+1, column=0, padx=5, pady=5)

        self.trial1_input = ttk.Entry(self.trial1_exp_lf,show=None)
        self.trial1_input.grid(row=self.trial1_row+1, column=1, padx=5, pady=5)


        self.trial1_button = ttk.Button(self.trial1_exp_lf, text="Start", command=self.trial1_toggle, bootstyle=DANGER)
        self.trial1_button.grid(row=self.trial1_row+1,column=2, padx=5, pady=5)

        self.trial1_button_2 = ttk.Button(self.trial1_exp_lf, text="Stop", command=self.trial1_stop, bootstyle=DANGER)
        self.trial1_button_2.grid(row=self.trial1_row+1,column=3, padx=5, pady=5)

        self.count_max = 0
        self.title_1 = ttk.Button(self.trial1_exp_lf, text="Record", command=self.trial1_Record, bootstyle=SUCCESS)
        self.title_1.grid(row=self.trial1_row+2,column=0, padx=5, pady=5)

        # # Trial and Status

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+3, column=2, padx=5, pady=5) 

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+4, column=2, padx=5, pady=5) 


        # Starting 
        self.title_1 = ttk.Label(self.trial1_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_1.grid(row=self.trial1_row+5, column=0, columnspan=5, padx=5, pady=5)   

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+6, column=0, padx=5, pady=5)   

        self.trial1_bar_max = 1000
        self.title_1_fg = ttk.Floodgauge(self.trial1_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_1_fg.grid(row=self.trial1_row+7, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame1)
        self.End_lf.place(x=700,y=740,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame2(self): 
        # --------------------------- Frame 2 ----------------------------------------------
        self.trial2_row = 1
        self.is_start_trial2 = True
        # Title
        self.title = ttk.Label(self.frame2, text="                                          2. Pre-motor assessment", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

         ### Description
        # add EF label frame
        self.trial2_lf = ttk.Labelframe(self.frame2,text="Preparation", bootstyle=INFO)
        self.trial2_lf.place(x=10,y=50,width=830,height=310)

        # description
        self.description_2 = ttk.Label(self.trial2_lf, text="    This section are used to check if the subject has the ability to complete the tasks. It will include ",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+0, column=0, columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial2_lf, text="    up direction, in direction and up&in direction. The order of automatic will be up, in and up&in.",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+1, column=0, columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+2, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+2, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+4, column=2, padx=5, pady=5)

        # Enter the maximum MVT value

        self.trial2_MVTInfo = ["Max Shoulder Abduction (Nm)","Maximum Elbow Extension (Nm)","Maximum Elbow Flexion (N)", "Experiment Mode"]

        self.trial2_result = []
        for i in range(2):
            ttk.Label(self.trial2_lf, text=self.trial2_MVTInfo[i],font=("Calibri", 10)).grid(row=self.trial2_row+6+i, column=0, padx=5, pady=5)
            trial2 = ttk.Entry(self.trial2_lf,show=None)
            trial2.grid(row=self.trial2_row+6+i, column=1, padx=5, pady=5)
            self.trial2_result.append(trial2)

        for i in range(1):
            ttk.Label(self.trial2_lf, text=self.trial2_MVTInfo[i+2],font=("Calibri", 10)).grid(row=self.trial2_row+6+i, column=2, padx=5, pady=5)
            trial2 = ttk.Entry(self.trial2_lf,show=None)
            trial2.grid(row=self.trial2_row+6+i, column=3, padx=5, pady=5)
            self.trial2_result.append(trial2)

        ### Experimental 
        # add trial2 experimental label frame
        self.trial2_exp_lf = ttk.Labelframe(self.frame2,text="Experimental", bootstyle=INFO)
        self.trial2_exp_lf.place(x=10,y=390,width=770,height=350)

        # UP IN UP&IN
        self.title_2 = ttk.Label(self.trial2_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_2.grid(row=self.trial2_row+0, column=0, padx=5, pady=5)


        self.trial2_start_StinngVar = ttk.StringVar(self.master)
        self.trial2_start_First = 'Select a task'
        self.trial2_start_StinngVar.set(self.trial2_start_First)
        self.trial2_start_Type = ["Automatic", "Up direction", "In direction", "Up and In direction"]
        self.trial2_start_Menu = ttk.OptionMenu(self.trial2_exp_lf, self.trial2_start_StinngVar, self.trial2_start_Type[0], *self.trial2_start_Type,)
        self.trial2_start_Menu.grid(row=self.trial2_row+0,column=1, padx=5, pady=5)


        self.trial2_button = ttk.Button(self.trial2_exp_lf, text="Start", command=self.trial2_toggle, bootstyle=DANGER)
        self.trial2_button.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)

        self.trial2_button_2 = ttk.Button(self.trial2_exp_lf, text="Stop", command=self.trial2_stop, bootstyle=DANGER)
        self.trial2_button_2.grid(row=self.trial2_row+0,column=3, padx=5, pady=5)

        # time and force
        self.title_2 = ttk.Label(self.trial2_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_2.grid(row=self.trial2_row+1, column=0, padx=5, pady=5)

        self.title_2 = ttk.Label(self.trial2_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_2.grid(row=self.trial2_row+1, column=2, padx=5, pady=5)

        self.title_2 = ttk.Label(self.trial2_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_2.grid(row=self.trial2_row+2, column=0, padx=5, pady=5) 


        # Starting 
        self.title_2 = ttk.Label(self.trial2_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_2.grid(row=self.trial2_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_2 = ttk.Label(self.trial2_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_2.grid(row=self.trial2_row+5, column=0, padx=5, pady=5)   

        self.trial2_bar_max = 1000
        self.title_2_fg = ttk.Floodgauge(self.trial2_exp_lf, bootstyle=INFO, length=750, maximum=self.trial2_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_2_fg.grid(row=self.trial2_row+6, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame2)
        self.End_lf.place(x=700,y=750,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame3(self):
        self.is_start_trial3 = True
        self.title = ttk.Label(self.frame3, text="                                         3, Single Arm Matching trials", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial3_row = 1
        ### Description
        # add EF label frame
        self.trial3_lf = ttk.Labelframe(self.frame3,text="Preparation", bootstyle=INFO)
        self.trial3_lf.place(x=10,y=50,width=830,height=310)

        # description
        self.description_2 = ttk.Label(self.trial3_lf, text="This section are used to do matching tasks. There are 2 type, 3 sets and 10 trials. Shoulder Set 1 means",font=("Calibri", 11))
        self.description_2.grid(row=self.trial3_row+0, column=0, columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial3_lf, text="shoulder will increase from 10% MVT to 30% and 50%. In the second type, elbow will change.",font=("Calibri", 11))
        self.description_2.grid(row=self.trial3_row+1, column=0, columnspan=4, padx=5, pady=5)


        # # INPUT MVT
        self.input_3 = ttk.Label(self.trial3_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+2, column=0, padx=5, pady=5)

        self.input_3 = ttk.Label(self.trial3_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+2, column=2, padx=5, pady=5)

        self.input_3 = ttk.Label(self.trial3_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+3, column=0, padx=5, pady=5)

        self.input_3 = ttk.Label(self.trial3_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+3, column=2, padx=5, pady=5)

        self.input_3 = ttk.Label(self.trial3_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+4, column=0, padx=5, pady=5)

        self.input_3 = ttk.Label(self.trial3_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_3.grid(row=self.trial3_row+4, column=2, padx=5, pady=5)

        # Enter the maximum MVT value

        self.trial3_MVTInfo = ["Max Shoulder Abduction (Nm)","Maximum Elbow Extension (Nm)","Maximum Elbow Flexion (N)", "Experiment Mode", "Experiment trial"]

        self.trial3_result = []
        for i in range(2):
            ttk.Label(self.trial3_lf, text=self.trial3_MVTInfo[i],font=("Calibri", 10)).grid(row=self.trial3_row+6+i, column=0, padx=5, pady=5)
            trial3 = ttk.Entry(self.trial3_lf,show=None)
            trial3.grid(row=self.trial3_row+6+i, column=1, padx=5, pady=5)
            self.trial3_result.append(trial3)

        for i in range(1):
            ttk.Label(self.trial3_lf, text=self.trial3_MVTInfo[i+2],font=("Calibri", 10)).grid(row=self.trial3_row+6+i, column=2, padx=5, pady=5)
            trial3 = ttk.Entry(self.trial3_lf,show=None)
            trial3.grid(row=self.trial3_row+6+i, column=3, padx=5, pady=5)
            self.trial3_result.append(trial3)


        ### Experimental 
        self.trial3_row = 0
        # add trial3 experimental label frame
        self.trial3_exp_lf = ttk.Labelframe(self.frame3,text="Experimental", bootstyle=INFO)
        self.trial3_exp_lf.place(x=10,y=370,width=770,height=350)

        # UP IN UP&IN
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_3.grid(row=self.trial3_row+0, column=0, padx=5, pady=5)


        self.trial3_start_StinngVar_1 = ttk.StringVar(self.master)
        self.trial3_start_First = 'Select a task'
        self.trial3_start_StinngVar_1.set(self.trial3_start_First)
        self.trial3_start_Type = ["Automatic", "Set 1", "Set 2", "Set 3"]
        self.trial3_start_Menu = ttk.OptionMenu(self.trial3_exp_lf, self.trial3_start_StinngVar_1, self.trial3_start_Type[0], *self.trial3_start_Type,)
        self.trial3_start_Menu.grid(row=self.trial3_row+0,column=1, padx=5, pady=5)


        self.trial3_start_StinngVar_2 = ttk.StringVar(self.master)
        self.trial3_start_First = 'Select a task'
        self.trial3_start_StinngVar_2.set(self.trial3_start_First)
        self.trial3_start_Type = ["Auto", "Trial 1","Trial 2","Trial 3","Trial 4","Trial 5","Trial 6","Trial 7","Trial 8","Trial 9","Trial 10"]
        self.trial3_start_Menu = ttk.OptionMenu(self.trial3_exp_lf, self.trial3_start_StinngVar_2, self.trial3_start_Type[0], *self.trial3_start_Type,)
        self.trial3_start_Menu.grid(row=self.trial3_row+0,column=2, padx=5, pady=5)


        self.trial3_button = ttk.Button(self.trial3_exp_lf, text="Start", command=self.trial3_Start, bootstyle=DANGER)
        self.trial3_button.grid(row=self.trial3_row+0,column=3, padx=5, pady=5)

        self.trial3_button_2 = ttk.Button(self.trial3_exp_lf, text="Stop", command=self.trial3_stop, bootstyle=DANGER)
        self.trial3_button_2.grid(row=self.trial3_row+0,column=4, padx=5, pady=5)

        self.trial3_button_3 = ttk.Button(self.trial3_exp_lf, text="Fixed", command=self.fixed_toggle_1, bootstyle=INFO)
        self.trial3_button_3.grid(row=self.trial3_row+1,column=1, padx=5, pady=5)

        self.trial3_button_4 = ttk.Button(self.trial3_exp_lf, text="Fixed", command=self.fixed_toggle_2, bootstyle=INFO)
        self.trial3_button_4.grid(row=self.trial3_row+1,column=2, padx=5, pady=5)

        # Trial and Status
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+2, column=0, padx=5, pady=5)

        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+2, column=2, padx=5, pady=5)


        # Starting 
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_3.grid(row=self.trial3_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_3 = ttk.Label(self.trial3_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+5, column=0, padx=5, pady=5)   

        self.title_3_fg = ttk.Floodgauge(self.trial3_exp_lf, bootstyle=INFO, length=750, maximum=1000, font=("Calibri", 12, 'bold'),)
        self.title_3_fg.grid(row=self.trial3_row+6, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame3)
        self.End_lf.place(x=700,y=740,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame4(self):
        self.is_start_trial4 = True
        self.title = ttk.Label(self.frame4, text="                                                  4, Baseline EMG", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial4_row = 0

        ### Description
        # add EF label frame
        self.trial4_lf = ttk.Labelframe(self.frame4,text="Preparation", bootstyle=INFO)
        self.trial4_lf.place(x=10,y=50,width=770,height=220)

        # description
        self.description_4 = ttk.Label(self.trial4_lf, text="This section will be used to test subject's EMG data. There are only one set and each set has only one ",font=("Calibri", 11))
        self.description_4.grid(row=self.trial4_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_4 = ttk.Label(self.trial4_lf, text="trial.                                                                       ",font=("Calibri", 11))
        self.description_4.grid(row=self.trial4_row+2, column=0, columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial4_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial4_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial4_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial4_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+4, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial4_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+5, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial4_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial4_row+5, column=2, padx=5, pady=5)


        ### Experimental 
        # add trial4 experimental label frame
        self.trial4_exp_lf = ttk.Labelframe(self.frame4,text="Experimental", bootstyle=INFO)
        self.trial4_exp_lf.place(x=10,y=300,width=770,height=350)

        # UP IN UP&IN
        self.title_4 = ttk.Label(self.trial4_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_4.grid(row=self.trial4_row+0, column=0, padx=5, pady=5)

        self.trial4_start_StinngVar = ttk.StringVar(self.master)
        self.trial4_start_First = 'Select a task'
        self.trial4_start_StinngVar.set(self.trial4_start_First)
        self.trial4_start_Type = ["Set 1"]
        self.trial4_start_Menu = ttk.OptionMenu(self.trial4_exp_lf, self.trial4_start_StinngVar, self.trial4_start_Type[0], *self.trial4_start_Type,)
        self.trial4_start_Menu.grid(row=self.trial4_row+0,column=1, padx=5, pady=5)


        self.title_4 = ttk.Button(self.trial4_exp_lf, text="Start", command=self.trial4_Start, bootstyle=DANGER)
        self.title_4.grid(row=self.trial4_row+0,column=2, padx=5, pady=5)

        # time and force
        self.title_4 = ttk.Label(self.trial4_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_4.grid(row=self.trial4_row+1, column=0, padx=5, pady=5)

        self.title_4 = ttk.Label(self.trial4_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_4.grid(row=self.trial4_row+2, column=0, padx=5, pady=5) 


        # Starting 
        self.title_4 = ttk.Label(self.trial4_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_4.grid(row=self.trial4_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_4 = ttk.Label(self.trial4_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_4.grid(row=self.trial4_row+5, column=0, padx=5, pady=5)   

        self.title_4_fg = ttk.Floodgauge(self.trial4_exp_lf, bootstyle=INFO, length=750, maximum=1000, font=("Calibri", 12, 'bold'),)
        self.title_4_fg.grid(row=self.trial4_row+6, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame4)
        self.End_lf.place(x=700,y=740,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame5(self):
        self.is_start_trial5 = True
        # --------------------------- Frame 5 ----------------------------------------------
        self.trial5_row = 1
        # Title
        self.title = ttk.Label(self.frame5, text="                                          5. Post-motor assessment", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

         ### Description
        # add EF label frame
        self.trial5_lf = ttk.Labelframe(self.frame5,text="Preparation", bootstyle=INFO)
        self.trial5_lf.place(x=10,y=50,width=830,height=310)

        # description
        self.description_5 = ttk.Label(self.trial5_lf, text="    This section are used to check the subjects' status after completing the matching tasks. It will be  ",font=("Calibri", 11))
        self.description_5.grid(row=self.trial5_row+0, column=0, columnspan=4, padx=5, pady=5)

        self.description_5 = ttk.Label(self.trial5_lf, text="    up direction, in direction and up&in direction. The order of automatic will be up, in and up&in.",font=("Calibri", 11))
        self.description_5.grid(row=self.trial5_row+1, column=0, columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial5_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+2, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial5_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+2, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial5_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial5_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial5_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial5_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial5_row+4, column=2, padx=5, pady=5)

        # Enter the maximum MVT value

        self.trial5_MVTInfo = ["Max Shoulder Abduction (Nm)","Maximum Elbow Extension (Nm)","Maximum Elbow Flexion (N)", "Experiment Mode"]

        self.trial5_result = []
        for i in range(2):
            ttk.Label(self.trial5_lf, text=self.trial5_MVTInfo[i],font=("Calibri", 10)).grid(row=self.trial5_row+6+i, column=0, padx=5, pady=5)
            trial5 = ttk.Entry(self.trial5_lf,show=None)
            trial5.grid(row=self.trial5_row+6+i, column=1, padx=5, pady=5)
            self.trial5_result.append(trial5)

        for i in range(1):
            ttk.Label(self.trial5_lf, text=self.trial5_MVTInfo[i+2],font=("Calibri", 10)).grid(row=self.trial5_row+6+i, column=2, padx=5, pady=5)
            trial5 = ttk.Entry(self.trial5_lf,show=None)
            trial5.grid(row=self.trial5_row+6+i, column=3, padx=5, pady=5)
            self.trial5_result.append(trial5)


        ### Experimental 
        # add trial5 experimental label frame
        self.trial5_exp_lf = ttk.Labelframe(self.frame5,text="Experimental", bootstyle=INFO)
        self.trial5_exp_lf.place(x=10,y=390,width=770,height=350)

        # UP IN UP&IN
        self.title_5 = ttk.Label(self.trial5_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_5.grid(row=self.trial5_row+0, column=0, padx=5, pady=5)


        self.trial5_start_StinngVar = ttk.StringVar(self.master)
        self.trial5_start_First = 'Select a task'
        self.trial5_start_StinngVar.set(self.trial5_start_First)
        self.trial5_start_Type = ["Automatic", "Up direction", "In direction", "Up and In direction"]
        self.trial5_start_Menu = ttk.OptionMenu(self.trial5_exp_lf, self.trial5_start_StinngVar, self.trial5_start_Type[0], *self.trial5_start_Type,)
        self.trial5_start_Menu.grid(row=self.trial5_row+0,column=1, padx=5, pady=5)


        self.title_5 = ttk.Button(self.trial5_exp_lf, text="Start", command=self.trial5_Start, bootstyle=DANGER)
        self.title_5.grid(row=self.trial5_row+0,column=2, padx=5, pady=5)

        # time and force
        self.title_5 = ttk.Label(self.trial5_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_5.grid(row=self.trial5_row+1, column=0, padx=5, pady=5)

        self.title_5 = ttk.Label(self.trial5_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_5.grid(row=self.trial5_row+1, column=2, padx=5, pady=5)

        self.title_5 = ttk.Label(self.trial5_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_5.grid(row=self.trial5_row+2, column=0, padx=5, pady=5) 


        # Starting 
        self.title_5 = ttk.Label(self.trial5_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_5.grid(row=self.trial5_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_5 = ttk.Label(self.trial5_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_5.grid(row=self.trial5_row+5, column=0, padx=5, pady=5)   

        self.trial5_bar_max = 1000
        self.title_5_fg = ttk.Floodgauge(self.trial5_exp_lf, bootstyle=INFO, length=750, maximum=self.trial5_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_5_fg.grid(row=self.trial5_row+6, column=0, columnspan=5, padx=5, pady=3)  

    def set_frame6(self):
        self.is_start_trial6 = True
        self.title = ttk.Label(self.frame6, text="                                             6. Working Memory trials", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial6_row = 0

        # bool
        self.trial6_count = 0

        ### Description
        # add EF label frame
        self.trial6_lf = ttk.Labelframe(self.frame6,text="Preparation", bootstyle=INFO)
        self.trial6_lf.place(x=10,y=50,width=770,height=220)

        # description
        self.description_6 = ttk.Label(self.trial6_lf, text="Torque Control - at the very end, holding the target torque for 10s.",font=("Calibri", 11))
        self.description_6.grid(row=self.trial6_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_6 = ttk.Label(self.trial6_lf, text="        The experiment will ouput 'Up', 'In', 'Out' and 'Down' sounds",font=("Calibri", 11))
        self.description_6.grid(row=self.trial6_row+2, column=0, columnspan=2, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial6_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial6_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial6_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial6_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+4, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial6_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+5, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial6_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial6_row+5, column=2, padx=5, pady=5)
    
        ### Experimental 
        # add trial6 experimental label frame
        self.trial6_exp_lf = ttk.Labelframe(self.frame6,text="Experimental", bootstyle=INFO)
        self.trial6_exp_lf.place(x=10,y=300,width=770,height=350)
    
        # UP DOWN IN OUT
        self.title_6 = ttk.Label(self.trial6_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_6.grid(row=self.trial6_row+0, column=0, padx=5, pady=5)

        self.trial6_start_StinngVar = ttk.StringVar(self.master)
        self.trial6_start_First = 'Select a task'
        self.trial6_start_StinngVar.set(self.trial6_start_First)
        self.trial6_start_Type = ["Automatic", "Set 1", "Set 2", "Set 3", "Set 4"]
        self.trial6_start_Menu = ttk.OptionMenu(self.trial6_exp_lf, self.trial6_start_StinngVar, self.trial6_start_Type[0], *self.trial6_start_Type,)
        self.trial6_start_Menu.grid(row=self.trial6_row+0,column=1, padx=5, pady=5)

        self.title_6 = ttk.Button(self.trial6_exp_lf, text="Start", command=self.trial6_Start, bootstyle=DANGER)
        self.title_6.grid(row=self.trial6_row+0,column=2, padx=5, pady=5)

        self.title_6 = ttk.Button(self.trial6_exp_lf, text="Stop", command=self.trial6_Stop, bootstyle=DANGER)
        self.title_6.grid(row=self.trial6_row+0,column=3, padx=5, pady=5)

        # trial and status
        self.title_6 = ttk.Label(self.trial6_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_6.grid(row=self.trial6_row+1, column=0, padx=5, pady=5)

        self.title_6 = ttk.Label(self.trial6_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_6.grid(row=self.trial6_row+1, column=2, padx=5, pady=5)

        self.title_6 = ttk.Label(self.trial6_exp_lf, text="Next Status: ",font=("Calibri", 12, "bold"))
        self.title_6.grid(row=self.trial6_row+2, column=2, padx=5, pady=5)

        # Starting 
        self.title_6 = ttk.Label(self.trial6_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_6.grid(row=self.trial6_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_6 = ttk.Label(self.trial6_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_6.grid(row=self.trial6_row+5, column=0, padx=5, pady=5)   

        self.title_6_fg = ttk.Floodgauge(self.trial6_exp_lf, bootstyle=INFO, length=750, maximum=1000, font=("Calibri", 12, 'bold'),)
        self.title_6_fg.grid(row=self.trial6_row+6, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame6)
        self.End_lf.place(x=700,y=740,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)



    # Helper functions
    def transmit(self, header, information):
        self.data_queue.put((header, information))

    def showError(self):
        print("retrycancel: ",Messagebox.show_error(title='Oh no', message="All fields should be filled"))

    # close the window
    def close(self):
        self.transmit("Close", "close")

    def pause(self):
        self.transmit("Pause", "pause")
        self.pause_bar = True
        print("Pause")

    def trial_iteration(self):
    
        # add new label
        if not self.in_queue.empty():
            self.Ext_queue = self.in_queue.get_nowait()

        self.after(100, self.trial_iteration)

    def calculate_bar(self, mode):
        # Time
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

        # Trial 1
        if mode == "EMG":
            # bar time
            start = Starting_time+0.6              # 0 - 1.8
            test_time = start+5.0                 # 1.8 - 4.8        
            end = test_time+Ending_time  
            
            # insert bar time into the matrix
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((test_time/end)*718+12))

        elif mode == "trial1_in&out&down":
            # bar time
            start = Starting_time+0.6              
            in_time = start+In_time+5.0                 
            relax = in_time+Relax_time+0.5           
            end = relax+Ending_time  
            
            # insert bar time into the matrix
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((relax/end)*718+12))

        # Trial 2
        elif mode == "trial2_up":
            # bar time
            start = Starting_time+0.6              # 0 - 1.8
            up = start+Up_time+2.0                 # 1.8 - 4.8
            hold = up+Hold_time+1.5                # 4.8 - 7.3
            relax = hold+Relax_time+0.5            # 7.3 - 9.1
            end = relax+Ending_time                # 9.1 - 10.1
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((up/end)*718+12))
            bar_matrix.append(int((hold/end)*718+12))
            bar_matrix.append(int((relax/end)*718+12))
        
        elif mode == "trial2_in":
            # bar time
            start = Starting_time+0.6              # 0 - 1.8
            in_time = start+In_time+2.0                 # 1.8 - 4.8
            hold = in_time+Hold_time+1.5                # 4.8 - 7.3
            relax_1 = hold+Relax_time+0.5            # 7.3 - 9.1
            out = relax_1+Out_time+0.2
            relax_2 = out+Relax_time+0.5           
            end = relax_2+Ending_time  
            
            # insert bar time into the matrix
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((hold/end)*718+12))
            bar_matrix.append(int((relax_1/end)*718+12))
            bar_matrix.append(int((out/end)*718+12))
            bar_matrix.append(int((relax_2/end)*718+12))

        elif mode == "trial2_upin":
            # bar time
            start = Starting_time+0.6              
            up = start+Up_time+2.0                 
            hold_1 = up+Hold_time+1.5               
            in_time = hold_1+In_time+2.0
            hold_2 = in_time+Hold_time+1.5                
            relax_1 = hold_2+Relax_time+0.5  
            out = relax_1+Out_time+0.2
            relax_2 = out+Relax_time+0.5           
            end = relax_2+Ending_time                
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((up/end)*718+12))
            bar_matrix.append(int((hold_1/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((hold_2/end)*718+12))
            bar_matrix.append(int((relax_1/end)*718+12))
            bar_matrix.append(int((out/end)*718+12))
            bar_matrix.append(int((relax_2/end)*718+12))

        # Trial 3
        elif mode == "trial3":
            # bar time
            start = Starting_time+0.5              
            up = start+Up_time+2.2                 
            hold_1 = up+Hold_time+1.0 # Hold for one second              
            in_time = hold_1+In_time+2.2
            hold_2 = in_time+Hold_time+2.0               
            relax_1 = hold_2+Relax_time+6
            match = relax_1+Match_time+2
            hold_3 = match+Hold_time+1
            relax_2 = hold_3+Relax_time+0.5
            out = relax_2+Out_time+0.2
            relax_3 = out+Relax_time+0.5           
            end = relax_3+Ending_time                
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((up/end)*718+12))
            bar_matrix.append(int((hold_1/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((hold_2/end)*718+12))
            bar_matrix.append(int((relax_1/end)*718+12))
            bar_matrix.append(int((match/end)*718+12))
            bar_matrix.append(int((hold_3/end)*718+12))
            bar_matrix.append(int((relax_2/end)*718+12))
            bar_matrix.append(int((out/end)*718+12))
            bar_matrix.append(int((relax_3/end)*718+12)) 

        elif mode == "trial6":
            # bar time
            # in    out   up    down
            start = Starting_time+0.6            
            in_time = start+In_time+0.5                 
            out = in_time+Out_time+0.5
            up = out+Up_time+0.5 
            down = up+Down_time+0.5                          
            end = down+Ending_time              
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((out/end)*718+12))
            bar_matrix.append(int((up/end)*718+12))
            bar_matrix.append(int((down/end)*718+12))

        return bar_matrix    

    # ---------------------------------------functions in frame 0---------------------------------------

    # check if all the data has been submitted in the frame 0
    def checkFields_frame0(self):
        result = []
        for i in range(4):
            result.append(self.subject_result[i].get())
        for i in range(4):
            result.append(self.jaco_result[i].get())
        for i in result:
            if i == '':
                self.showError()
                break      
    
    def trial0_start(self):
        # save the data
        trial0_saved = []
        trial0_header = []
        for i in range(8):
            trial0_header.append(self.subjectInfo[i])

        # save the subject information data
        for i in range(4):
            trial0_saved.append(self.subject_result[i].get())

        trial0_saved.append(self.genders_StinngVar.get())
        trial0_saved.append(self.diabetes_StinngVar.get())
        trial0_saved.append(self.domArm_StinngVar.get())
        trial0_saved.append(self.TestArm_StinngVar.get())
        
        # reset the subject saved list
        disabtes = trial0_saved.pop(2)
        subject_type = trial0_saved.pop(2)
        trial0_saved.insert(3, disabtes)
        trial0_saved.insert(5, subject_type)

        # save the Jacobian information data
        for i in range(4):
            trial0_header.append(self.jacobInfo[i])
            trial0_saved.append(self.jaco_result[i].get())

        # make sure all data has been input
        is_correct = True
        if self.checkFields_frame0():
            is_correct = False
        
        # if all data has been submitted correctly
        if is_correct:
            self.label1 = ttk.Label(self.sub_lf, text='Successfully Input !', bootstyle=SUCCESS)
            self.label1.grid(row=8, column=4)

            trial0_Final = dict(zip(trial0_header, trial0_saved))
            self.transmit("Trial0", trial0_Final)

            print(trial0_Final)

            for i in [self.trial2_lf, self.trial3_lf, self.trial4_lf, self.trial5_lf, self.trial6_lf]:
    
                self.input_subj = ttk.Label(i, text=trial0_saved[0],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+2, column=1, padx=5, pady=5)              

                self.input_subj = ttk.Label(i, text=trial0_saved[1],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)   

                self.input_subj = ttk.Label(i, text=trial0_saved[2],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+3, column=1, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[3],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+3, column=3, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[5],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+4, column=1, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[7],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+4, column=3, padx=5, pady=5)  

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[0],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+4, column=1, padx=5, pady=5)              

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[1],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+4, column=3, padx=5, pady=5)   

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[2],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+5, column=1, padx=5, pady=5) 

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[3],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+5, column=3, padx=5, pady=5) 

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[5],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+6, column=1, padx=5, pady=5) 

            self.input_subj = ttk.Label(self.trial1_lf, text=trial0_saved[7],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_subj.grid(row=self.trial2_row+6, column=3, padx=5, pady=5)  

    def trial0_reset(self):
        self.label1 = ttk.Label(self.sub_lf, text='Need to develop!', bootstyle=SUCCESS)
        self.label1.grid(row=7, column=4)
    # ---------------------------------------functions in frame 1---------------------------------------

    def trial1_Start(self):
        self.pause_bar = False
        self.stop_bar = False
        # save the data
        trial1_saved = []
        trial1_saved.append(self.trial1_start_StinngVar.get())
        trial1_saved.append(self.trial1_input.get())

        trial1_header = []
        trial1_header.append('Experiment Mode')
        trial1_header.append('Initial Value')

        # make sure all data has been input
        is_correct = True
        if self.trial1_start_StinngVar.get() == "Set 6" or self.trial1_start_StinngVar.get() == "Set 7" or self.trial1_start_StinngVar.get() == "Set 8":  
            if self.trial1_input.get() == "":
                self.showError()
                is_correct = False
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:
            if self.trial_finish or self.is_start_trial1:
                maxFinal = dict(zip(trial1_header, trial1_saved))
                self.transmit("Trial1", maxFinal)
                print(maxFinal)
                self.is_start_trial1 = False


            if self.trial1_start_StinngVar.get() == "Set 1" or self.trial1_start_StinngVar.get() == "Set 2" or self.trial1_start_StinngVar.get() == "Set 3" or self.trial1_start_StinngVar.get() == "Set 4" or self.trial1_start_StinngVar.get() == "Set 5":
                # delete the old bar
                self.delete_trial1_label()

                # add label on the bar
                self.add_trial1_EMG()  

                # start the progressive bar
                self.start_trial1_bar(170)
            
            elif self.trial1_start_StinngVar.get() == "Set 6":
                # delete the old bar
                self.delete_trial1_label()

                # add label on the bar
                self.add_trial1_in()

                # start the progressive bar
                self.start_trial1_bar(210)

            elif self.trial1_start_StinngVar.get() == "Set 7":
                # delete the old bar
                self.delete_trial1_label()

                # add label on the bar
                self.add_trial1_out()

                # start the progressive bar
                self.start_trial1_bar(210)

            elif self.trial1_start_StinngVar.get() == "Set 8":
                # delete the old bar
                self.delete_trial1_label()

                # add label on the bar
                self.add_trial1_up()

                # start the progressive bar
                self.start_trial1_bar(210)

    def trial1_toggle(self):
        """Toggle the start and pause button."""
        if self.running.get():
            self.running.set(False)
            self.trial1_button.grid_forget()
            self.pause()
            self.trial1_button = ttk.Button(self.trial1_exp_lf, text="Start", command=self.trial1_toggle, bootstyle=DANGER)
            self.trial1_button.grid(row=self.trial1_row+1,column=2, padx=5, pady=5)
        else:
            self.running.set(True)
            self.trial1_button.grid_forget()
            self.trial1_button = ttk.Button(self.trial1_exp_lf, text="Pause", command=self.trial1_toggle, bootstyle=WARNING)
            self.trial1_button.grid(row=self.trial1_row+1,column=2, padx=5, pady=5)
            self.trial1_Start()

    def trial1_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.min_value = 0
        self.title_1_fg.grid_forget()
        self.title_1_fg = ttk.Floodgauge(self.trial1_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_1_fg.grid(row=self.trial1_row+8, column=0, columnspan=5, padx=5, pady=3)  
        self.title_1_fg['value'] = 0

    def start_trial1_bar(self, max):
        # start the progressive bar
        self.title_1_fg['maximum'] = max
        self.title_1_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False

        for i in range(self.min, max):

            if self.stop_bar:
                self.title_1_fg['value'] = 0
                self.trial1_exp_lf.update()
                time.sleep(0.05)
                print("Stop")
            else:
                if self.pause_bar:
                    if not is_get_min:
                        self.min_value = i
                        is_get_min = True
                    self.title_1_fg.stop()
                    self.has_started_bar = True
                    self.trial_finish = False
                else:
                    self.title_1_fg['value'] = i+1
                    self.trial1_exp_lf.update()
                    time.sleep(0.05) 
                
            if self.title_1_fg['value'] == max:
                self.trial_finish = True
                self.trial1_stop()
        
        
    def trial1_Record(self):
        # subscribe the data from experiment protocol
        if not self.in_queue.empty():
            self.Ext_queue = self.in_queue.get_nowait()

        self.count_max += 1
        if self.count_max%4 == 1:
            if self.count_max > 1:
                self.trial1_record_1.forget()
                self.trial1_record_1 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_1.grid(row=self.trial1_row+2,column=1, padx=5, pady=5)
            else:
                self.trial1_record_1 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_1.grid(row=self.trial1_row+2,column=1, padx=5, pady=5)
        elif self.count_max%4  == 2:
            if self.count_max > 2:
                self.trial1_record_2.forget()
                self.trial1_record_2 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_2.grid(row=self.trial1_row+2,column=2, columnspan=2, padx=5, pady=5)
            else:
                self.trial1_record_2 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_2.grid(row=self.trial1_row+2,column=2, columnspan=2, padx=5, pady=5)
        elif self.count_max%4  == 3:
            if self.count_max > 3:
                self.trial1_record_3.forget()
                self.trial1_record_3 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_3.grid(row=self.trial1_row+3,column=1, padx=5, pady=5)
            else:
                self.trial1_record_3 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_3.grid(row=self.trial1_row+3,column=1, padx=5, pady=5)
        elif self.count_max%4  == 0:
            if self.count_max > 4:
                self.trial1_record_4.forget()
                self.trial1_record_4 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_4.grid(row=self.trial1_row+3,column=2, columnspan=2, padx=5, pady=5)
            else:
                self.trial1_record_4 = ttk.Label(self.trial1_exp_lf, text=str((list(self.Ext_queue)[4])+' Trial '+ str(self.count_max) + '  MVT: '+str(round(float(list(self.Ext_queue)[3]), 7))), bootstyle=SUCCESS)
                self.trial1_record_4.grid(row=self.trial1_row+3,column=2, columnspan=2, padx=5, pady=5)

    def add_trial1_EMG(self):
        self.trial1_start_pos = self.calculate_bar("EMG")

        self.trial1_EMG_1 = ttk.Label(self.frame1, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial1_EMG_1.place(x=self.trial1_start_pos[0],y=645)  

        self.trial1_EMG_2 = ttk.Label(self.frame1, text="| Test ",font=("Calibri", 10, "bold"))
        self.trial1_EMG_2.place(x=self.trial1_start_pos[1],y=645) 

        self.trial1_EMG_3 = ttk.Label(self.frame1, text="| End ",font=("Calibri", 10, "bold"))
        self.trial1_EMG_3.place(x=self.trial1_start_pos[2],y=645) 

        self.is_trial1_EMG = True
    
    def delete_trial1_EMG(self):
        self.trial1_EMG_1.place_forget()
        self.trial1_EMG_2.place_forget()
        self.trial1_EMG_3.place_forget()

    def add_trial1_in(self):
        self.trial1_start_pos = self.calculate_bar("trial1_in&out&down")

        self.trial1_in_1 = ttk.Label(self.frame1, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial1_in_1.place(x=self.trial1_start_pos[0],y=645)  

        self.trial1_in_2 = ttk.Label(self.frame1, text="| In ",font=("Calibri", 10, "bold"))
        self.trial1_in_2.place(x=self.trial1_start_pos[1],y=645) 

        self.trial1_in_3 = ttk.Label(self.frame1, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial1_in_3.place(x=self.trial1_start_pos[2],y=645) 

        self.trial1_in_4 = ttk.Label(self.frame1, text="| End ",font=("Calibri", 10, "bold"))
        self.trial1_in_4.place(x=self.trial1_start_pos[3],y=645) 

        self.is_trial1_in = True
    
    def delete_trial1_in(self):
        self.trial1_in_1.place_forget()
        self.trial1_in_2.place_forget()
        self.trial1_in_3.place_forget()
        self.trial1_in_4.place_forget()

    def add_trial1_out(self):
        self.trial1_start_pos = self.calculate_bar("trial1_in&out&down")

        self.trial1_out_1 = ttk.Label(self.frame1, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial1_out_1.place(x=self.trial1_start_pos[0],y=645)  

        self.trial1_out_2 = ttk.Label(self.frame1, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial1_out_2.place(x=self.trial1_start_pos[1],y=645) 

        self.trial1_out_3 = ttk.Label(self.frame1, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial1_out_3.place(x=self.trial1_start_pos[2],y=645) 

        self.trial1_out_4 = ttk.Label(self.frame1, text="| End ",font=("Calibri", 10, "bold"))
        self.trial1_out_4.place(x=self.trial1_start_pos[3],y=645) 

        self.is_trial1_out = True

    def delete_trial1_out(self):
        self.trial1_out_1.place_forget()
        self.trial1_out_2.place_forget()
        self.trial1_out_3.place_forget()
        self.trial1_out_4.place_forget()

    def add_trial1_up(self):
        self.trial1_start_pos = self.calculate_bar("trial1_in&out&down")

        self.trial1_up_1 = ttk.Label(self.frame1, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial1_up_1.place(x=self.trial1_start_pos[0],y=645)  

        self.trial1_up_2 = ttk.Label(self.frame1, text="| Up ",font=("Calibri", 10, "bold"))
        self.trial1_up_2.place(x=self.trial1_start_pos[1],y=645) 

        self.trial1_up_3 = ttk.Label(self.frame1, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial1_up_3.place(x=self.trial1_start_pos[2],y=645) 

        self.trial1_up_4 = ttk.Label(self.frame1, text="| End ",font=("Calibri", 10, "bold"))
        self.trial1_up_4.place(x=self.trial1_start_pos[3],y=645) 

        self.is_trial1_up = True
    
    def delete_trial1_up(self):
        self.trial1_up_1.place_forget()
        self.trial1_up_2.place_forget()
        self.trial1_up_3.place_forget()
        self.trial1_up_4.place_forget()

    def delete_trial1_label(self):
        if self.is_trial1_EMG:
            self.delete_trial1_EMG()
        elif self.is_trial1_in:
            self.delete_trial1_in()
        elif self.is_trial1_out:
            self.delete_trial1_out()
        elif self.is_trial1_up:
            self.delete_trial1_up()


    # ---------------------------------------functions in frame 2, Trial 2---------------------------------------
    def trial2_Start(self):
        self.pause_bar = False
        self.stop_bar = False

        # save the data
        trial2_saved = []
        for i in range(3):
            trial2_saved.append(self.trial2_result[i].get())

        # make sure all data has been input
        is_correct = True
        for i in trial2_saved:
            if i == '':
                self.showError()
                is_correct = False
                break
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:

            if self.trial2_start_StinngVar.get() == "Up direction":

                # ouput the data to the experiment protocol
                trial2_saved.append(self.trial2_start_StinngVar.get())
                trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                if self.trial_finish or self.is_start_trial2:
                    self.transmit("Trial2", trial2_maxFinal)
                    self.is_start_trial2 = False
                    print(trial2_maxFinal)

                # delete the old bar
                self.delete_trial2_label()

                # add label on the bar
                self.add_trial2_up()  

                # start the progressive bar
                self.start_trial2_bar(200)

            elif self.trial2_start_StinngVar.get() == "In direction":

                # ouput the data to the experiment protocol
                trial2_saved.append(self.trial2_start_StinngVar.get())
                trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                if self.trial_finish or self.is_start_trial2:
                    self.transmit("Trial2", trial2_maxFinal)
                    self.is_start_trial2 = False
                    print(trial2_maxFinal)

                # delete the old bar
                self.delete_trial2_label()

                # add label on the bar
                self.add_trial2_in()  

                # start the progressive bar
                self.start_trial2_bar(262)

            elif self.trial2_start_StinngVar.get() == "Up and In direction":

                # ouput the data to the experiment protocol
                trial2_saved.append(self.trial2_start_StinngVar.get())
                trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                if self.trial_finish or self.is_start_trial2:
                    self.transmit("Trial2", trial2_maxFinal)
                    self.is_start_trial2 = False
                    print(trial2_maxFinal)

                # delete the old bar
                self.delete_trial2_label()

                # add label on the bar
                self.add_trial2_upin()   

                # start the progressive bar
                self.start_trial2_bar(380) # 18.6 second  1 second to 20
            
            elif self.trial2_start_StinngVar.get() == "Automatic":

                # -----------------------Up direction-----------------------
                if not self.pause_bar:
                    trial2_saved.append("Up direction")
                    trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                    if self.trial_finish or self.is_start_trial2:
                        self.transmit("Trial2", trial2_maxFinal)
                        self.is_start_trial2 = False
                        print(trial2_maxFinal)

                    # delete the old bar
                    self.delete_trial2_label()

                    # add label on the bar
                    self.add_trial2_up()  

                    # start the progressive bar
                    self.start_trial2_bar(200)

                    time.sleep(2.0)

                # -----------------------In direction-----------------------
                if not self.pause_bar:
                    trial2_saved.pop()
                    trial2_saved.append("In direction")
                    trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                    if self.trial_finish or self.is_start_trial2:
                        self.transmit("Trial2", trial2_maxFinal)
                        self.is_start_trial2 = False
                        print(trial2_maxFinal)

                    # delete the up bar
                    self.delete_trial2_up()

                    # add label on the bar
                    self.add_trial2_in()  

                    # start the progressive bar
                    self.start_trial2_bar(262)
                    
                    time.sleep(2.0)

                # -----------------------Up and In direction-----------------------
                if not self.pause_bar:
                    trial2_saved.pop()
                    trial2_saved.append("Up and In direction")
                    trial2_maxFinal = dict(zip(self.trial2_MVTInfo, trial2_saved))
                    if self.trial_finish or self.is_start_trial2:
                        self.transmit("Trial2", trial2_maxFinal)
                        self.is_start_trial2 = False
                        print(trial2_maxFinal)

                    # delete the in bar
                    self.delete_trial2_in()

                    # add label on the bar
                    self.add_trial2_upin()  

                    # start the progressive bar
                    self.start_trial2_bar(380)

    def trial2_toggle(self):
        """Toggle the start and pause button."""
        if self.running.get():
            self.running.set(False)
            self.trial2_button.grid_forget()
            self.pause()
            self.trial2_button = ttk.Button(self.trial2_exp_lf, text="Start", command=self.trial2_toggle, bootstyle=DANGER)
            self.trial2_button.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)
        else:
            self.running.set(True)
            self.trial2_button.grid_forget()
            self.trial2_button = ttk.Button(self.trial2_exp_lf, text="Pause", command=self.trial2_toggle, bootstyle=WARNING)
            self.trial2_button.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)
            self.trial2_Start()

    def trial2_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.min_value = 0
        self.title_2_fg.grid_forget()
        self.title_2_fg = ttk.Floodgauge(self.trial2_exp_lf, bootstyle=INFO, length=750, maximum=self.trial2_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_2_fg.grid(row=self.trial2_row+6, column=0, columnspan=5, padx=5, pady=3)  
        self.title_2_fg['value'] = 0
        self.transmit("Stop", "stop")

    def start_trial2_bar(self, max):
        # start the progressive bar
        self.title_2_fg['maximum'] = max
        self.title_2_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False

        for i in range(self.min, max):
            
            # stop the experiment
            if self.stop_bar:
                self.title_2_fg['value'] = 0
                self.trial2_exp_lf.update()
                time.sleep(0.05)
            else:
                # Pause the experiment
                if self.pause_bar:
                    if not is_get_min:
                        self.min_value = i
                        is_get_min = True
                    self.title_2_fg.stop()
                    self.has_started_bar = True
                    self.trial_finish = False
                # Continue the experiment
                else:
                    self.title_2_fg['value'] = i+1
                    self.trial2_exp_lf.update()
                    time.sleep(0.05) 
                
            if self.title_2_fg['value'] == max:
                self.trial_finish = True
                if self.trial2_start_StinngVar.get() != "Automatic":
                    self.trial2_stop()

    def add_trial2_up(self):
        # calculate trial2 distance of label
        self.trial2_start_pos = self.calculate_bar('trial2_up')

        self.trial2_up_1 = ttk.Label(self.frame2, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_up_1.place(x=self.trial2_start_pos[0],y=585)  

        self.trial2_up_2 = ttk.Label(self.frame2, text="| up ",font=("Calibri", 10, "bold"))
        self.trial2_up_2.place(x=self.trial2_start_pos[1],y=585)  

        self.trial2_up_3 = ttk.Label(self.frame2, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_up_3.place(x=self.trial2_start_pos[2],y=585)  

        self.trial2_up_4 = ttk.Label(self.frame2, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_up_4.place(x=self.trial2_start_pos[3],y=585) 

        self.trial2_up_5 = ttk.Label(self.frame2, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_up_5.place(x=self.trial2_start_pos[4],y=585) 

        self.title_2_trial = ttk.Label(self.trial2_exp_lf, text="Up direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_trial.grid(row=self.trial2_row+1, column=1, padx=5, pady=5)

        self.title_2_status_1 = ttk.Label(self.trial2_exp_lf, text="25 % MVT_EL: "+str(float(self.trial2_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

        self.title_2_status_2 = ttk.Label(self.trial2_exp_lf, text="20 % MVT_SH: "+str(float(self.trial2_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 

        self.is_trial2_up = True

    def delete_trial2_up(self):
        self.trial2_up_1.place_forget()
        self.trial2_up_2.place_forget()
        self.trial2_up_3.place_forget()
        self.trial2_up_4.place_forget()
        self.trial2_up_5.place_forget()
        self.title_2_trial.grid_forget()
        self.title_2_status_1.grid_forget()
        self.title_2_status_2.grid_forget()

        self.is_trial2_up = False

    def add_trial2_in(self):
        # calculate trial2 distance of label
        self.trial2_start_pos = self.calculate_bar('trial2_in')

        self.trial2_in_1 = ttk.Label(self.frame2, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_in_1.place(x=self.trial2_start_pos[0],y=585)  

        self.trial2_in_2 = ttk.Label(self.frame2, text="| in ",font=("Calibri", 10, "bold"))
        self.trial2_in_2.place(x=self.trial2_start_pos[1],y=585)  

        self.trial2_in_3 = ttk.Label(self.frame2, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_in_3.place(x=self.trial2_start_pos[2],y=585)  

        self.trial2_in_4 = ttk.Label(self.frame2, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_in_4.place(x=self.trial2_start_pos[3],y=585) 

        self.trial2_in_5 = ttk.Label(self.frame2, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial2_in_5.place(x=self.trial2_start_pos[4],y=585) 

        self.trial2_in_6 = ttk.Label(self.frame2, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_in_6.place(x=self.trial2_start_pos[5],y=585) 

        self.trial2_in_7 = ttk.Label(self.frame2, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_in_7.place(x=self.trial2_start_pos[6],y=585) 

        self.title_2_trial = ttk.Label(self.trial2_exp_lf, text="In direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_trial.grid(row=self.trial2_row+1, column=1, padx=5, pady=5)

        self.title_2_status_1 = ttk.Label(self.trial2_exp_lf, text="25 % MVT_EL: "+str(float(self.trial2_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

        self.title_2_status_2 = ttk.Label(self.trial2_exp_lf, text="20 % MVT_SH: "+str(float(self.trial2_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 

        self.is_trial2_in = True

    def delete_trial2_in(self):
        self.trial2_in_1.place_forget()
        self.trial2_in_2.place_forget()
        self.trial2_in_3.place_forget()
        self.trial2_in_4.place_forget()
        self.trial2_in_5.place_forget()
        self.trial2_in_6.place_forget()
        self.trial2_in_7.place_forget()
        self.title_2_trial.grid_forget()
        self.title_2_status_1.grid_forget()
        self.title_2_status_2.grid_forget()
        
        self.is_trial2_in = False

    def add_trial2_upin(self):
        # calculate trial2 distance of label
        self.trial2_start_pos = self.calculate_bar('trial2_upin')

        self.trial2_upin_1 = ttk.Label(self.frame2, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_upin_1.place(x=self.trial2_start_pos[0],y=585)  

        self.trial2_upin_2 = ttk.Label(self.frame2, text="| up ",font=("Calibri", 10, "bold"))
        self.trial2_upin_2.place(x=self.trial2_start_pos[1],y=585)  

        self.trial2_upin_3 = ttk.Label(self.frame2, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_upin_3.place(x=self.trial2_start_pos[2],y=585)  

        self.trial2_upin_4 = ttk.Label(self.frame2, text="| in ",font=("Calibri", 10, "bold"))
        self.trial2_upin_4.place(x=self.trial2_start_pos[3],y=585)  

        self.trial2_upin_5 = ttk.Label(self.frame2, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_upin_5.place(x=self.trial2_start_pos[4],y=585)  

        self.trial2_upin_6 = ttk.Label(self.frame2, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_upin_6.place(x=self.trial2_start_pos[5],y=585) 

        self.trial2_upin_7 = ttk.Label(self.frame2, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial2_upin_7.place(x=self.trial2_start_pos[6],y=585) 

        self.trial2_upin_8 = ttk.Label(self.frame2, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_upin_8.place(x=self.trial2_start_pos[7],y=585) 

        self.trial2_upin_9 = ttk.Label(self.frame2, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_upin_9.place(x=self.trial2_start_pos[8],y=585) 

        self.title_2_trial = ttk.Label(self.trial2_exp_lf, text="Up and In direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_trial.grid(row=self.trial2_row+1, column=1, padx=5, pady=5)

        self.title_2_status_1 = ttk.Label(self.trial2_exp_lf, text="25 % MVT_EL: "+str(float(self.trial2_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

        self.title_2_status_2 = ttk.Label(self.trial2_exp_lf, text="20 % MVT_SH: "+str(float(self.trial2_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_2_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)  


        self.is_trial2_upin = True

    def delete_trial2_upin(self):
        self.trial2_upin_1.place_forget()
        self.trial2_upin_2.place_forget()
        self.trial2_upin_3.place_forget()
        self.trial2_upin_4.place_forget()
        self.trial2_upin_5.place_forget()
        self.trial2_upin_6.place_forget()
        self.trial2_upin_7.place_forget()
        self.trial2_upin_8.place_forget()
        self.trial2_upin_9.place_forget()
        self.title_2_trial.grid_forget()
        self.title_2_status_1.grid_forget()
        self.title_2_status_2.grid_forget()

        self.is_trial2_upin = False

    def delete_trial2_label(self):
        if self.is_trial2_up:
            self.delete_trial2_up()
        elif self.is_trial2_in:
            self.delete_trial2_in()
        elif self.is_trial2_upin:
            self.delete_trial2_upin()

    # ---------------------------------------functions in frame 3---------------------------------------

    def trial3_Start(self):
        self.pause_bar = False
        self.stop_bar = False

        # save the data
        trial3_saved = []
        for i in range(3):
            trial3_saved.append(self.trial3_result[i].get())
        
        # make sure all data has been input
        is_correct = True
        for i in trial3_saved:
            if i == '':
                self.showError()
                is_correct = False
                break
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly    
        if is_correct:

            self.add_trial3_bar()
            if self.trial3_start_StinngVar_1.get() == "Automatic" and self.trial3_start_StinngVar_2.get() == "Auto":
                for set_count in range(1,4):
                    for trial_count in range(1,11):
                        if self.trial3_break:
                            break

                        trial3_saved.append("Set " + str(set_count))
                        trial3_saved.append("Trial " + str(trial_count))

                        trial3_maxFinal = dict(zip(self.trial3_MVTInfo, trial3_saved))
                        if self.trial_finish or self.is_start_trial3:
                            self.transmit("Trial3", trial3_maxFinal)
                            self.is_start_trial2 = False
                            print(trial3_maxFinal)

                        # delete the old bar
                        self.delete_trial3_label()

                        # add label on the bar
                        self.add_trial3_status(set_count,trial_count)  
                        
                        # start the progressive bar
                        self.start_trial3_bar(560)

            elif self.trial3_start_StinngVar_1.get()[0] == "S" and self.trial3_start_StinngVar_2.get()[0] == "T":
                
                trial3_saved.append(self.trial3_start_StinngVar_1.get())
                trial3_saved.append(self.trial3_start_StinngVar_2.get())

                trial3_maxFinal = dict(zip(self.trial3_MVTInfo, trial3_saved))
                if self.trial_finish or self.is_start_trial3:
                    self.transmit("Trial3", trial3_maxFinal)
                    self.is_start_trial2 = False
                    print(trial3_maxFinal)

                self.trial3_break = True
                # delete the old bar
                self.delete_trial3_label()

                # add label on the bar
                self.add_trial3_status(int(self.trial3_start_StinngVar_1.get()[4]),int(self.trial3_start_StinngVar_2.get()[6]))  

                # start the progressive bar
                self.start_trial3_bar(560)      
            else:
                print("retrycancel: ",Messagebox.show_error(title='Oh no', message="Please choose correct task!"))      

    def trial3_toggle(self):
        """Toggle the start and pause button."""
        if self.running.get():
            self.running.set(False)
            self.trial3_button.grid_forget()
            self.pause()
            self.trial3_button = ttk.Button(self.trial3_exp_lf, text="Start", command=self.trial3_toggle, bootstyle=DANGER)
            self.trial3_button.grid(row=self.trial3_row+0,column=3, padx=5, pady=5)
        else:
            self.running.set(True)
            self.trial3_button.grid_forget()
            self.trial3_button = ttk.Button(self.trial3_exp_lf, text="Pause", command=self.trial3_toggle, bootstyle=WARNING)
            self.trial3_button.grid(row=self.trial3_row+0,column=3, padx=5, pady=5)
            self.trial3_Start()
    
    def fixed_toggle_1(self):
        """Toggle the fixed and unfixed button."""
        if self.running_1.get():
            self.running_1.set(False)
            self.trial3_button_3.grid_forget()
            self.trial3_button_3 = ttk.Button(self.trial3_exp_lf, text="Fixed", command=self.fixed_toggle_1, bootstyle=INFO)
            self.trial3_button_3.grid(row=self.trial3_row+1,column=1, padx=5, pady=5)
            # self.pause()
            print("1")
        else:
            self.running_1.set(True)
            self.trial3_button_3.grid_forget()
            self.trial3_button_3 = ttk.Button(self.trial3_exp_lf, text="Un fixed", command=self.fixed_toggle_1, bootstyle=WARNING)
            self.trial3_button_3.grid(row=self.trial3_row+1,column=1, padx=5, pady=5)
            print("2")
            # self.trial3_Start()

    def fixed_toggle_2(self):
        """Toggle the fixed and unfixed button."""
        if self.running_2.get():
            self.running_2.set(False)
            self.trial3_button_4.grid_forget()
            self.trial3_button_4 = ttk.Button(self.trial3_exp_lf, text="Fixed", command=self.fixed_toggle_2, bootstyle=INFO)
            self.trial3_button_4.grid(row=self.trial3_row+1,column=2, padx=5, pady=5)
            print("3")
            # self.pause()
        else:
            self.running_2.set(True)
            self.trial3_button_4.grid_forget()
            self.trial3_button_4 = ttk.Button(self.trial3_exp_lf, text="Un fixed", command=self.fixed_toggle_2, bootstyle=WARNING)
            self.trial3_button_4.grid(row=self.trial3_row+1,column=2, padx=5, pady=5)
            # self.trial3_Start()
            print("4")

    def start_trial3_bar(self, max):
        # start the progressive bar
        self.title_3_fg['maximum'] = max
        self.title_3_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False


        for i in range(self.min, max):

            # stop the experiment
            if self.stop_bar:
                self.title_3_fg['value'] = 0
                self.trial3_exp_lf.update()
                time.sleep(0.05)
            else:
                # Pause the experiment
                if self.pause_bar:
                    if not is_get_min:
                        self.min_value = i
                        is_get_min = True
                    self.title_3_fg.stop()
                    self.has_started_bar = True
                    self.trial_finish = False
                # Continue the experiment
                else:
                    self.title_3_fg['value'] = i+1
                    self.trial3_exp_lf.update()
                    time.sleep(0.05) 

            if self.title_3_fg['value'] == max:
                self.trial_finish = True
                if self.trial3_start_StinngVar_2.get() != "Auto":
                    self.trial3_stop()

    def trial3_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.min_value = 0
        self.title_3_fg.grid_forget()
        self.title_3_fg = ttk.Floodgauge(self.trial3_exp_lf, bootstyle=INFO, length=750, maximum=100, font=("Calibri", 12, 'bold'),)
        self.title_3_fg.grid(row=self.trial3_row+7, column=0, columnspan=5, padx=5, pady=3)  
        self.title_3_fg['value'] = 0
        self.transmit("Stop", "stop")

    def add_trial3_bar(self):
        # calculate trial2 distance of label
        self.trial3_start_pos = self.calculate_bar('trial3')
        
        self.trial3_bar_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial3_bar_1.place(x=self.trial3_start_pos[0],y=608)  

        self.trial3_bar_2 = ttk.Label(self.frame3, text="| up ",font=("Calibri", 10, "bold"))
        self.trial3_bar_2.place(x=self.trial3_start_pos[1],y=608)  

        self.trial3_bar_3 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial3_bar_3.place(x=self.trial3_start_pos[2],y=608)  

        self.trial3_bar_4 = ttk.Label(self.frame3, text="| in ",font=("Calibri", 10, "bold"))
        self.trial3_bar_4.place(x=self.trial3_start_pos[3],y=608)  

        self.trial3_bar_5 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial3_bar_5.place(x=self.trial3_start_pos[4],y=608)  

        self.trial3_bar_6 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial3_bar_6.place(x=self.trial3_start_pos[5],y=608) 

        self.trial3_bar_7 = ttk.Label(self.frame3, text="| Match ",font=("Calibri", 10, "bold"))
        self.trial3_bar_7.place(x=self.trial3_start_pos[6],y=608) 

        self.trial3_bar_8 = ttk.Label(self.frame3, text="| Hold ",font=("Calibri", 10, "bold"))
        self.trial3_bar_8.place(x=self.trial3_start_pos[7],y=608) 

        self.trial3_bar_9 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial3_bar_9.place(x=self.trial3_start_pos[8],y=608) 

        self.trial3_bar_10 = ttk.Label(self.frame3, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial3_bar_10.place(x=self.trial3_start_pos[9],y=608) 

        self.trial3_bar_11 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial3_bar_11.place(x=self.trial3_start_pos[10],y=608) 

        self.trial3_bar_12 = ttk.Label(self.frame3, text="| End ",font=("Calibri", 10, "bold"))
        self.trial3_bar_12.place(x=self.trial3_start_pos[11],y=608) 

    def add_trial3_status(self, set_number, trial_number):
        self.title_3_current_trial = ttk.Label(self.trial3_exp_lf, text="Set "+str(set_number)+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_3_current_trial.grid(row=self.trial3_row+2, column=1, padx=5, pady=5)

        self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="25 % MVT_EL: "+str(round(float(self.trial3_result[2].get())*0.25, 2))+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_3_status_1.grid(row=self.trial3_row+2, column=3, padx=5, pady=5)   

        if set_number == 1:
            percent = 10
        elif set_number == 2:
            percent = 30
        elif set_number == 3:
            percent = 50

        self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text=str(percent)+"% MVT_SH: "+str(round(float(self.trial3_result[0].get())*(percent/100), 2))+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_3_status_2.grid(row=self.trial3_row+3, column=3, padx=5, pady=5) 

        self.is_trial3_status = True

    def delete_trial3_label(self):
        if self.is_trial3_status:
            self.title_3_current_trial.grid_forget()
            self.title_3_status_1.grid_forget()
            self.title_3_status_2.grid_forget()

        self.is_trial3_status = False

    # ---------------------------------------functions in frame 4---------------------------------------

    def trial4_Start(self):
        # save the data
        trial4_saved = []
        trial4_saved.append(self.trial4_start_StinngVar.get())

        trial4_header = []
        trial4_header.append('Experiment Mode')

        is_correct = True
        # make sure all data has been input
        if self.checkFields_frame0():
            is_correct = False
        
        # if all data has been submitted correctly
        if is_correct:
            maxFinal = dict(zip(trial4_header, trial4_saved))
            self.transmit("Trial4", maxFinal)
            print(maxFinal)

            self.add_trial4_bar()

            # delete the old bar
            self.delete_trial4_label()

            # add label on the bar
            self.add_trial4_status(int(self.trial4_start_StinngVar.get()[4]))  

            # start the progressive bar
            self.start_trial4_bar(156) 

    def start_trial4_bar(self, max):
        # start the progressive bar
        self.title_4_fg['maximum'] = max
        self.title_4_fg['value'] = 0

        for i in range(max):
            self.title_4_fg['value'] = i+1
            self.trial4_exp_lf.update()
            time.sleep(0.05) 
    
    def add_trial4_bar(self):
        self.trial4_start_pos = self.calculate_bar("EMG")

        self.trial4_EMG_1 = ttk.Label(self.frame4, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial4_EMG_1.place(x=self.trial4_start_pos[0],y=495)  

        self.trial4_EMG_2 = ttk.Label(self.frame4, text="| Test ",font=("Calibri", 10, "bold"))
        self.trial4_EMG_2.place(x=self.trial4_start_pos[1],y=495) 

        self.trial4_EMG_3 = ttk.Label(self.frame4, text="| End ",font=("Calibri", 10, "bold"))
        self.trial4_EMG_3.place(x=self.trial4_start_pos[2],y=495) 

    def add_trial4_status(self, set_number):
        self.title_4_current_trial = ttk.Label(self.trial4_exp_lf, text="Set "+str(set_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_4_current_trial.grid(row=self.trial4_row+1, column=1, padx=5, pady=5)

        self.is_trial4_status = True

    def delete_trial4_label(self):
        if self.is_trial4_status:
            self.title_4_current_trial.grid_forget()

        self.is_trial4_status = False

    # ---------------------------------------functions in frame 5---------------------------------------
    def trial5_Start(self):
        # save the data
        trial5_saved = []
        for i in range(3):
            trial5_saved.append(self.trial5_result[i].get())

        # make sure all data has been input
        is_correct = True
        for i in trial5_saved:
            if i == '':
                self.showError()
                is_correct = False
                break
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:
            trial5_saved.append(self.trial5_start_StinngVar.get())
            trial5_maxFinal = dict(zip(self.trial5_MVTInfo, trial5_saved))
            self.transmit("Trial5", trial5_maxFinal)

            print(trial5_maxFinal)

            if self.trial5_start_StinngVar.get() == "Up direction":
                # delete the old bar
                self.delete_trial5_label()

                # add label on the bar
                self.add_trial5_up()  

                # start the progressive bar
                self.start_trial5_bar(150)

            elif self.trial5_start_StinngVar.get() == "In direction":
                # delete the old bar
                self.delete_trial5_label()

                # add label on the bar
                self.add_trial5_in()  

                # start the progressive bar
                self.start_trial5_bar(150)

            elif self.trial5_start_StinngVar.get() == "Up and In direction":
                # delete the old bar
                self.delete_trial5_label()

                # add label on the bar
                self.add_trial5_upin()   

                # start the progressive bar
                self.start_trial5_bar(200)
            
            elif self.trial5_start_StinngVar.get() == "Automatic":
                # delete the old bar
                self.delete_trial5_label()

                # add label on the bar
                self.add_trial5_up()  

                # start the progressive bar
                self.start_trial5_bar(150)

                # delete the up bar
                self.delete_trial5_up()

                # add label on the bar
                self.add_trial5_in()  

                # start the progressive bar
                self.start_trial5_bar(150)

                # delete the in bar
                self.delete_trial5_in()

                # add label on the bar
                self.add_trial5_upin()  

                # start the progressive bar
                self.start_trial5_bar(200)

    def start_trial5_bar(self, max):
        # start the progressive bar
        self.title_5_fg['maximum'] = max
        self.title_5_fg['value'] = 0

        for i in range(max):
            self.title_5_fg['value'] = i+1
            self.trial5_exp_lf.update()
            time.sleep(0.05) 

    def add_trial5_up(self):
        # calculate trial5 distance of label
        self.trial5_start_pos = self.calculate_bar('trial2_up')

        self.trial5_up_1 = ttk.Label(self.frame5, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial5_up_1.place(x=self.trial5_start_pos[0],y=585)  

        self.trial5_up_2 = ttk.Label(self.frame5, text="| up ",font=("Calibri", 10, "bold"))
        self.trial5_up_2.place(x=self.trial5_start_pos[1],y=585)  

        self.trial5_up_3 = ttk.Label(self.frame5, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial5_up_3.place(x=self.trial5_start_pos[2],y=585)  

        self.trial5_up_4 = ttk.Label(self.frame5, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial5_up_4.place(x=self.trial5_start_pos[3],y=585) 

        self.trial5_up_5 = ttk.Label(self.frame5, text="| End ",font=("Calibri", 10, "bold"))
        self.trial5_up_5.place(x=self.trial5_start_pos[4],y=585) 

        self.title_5_trial = ttk.Label(self.trial5_exp_lf, text="Up direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_trial.grid(row=self.trial5_row+1, column=1, padx=5, pady=5)

        self.title_5_status_1 = ttk.Label(self.trial5_exp_lf, text="25 % MVT_EL: "+str(float(self.trial5_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_1.grid(row=self.trial5_row+1, column=3, padx=5, pady=5)   

        self.title_5_status_2 = ttk.Label(self.trial5_exp_lf, text="20 % MVT_SH: "+str(float(self.trial5_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_2.grid(row=self.trial5_row+2, column=3, padx=5, pady=5) 

        self.is_trial5_up = True
   
    def delete_trial5_up(self):
        self.trial5_up_1.place_forget()
        self.trial5_up_2.place_forget()
        self.trial5_up_3.place_forget()
        self.trial5_up_4.place_forget()
        self.trial5_up_5.place_forget()
        self.title_5_trial.grid_forget()
        self.title_5_status_1.grid_forget()
        self.title_5_status_2.grid_forget()

        self.is_trial5_up = False

    def add_trial5_in(self):
        # calculate trial5 distance of label
        self.trial5_start_pos = self.calculate_bar('trial2_in')

        self.trial5_in_1 = ttk.Label(self.frame5, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial5_in_1.place(x=self.trial5_start_pos[0],y=585)  

        self.trial5_in_2 = ttk.Label(self.frame5, text="| in ",font=("Calibri", 10, "bold"))
        self.trial5_in_2.place(x=self.trial5_start_pos[1],y=585)  

        self.trial5_in_3 = ttk.Label(self.frame5, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial5_in_3.place(x=self.trial5_start_pos[2],y=585)  

        self.trial5_in_4 = ttk.Label(self.frame5, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial5_in_4.place(x=self.trial5_start_pos[3],y=585) 

        self.trial5_in_5 = ttk.Label(self.frame5, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial5_in_5.place(x=self.trial5_start_pos[4],y=585) 

        self.trial5_in_6 = ttk.Label(self.frame5, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial5_in_6.place(x=self.trial5_start_pos[5],y=585) 

        self.trial5_in_7 = ttk.Label(self.frame5, text="| End ",font=("Calibri", 10, "bold"))
        self.trial5_in_7.place(x=self.trial5_start_pos[6],y=585) 

        self.title_5_trial = ttk.Label(self.trial5_exp_lf, text="In direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_trial.grid(row=self.trial5_row+1, column=1, padx=5, pady=5)

        self.title_5_status_1 = ttk.Label(self.trial5_exp_lf, text="25 % MVT_EL: "+str(float(self.trial5_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_1.grid(row=self.trial5_row+1, column=3, padx=5, pady=5)   

        self.title_5_status_2 = ttk.Label(self.trial5_exp_lf, text="20 % MVT_SH: "+str(float(self.trial5_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_2.grid(row=self.trial5_row+2, column=3, padx=5, pady=5) 

        self.is_trial5_in = True
   
    def delete_trial5_in(self):
        self.trial5_in_1.place_forget()
        self.trial5_in_2.place_forget()
        self.trial5_in_3.place_forget()
        self.trial5_in_4.place_forget()
        self.trial5_in_5.place_forget()
        self.trial5_in_6.place_forget()
        self.trial5_in_7.place_forget()
        self.title_5_trial.grid_forget()
        self.title_5_status_1.grid_forget()
        self.title_5_status_2.grid_forget()
        
        self.is_trial5_in = False
   
    def add_trial5_upin(self):
        # calculate trial5 distance of label
        self.trial5_start_pos = self.calculate_bar('trial2_upin')

        self.trial5_upin_1 = ttk.Label(self.frame5, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial5_upin_1.place(x=self.trial5_start_pos[0],y=585)  

        self.trial5_upin_2 = ttk.Label(self.frame5, text="| up ",font=("Calibri", 10, "bold"))
        self.trial5_upin_2.place(x=self.trial5_start_pos[1],y=585)  

        self.trial5_upin_3 = ttk.Label(self.frame5, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial5_upin_3.place(x=self.trial5_start_pos[2],y=585)  

        self.trial5_upin_4 = ttk.Label(self.frame5, text="| in ",font=("Calibri", 10, "bold"))
        self.trial5_upin_4.place(x=self.trial5_start_pos[3],y=585)  

        self.trial5_upin_5 = ttk.Label(self.frame5, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial5_upin_5.place(x=self.trial5_start_pos[4],y=585)  

        self.trial5_upin_6 = ttk.Label(self.frame5, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial5_upin_6.place(x=self.trial5_start_pos[5],y=585) 

        self.trial5_upin_7 = ttk.Label(self.frame5, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial5_upin_7.place(x=self.trial5_start_pos[6],y=585) 

        self.trial5_upin_8 = ttk.Label(self.frame5, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial5_upin_8.place(x=self.trial5_start_pos[7],y=585) 

        self.trial5_upin_9 = ttk.Label(self.frame5, text="| End ",font=("Calibri", 10, "bold"))
        self.trial5_upin_9.place(x=self.trial5_start_pos[8],y=585) 

        self.title_5_trial = ttk.Label(self.trial5_exp_lf, text="Up and In direction",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_trial.grid(row=self.trial5_row+1, column=1, padx=5, pady=5)

        self.title_5_status_1 = ttk.Label(self.trial5_exp_lf, text="25 % MVT_EL: "+str(float(self.trial5_result[2].get())*0.25)+" N",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_1.grid(row=self.trial5_row+1, column=3, padx=5, pady=5)   

        self.title_5_status_2 = ttk.Label(self.trial5_exp_lf, text="20 % MVT_SH: "+str(float(self.trial5_result[0].get())*0.20)+" Nm",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_5_status_2.grid(row=self.trial5_row+2, column=3, padx=5, pady=5)  

        self.is_trial5_upin = True

    def delete_trial5_upin(self):
        self.trial5_upin_1.place_forget()
        self.trial5_upin_2.place_forget()
        self.trial5_upin_3.place_forget()
        self.trial5_upin_4.place_forget()
        self.trial5_upin_5.place_forget()
        self.trial5_upin_6.place_forget()
        self.trial5_upin_7.place_forget()
        self.trial5_upin_8.place_forget()
        self.trial5_upin_9.place_forget()
        self.title_5_trial.grid_forget()
        self.title_5_status_1.grid_forget()
        self.title_5_status_2.grid_forget()

        self.is_trial5_upin = False
   
    def delete_trial5_label(self):
        M = [self.is_trial5_up, self.is_trial5_in, self.is_trial5_upin]
        print(M)
        if self.is_trial5_up:
            self.delete_trial5_up()
        elif self.is_trial5_in:
            self.delete_trial5_in()
        elif self.is_trial5_upin:
            self.delete_trial5_upin()
   
   # ---------------------------------------functions in frame 6---------------------------------------
    def trial6_Start(self):
        self.stop_bar = False
        # save the data
        trial6_saved = []
        trial6_saved.append(self.trial6_start_StinngVar.get())

        trial6_header = []
        trial6_header.append('Experiment Mode')

        is_correct = True
        # make sure all data has been input
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:

            if self.trial6_start_StinngVar.get() == "Automatic":
                for set_count in range(1,100):
                    if self.trial6_break == False:
                        # ouput the GUI data to experiment protocol
                        trial6_saved.pop()
                        if set_count %4 == 1:
                            trial6_saved.append("Set 1")
                        elif set_count %4 == 2:
                            trial6_saved.append("Set 2")
                        elif set_count %4 == 3:
                            trial6_saved.append("Set 3")
                        elif set_count %4 == 0:
                            trial6_saved.append("Set 4")

                        maxFinal = dict(zip(trial6_header, trial6_saved))
                        self.transmit("Trial6", maxFinal)
                        print(maxFinal)

                        # delete the old bar
                        self.delete_trial6_label()

                        # add label on the bar
                        self.add_trial6_bar(set_count) 

                        # start the progressive bar
                        self.start_trial6_bar(195)  

            else:
                maxFinal = dict(zip(trial6_header, trial6_saved))
                self.transmit("Trial6", maxFinal)
                print(maxFinal)

                self.trial6_break = True
                # delete the old bar
                self.delete_trial6_label()

                # add label on the bar
                self.add_trial6_bar(int(self.trial6_start_StinngVar.get()[4]))

                # start the progressive bar
                self.start_trial6_bar(195) 
                self.trial6_break = False


    

    def start_trial6_bar(self, max):
        # start the progressive bar
        self.title_6_fg['maximum'] = max
        self.title_6_fg['value'] = 0

        for i in range(max):

            if self.stop_bar:
                self.title_1_fg['value'] = 0
                self.trial1_exp_lf.update()
                time.sleep(0.05)
            else:
                self.title_6_fg['value'] = i+1
                self.trial6_exp_lf.update()
                time.sleep(0.05) 

    def add_trial6_bar(self, set_count):
        if set_count %4 == 1:
            self.add_trial6_set1()
        elif set_count %4 == 2:
            self.add_trial6_set2()
        elif set_count %4 == 3:
            self.add_trial6_set3()
        elif set_count %4 == 0:
            self.add_trial6_set4()
    
    def trial6_Stop(self):
        self.stop_bar = True
        self.title_6_fg.grid_forget()
        self.title_6_fg = ttk.Floodgauge(self.trial6_exp_lf, bootstyle=INFO, length=750, maximum=1000, font=("Calibri", 12, 'bold'),)
        self.title_6_fg.grid(row=self.trial6_row+6, column=0, columnspan=5, padx=5, pady=3)   
        self.title_6_fg['value'] = 0
        self.transmit("Stop", "stop")


    def add_trial6_set1(self):
        
        # In Out Up Down
        # calculate trial6 distance of label   
        self.trial6_start_pos = self.calculate_bar('trial6')

        self.trial6_set1_1 = ttk.Label(self.frame6, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial6_set1_1.place(x=self.trial6_start_pos[0],y=495)  

        self.trial6_set1_2 = ttk.Label(self.frame6, text="| In ",font=("Calibri", 10, "bold"))
        self.trial6_set1_2.place(x=self.trial6_start_pos[1],y=495)  

        self.trial6_set1_3 = ttk.Label(self.frame6, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial6_set1_3.place(x=self.trial6_start_pos[2],y=495)  

        self.trial6_set1_4 = ttk.Label(self.frame6, text="| Up ",font=("Calibri", 10, "bold"))
        self.trial6_set1_4.place(x=self.trial6_start_pos[3],y=495) 

        self.trial6_set1_5 = ttk.Label(self.frame6, text="| Down ",font=("Calibri", 10, "bold"))
        self.trial6_set1_5.place(x=self.trial6_start_pos[4],y=495) 

        self.trial6_set1_6 = ttk.Label(self.frame6, text="| End ",font=("Calibri", 10, "bold"))
        self.trial6_set1_6.place(x=self.trial6_start_pos[5],y=495) 

        self.title_6_trial = ttk.Label(self.trial6_exp_lf, text="Set 1",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_trial.grid(row=self.trial6_row+1, column=1, padx=5, pady=5)

        self.title_6_status_1 = ttk.Label(self.trial6_exp_lf, text="In Out Up Down",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_1.grid(row=self.trial6_row+1, column=3, padx=5, pady=5)   

        self.title_6_status_2 = ttk.Label(self.trial6_exp_lf, text="Out Up Down In",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_2.grid(row=self.trial6_row+2, column=3, padx=5, pady=5) 

        self.is_trial6_set1 = True
   
    def delete_trial6_set1(self):
        self.trial6_set1_1.place_forget()
        self.trial6_set1_2.place_forget()
        self.trial6_set1_3.place_forget()
        self.trial6_set1_4.place_forget()
        self.trial6_set1_5.place_forget()
        self.trial6_set1_6.place_forget()
        self.title_6_trial.grid_forget()
        self.title_6_status_1.grid_forget()
        self.title_6_status_2.grid_forget()

        self.is_trial6_set1 = False

    def add_trial6_set2(self):
        # Out Up Down In
        # calculate trial6 distance of label   
        self.trial6_start_pos = self.calculate_bar('trial6')

        self.trial6_set2_1 = ttk.Label(self.frame6, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial6_set2_1.place(x=self.trial6_start_pos[0],y=495)  

        self.trial6_set2_2 = ttk.Label(self.frame6, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial6_set2_2.place(x=self.trial6_start_pos[1],y=495)  

        self.trial6_set2_3 = ttk.Label(self.frame6, text="| Up ",font=("Calibri", 10, "bold"))
        self.trial6_set2_3.place(x=self.trial6_start_pos[2],y=495)  

        self.trial6_set2_4 = ttk.Label(self.frame6, text="| Down ",font=("Calibri", 10, "bold"))
        self.trial6_set2_4.place(x=self.trial6_start_pos[3],y=495) 

        self.trial6_set2_5 = ttk.Label(self.frame6, text="| In ",font=("Calibri", 10, "bold"))
        self.trial6_set2_5.place(x=self.trial6_start_pos[4],y=495) 

        self.trial6_set2_6 = ttk.Label(self.frame6, text="| End ",font=("Calibri", 10, "bold"))
        self.trial6_set2_6.place(x=self.trial6_start_pos[5],y=495) 

        self.title_6_trial = ttk.Label(self.trial6_exp_lf, text="Set 2",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_trial.grid(row=self.trial6_row+1, column=1, padx=5, pady=5)

        self.title_6_status_1 = ttk.Label(self.trial6_exp_lf, text="Out Up Down In",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_1.grid(row=self.trial6_row+1, column=3, padx=5, pady=5)   

        self.title_6_status_2 = ttk.Label(self.trial6_exp_lf, text="Up Down In Out",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_2.grid(row=self.trial6_row+2, column=3, padx=5, pady=5) 

        self.is_trial6_set2 = True
   
    def delete_trial6_set2(self):
        self.trial6_set2_1.place_forget()
        self.trial6_set2_2.place_forget()
        self.trial6_set2_3.place_forget()
        self.trial6_set2_4.place_forget()
        self.trial6_set2_5.place_forget()
        self.trial6_set2_6.place_forget()
        self.title_6_trial.grid_forget()
        self.title_6_status_1.grid_forget()
        self.title_6_status_2.grid_forget()

        self.is_trial6_set2 = False

    def add_trial6_set3(self):
        # Up Down In Out
        # calculate trial6 distance of label   
        self.trial6_start_pos = self.calculate_bar('trial6')

        self.trial6_set3_1 = ttk.Label(self.frame6, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial6_set3_1.place(x=self.trial6_start_pos[0],y=495)  

        self.trial6_set3_2 = ttk.Label(self.frame6, text="| Up ",font=("Calibri", 10, "bold"))
        self.trial6_set3_2.place(x=self.trial6_start_pos[1],y=495)  

        self.trial6_set3_3 = ttk.Label(self.frame6, text="| Down ",font=("Calibri", 10, "bold"))
        self.trial6_set3_3.place(x=self.trial6_start_pos[2],y=495)  

        self.trial6_set3_4 = ttk.Label(self.frame6, text="| In ",font=("Calibri", 10, "bold"))
        self.trial6_set3_4.place(x=self.trial6_start_pos[3],y=495) 

        self.trial6_set3_5 = ttk.Label(self.frame6, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial6_set3_5.place(x=self.trial6_start_pos[4],y=495) 

        self.trial6_set3_6 = ttk.Label(self.frame6, text="| End ",font=("Calibri", 10, "bold"))
        self.trial6_set3_6.place(x=self.trial6_start_pos[5],y=495) 

        self.title_6_trial = ttk.Label(self.trial6_exp_lf, text="Set 3",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_trial.grid(row=self.trial6_row+1, column=1, padx=5, pady=5)

        self.title_6_status_1 = ttk.Label(self.trial6_exp_lf, text="Up Down In Out",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_1.grid(row=self.trial6_row+1, column=3, padx=5, pady=5)   

        self.title_6_status_2 = ttk.Label(self.trial6_exp_lf, text="Down In Out Up",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_2.grid(row=self.trial6_row+2, column=3, padx=5, pady=5) 

        self.is_trial6_set3 = True
   
    def delete_trial6_set3(self):
        self.trial6_set3_1.place_forget()
        self.trial6_set3_2.place_forget()
        self.trial6_set3_3.place_forget()
        self.trial6_set3_4.place_forget()
        self.trial6_set3_5.place_forget()
        self.trial6_set3_6.place_forget()
        self.title_6_trial.grid_forget()
        self.title_6_status_1.grid_forget()
        self.title_6_status_2.grid_forget()

        self.is_trial6_set3 = False

    def add_trial6_set4(self):
        # Down In Out Up
        # calculate trial6 distance of label   
        self.trial6_start_pos = self.calculate_bar('trial6')

        self.trial6_set4_1 = ttk.Label(self.frame6, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial6_set4_1.place(x=self.trial6_start_pos[0],y=495)  

        self.trial6_set4_2 = ttk.Label(self.frame6, text="| Down ",font=("Calibri", 10, "bold"))
        self.trial6_set4_2.place(x=self.trial6_start_pos[1],y=495)  

        self.trial6_set4_3 = ttk.Label(self.frame6, text="| In ",font=("Calibri", 10, "bold"))
        self.trial6_set4_3.place(x=self.trial6_start_pos[2],y=495)  

        self.trial6_set4_4 = ttk.Label(self.frame6, text="| Out ",font=("Calibri", 10, "bold"))
        self.trial6_set4_4.place(x=self.trial6_start_pos[3],y=495) 

        self.trial6_set4_5 = ttk.Label(self.frame6, text="| Up ",font=("Calibri", 10, "bold"))
        self.trial6_set4_5.place(x=self.trial6_start_pos[4],y=495) 

        self.trial6_set4_6 = ttk.Label(self.frame6, text="| End ",font=("Calibri", 10, "bold"))
        self.trial6_set4_6.place(x=self.trial6_start_pos[5],y=495) 

        self.title_6_trial = ttk.Label(self.trial6_exp_lf, text="Set 4",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_trial.grid(row=self.trial6_row+1, column=1, padx=5, pady=5)

        self.title_6_status_1 = ttk.Label(self.trial6_exp_lf, text="Down In Out Up",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_1.grid(row=self.trial6_row+1, column=3, padx=5, pady=5)   

        self.title_6_status_2 = ttk.Label(self.trial6_exp_lf, text="In Out Up Down",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_6_status_2.grid(row=self.trial6_row+2, column=3, padx=5, pady=5) 

        self.is_trial6_set4 = True
   
    def delete_trial6_set4(self):
        self.trial6_set4_1.place_forget()
        self.trial6_set4_2.place_forget()
        self.trial6_set4_3.place_forget()
        self.trial6_set4_4.place_forget()
        self.trial6_set4_5.place_forget()
        self.trial6_set4_6.place_forget()
        self.title_6_trial.grid_forget()
        self.title_6_status_1.grid_forget()
        self.title_6_status_2.grid_forget()

        self.is_trial6_set4 = False

    def delete_trial6_label(self):
        if self.is_trial6_set1:
            self.delete_trial6_set1()
        elif self.is_trial6_set2:
            self.delete_trial6_set2()
        elif self.is_trial6_set3:
            self.delete_trial6_set3()
        elif self.is_trial6_set4:
            self.delete_trial6_set4()
   # def pause(self):
    #     self.pauseFlag = not(self.pauseFlag)
    #     self.transmit("Pause", self.pauseFlag)

    # def end(self):
    #     self.transmit("End", 'end')



def launchGUI(conn, in_conn):
    # run the GUI
    root = ttk.Window(
            title="Torque GUI",        
            themename="litera",     
            size=(1100,800),        
            position=(100,100),     
            minsize=(0,0),         
            maxsize=(1100,800),    
            resizable=None,         
            alpha=1.0,              
    )
    gui = GUI(root, conn, in_conn)
    root.mainloop()
    exit()


if __name__=='__main__':
    launchGUI(conn=Queue(),in_conn=Queue())
    pass
