from multiprocessing import Process, Queue
from sre_parse import WHITESPACE
from tkinter import font
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import time

class GUI:
    def __init__(self, master, conn, in_conn=None):
        self.is_trial2_auto = False
        self.is_trial2_up = False
        self.is_trial2_in = False
        self.is_trial2_upin = False

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
        self.frame1 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame2 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame3 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame4 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame5 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame6 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame7 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame8 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame9 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)

        self.notebk.add(self.frame1, text = 'Constant                                           ')
        self.notebk.add(self.frame2, text = 'Type 1: Maximum measurements   ')
        self.notebk.add(self.frame3, text = 'Type 2: Pre-motor assessment        ')
        self.notebk.add(self.frame4, text = 'Type 3: Matching trials                    ')
        self.notebk.add(self.frame5, text = "Type 4: Baseline sEMG's                  ")
        self.notebk.add(self.frame6, text = 'Type 5: Post-motor assessment      ')
        self.notebk.add(self.frame7, text = 'Type 6: Torque Control assessment')
        self.notebk.add(self.frame8, text = "Type 8: Working Memory trials       ")
        self.notebk.pack(expand = 1, fill="both")

        self.set_frame1()
        self.set_frame2()
        self.set_frame3()
        self.set_frame4()

    # frame functions

    def set_frame1(self):
        # --------------------------- Frame 1 ----------------------------------------------
        self.title = ttk.Label(self.frame1, text="                                                       Constant Value", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=2, columnspan=4, padx=10, pady=10)

        # Subject Info Pane
        self.sub_lf = ttk.Labelframe(self.frame1,text="Subject Information", bootstyle=INFO)
        self.sub_lf.place(x=40,y=50,width=400,height=420)

        self.subjectInfo = ['Subject Number', 'Age', 'Gender', 'Subject Type', 'Disabetes', 'Years since stroke', 
                             'Dominant Arm', 'Testing Arm']

        self.subject_result = []
        # Text entry fields
        for i in range(len(self.subjectInfo)):
            ttk.Label(self.sub_lf, text=self.subjectInfo[i],font=("Calibri", 10)).grid(row=i+1, column=0, padx=5, pady=5)
            if self.subjectInfo[i] not in ['Gender', 'Disabetes', 'Dominant Arm', 'Testing Arm']:
                e1 = ttk.Entry(self.sub_lf,show=None)
                e1.grid(row=i+1, column=1, padx=5, pady=5)
                self.subject_result.append(e1)
        
        # Option Menus
        # Gender
        self.genders_StinngVar = ttk.StringVar(self.master)
        self.genders_First = 'Select a gender'
        self.genders_StinngVar.set(self.genders_First)
        self.genders_Type = ["Male", "Female", "Other"]
        self.genders_Menu = ttk.OptionMenu(self.sub_lf, self.genders_StinngVar, self.genders_Type[0], *self.genders_Type,)
        self.genders_Menu.grid(row=3, column=1, padx=5, pady=5)
    
        # Disabetes
        self.disabetes_StinngVar = ttk.StringVar(self.master)
        self.disabetes_First = 'YES/NO'
        self.disabetes_StinngVar.set(self.disabetes_First)
        self.disabetes_Type = ['YES','NO']
        self.disabetes_Menu = ttk.OptionMenu(self.sub_lf, self.disabetes_StinngVar, self.disabetes_Type[0], *self.disabetes_Type)
        self.disabetes_Menu.grid(row=5, column=1, padx=5, pady=5)

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

        # Submit subject information
        self.jacobSub = ttk.Button(self.sub_lf, text="Submit", bootstyle=(INFO, OUTLINE), command=self.Subject_Submit)
        self.jacobSub.grid(row=9,column=1, padx=5, pady=5)
       
        # Input Jacobean
        # self.title = ttk.Label(self.frame1, text="-----------------------------------Please Input the Jacobean Constant-----------------------------------", bootstyle=DANGER)
        # self.title.grid(row=10, column=0,columnspan=4, padx=5, pady=5)

        # Jacobean Constants Pane
        self.jac_lf = ttk.Labelframe(self.frame1,text="Jacobean Constant", bootstyle=INFO)
        self.jac_lf.place(x=40,y=500,width=500,height=250)
        
        self.jacobInfo = ["Shoulder Abduction Angle (degree)","Elbow Flexion Angle (degree)","Arm Length (m)",
                          "Midload cell to elbow joint (m)"]

        self.jaco_result = []
        for i in range(len(self.jacobInfo)):
            ttk.Label(self.jac_lf, text=self.jacobInfo[i],font=("Calibri", 10)).grid(row=i+11, column=0, padx=5, pady=5)
            e2 = ttk.Entry(self.jac_lf,show=None)
            e2.grid(row=i+11, column=1, padx=5, pady=5)
            self.jaco_result.append(e2)

        # Submit
        self.subStringVars = [self.genders_StinngVar, self.disabetes_StinngVar, self.domArm_StinngVar, self.TestArm_StinngVar]
        self.subFirsts = [self.genders_First, self.disabetes_First, self.domArm_First, self.TestArm_First]

        self.jacobSub = ttk.Button(self.jac_lf, text="Submit and Save", bootstyle=(INFO, OUTLINE), command=self.jacobSubmit)
        self.jacobSub.grid(row=len(self.jacobInfo)+11,column=1, padx=5, pady=5)

        # End 
        self.End_lf = ttk.Frame(self.frame1)
        self.End_lf.place(x=700,y=700,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame2(self):
        # --------------------------- Frame 2 ----------------------------------------------
        # Title
        # self.title = ttk.Label(self.frame2, text="------------------------------Trial Type 1: Maximum measurements (sEMGs, elbow and shoulder torques)------------------------------", bootstyle=DANGER)
        self.title = ttk.Label(self.frame2, text="           Maximum measurements (sEMGs, elbow and shoulder torques)", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        # set initial value of MVT
        self.setInfo = ["SET 1 Max torque flexion paretic", "SET 2 Max torque shoulder abduction", "SET 3 Synergy while holding 40% Max Shoulder Abduction"]
        self.maxInfo = ["Input a initial value of MVT_EF (elbow flexion)","Input a initial value of MVT shoulder abduction", "Input a initial value of EMG"]

        self.count_max = 0

        ### MVT_EF
        self.EF_row = 1
        # add EF label frame
        self.EF_lf = ttk.Labelframe(self.frame2,text=self.setInfo[0], bootstyle=INFO)
        self.EF_lf.place(x=10,y=50,width=350,height=500)

        self.EF_title = ttk.Label(self.EF_lf, text="Trial 1", font=("Calibri", 12, "bold"))
        self.EF_title.grid(row=self.EF_row+1, column=0, padx=5, pady=5)

        # enter initial value
        ttk.Label(self.EF_lf, text=self.maxInfo[0],font=("Calibri", 10)).grid(row=self.EF_row+2, column=0, padx=5, pady=5)
        self.EF_data = ttk.Entry(self.EF_lf,show=None)
        self.EF_data.grid(row=self.EF_row+3, column=0, padx=5, pady=5)

        # submit EF
        self.MVTSub = ttk.Button(self.EF_lf, text="Start", command=self.EF_maxSubmit)
        self.MVTSub.grid(row=self.EF_row+4,column=0, padx=5, pady=5)
        
        # record
        self.save = ttk.Button(self.EF_lf, text='Record', command=self.EF_record)
        self.save.grid(row=self.EF_row+9, column=0, padx=5, pady=5)

        ##########################################Fake##############################
        ### MVT_extension
        # add extension label frame
        self.Ext_lf = ttk.Labelframe(self.frame2,text=self.setInfo[1], bootstyle=INFO)
        self.Ext_lf.place(x=400,y=50,width=350,height=500)

        self.Ext_row = 0

        self.Ext_title = ttk.Label(self.Ext_lf, text="Trial 1", font=("Calibri", 12, "bold"))
        self.Ext_title.grid(row=self.Ext_row+1, column=1, padx=5, pady=5)

        ttk.Label(self.Ext_lf, text=self.maxInfo[1],font=("Calibri", 10)).grid(row=self.Ext_row+2, column=1, padx=5, pady=5)
        self.Ext_data = ttk.Entry(self.Ext_lf,show=None)
        self.Ext_data.grid(row=self.Ext_row+3, column=1, padx=5, pady=5)

        # submit extension
        self.MVTSub = ttk.Button(self.Ext_lf, text="Start", command=self.Ext_maxSubmit)
        self.MVTSub.grid(row=self.Ext_row+4,column=1, padx=5, pady=5)
        
        # record
        self.save = ttk.Button(self.Ext_lf, text='Record', command=self.Ext_record)
        self.save.grid(row=self.Ext_row+9, column=1, padx=5, pady=5)
    
        # ### MVT_Flex
        # self.EF_row = 1
        # ttk.Label(self.frame2, text=self.setInfo[2]).grid(row=self.EF_row, column=2, padx=5, pady=5)
        # ttk.Label(self.frame2, text=self.maxInfo[2]).grid(row=self.EF_row+1, column=2, padx=5, pady=5)
        # self.EF_data = ttk.Entry(self.frame2,show=None)
        # self.EF_data.grid(row=self.EF_row+2, column=2, padx=5, pady=5)

        # # submit EF
        # self.MVTSub = ttk.Button(self.frame2, text="Start", command=self.EF_maxSubmit)
        # self.MVTSub.grid(row=self.EF_row+3,column=2, padx=5, pady=5)
        
        # # record
        # self.save = ttk.Button(self.frame2, text='Record', command=self.EF_record)
        # self.save.grid(row=self.EF_row+8, column=2, padx=5, pady=5)

        # End 
        self.End_lf = ttk.Frame(self.frame2)
        self.End_lf.place(x=700,y=700,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame3(self): 
        # --------------------------- Frame 3 ----------------------------------------------
        self.trial2_row = 1
        self.trial2_maxinfo = ["Maximum elbow flexion value"]

        # Title
        self.title = ttk.Label(self.frame3, text="                                          Pre-motor assessment", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        ### Description
        # add EF label frame
        self.trial2_lf = ttk.Labelframe(self.frame3,text="Preparation", bootstyle=INFO)
        self.trial2_lf.place(x=10,y=50,width=770,height=260)

        # description
        self.description_2 = ttk.Label(self.trial2_lf, text="    This section is used to do a pre-motor assessment, the subject will do a small test with 25% MVT_EF",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+1, column=0, columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+2, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+2, column=2, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+3, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+3, column=2, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Years since stroke:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+4, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+4, column=2, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Max MVT_EF value:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+5, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="25% of Max MVT_EF value:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+5, column=2, padx=5, pady=5)

        # Enter the maximum MVT value
        self.title_2 = ttk.Label(self.trial2_lf, text="    Input the maximum MVT_EF: ",font=("Calibri", 10))
        self.title_2.grid(row=self.trial2_row+6, column=0, padx=5, pady=5)

        self.input_2_data = ttk.Entry(self.trial2_lf,show=None)
        self.input_2_data.grid(row=self.trial2_row+6, column=1, padx=10, pady=5)
        
        self.MVTSub = ttk.Button(self.trial2_lf, text="Submit", command=self.trial2_Submit)
        self.MVTSub.grid(row=self.trial2_row+6,column=2, padx=5, pady=5)

        ### Experimental 
        # add trail2 experimental label frame
        self.trial2_exp_lf = ttk.Labelframe(self.frame3,text="Experimental", bootstyle=INFO)
        self.trial2_exp_lf.place(x=10,y=330,width=770,height=350)

        # UP IN UP&IN
        self.title_2 = ttk.Label(self.trial2_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_2.grid(row=self.trial2_row+0, column=0, padx=5, pady=5)


        self.trial2_start_StinngVar = ttk.StringVar(self.master)
        self.trial2_start_First = 'Select a gender'
        self.trial2_start_StinngVar.set(self.trial2_start_First)
        self.trial2_start_Type = ["Automatic", "Up direction", "In direction", "Up and In direction"]
        self.trial2_start_Menu = ttk.OptionMenu(self.trial2_exp_lf, self.trial2_start_StinngVar, self.trial2_start_Type[0], *self.trial2_start_Type,)
        self.trial2_start_Menu.grid(row=self.trial2_row+0,column=1, padx=5, pady=5)


        self.title_2 = ttk.Button(self.trial2_exp_lf, text="Start", command=self.trial2_Start, bootstyle=DANGER)
        self.title_2.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)

        # self.MVTSub = ttk.Button(self.trial2_exp_lf, text="Start: In direction", command=self.trial2_Submit, bootstyle=DANGER)
        # self.MVTSub.grid(row=self.trial2_row+0,column=1, padx=5, pady=5)

        # self.MVTSub = ttk.Button(self.trial2_exp_lf, text="Start: Up and In direction", command=self.trial2_Submit, bootstyle=DANGER)
        # self.MVTSub.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)



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
        self.title_2_fg = ttk.Floodgauge(self.trial2_exp_lf, bootstyle=INFO, length=720, maximum=self.trial2_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_2_fg.grid(row=self.trial2_row+6, column=0, columnspan=5, padx=5, pady=3)  




        # End 
        self.End_lf = ttk.Frame(self.frame3)
        self.End_lf.place(x=700,y=700,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame4(self):
        self.title = ttk.Label(self.frame4, text="                                               Matching tasks", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        ### Description
        # add EF label frame
        self.trial2_lf = ttk.Labelframe(self.frame4,text="Preparation", bootstyle=INFO)
        self.trial2_lf.place(x=10,y=50,width=770,height=310)

        # description
        self.description_2 = ttk.Label(self.trial2_lf, text="    This section is used to do a pre-motor assessment, the subject will do a small test with 25% MVT_EF",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+1, column=0, columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+2, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+2, column=2, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+3, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+3, column=2, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Years since stroke:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+4, column=0, padx=5, pady=5)

        self.input_2 = ttk.Label(self.trial2_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_2.grid(row=self.trial2_row+4, column=2, padx=5, pady=5)

        # Enter the maximum MVT value

        self.MVTInfo = ["Max Shoulder Abduction (Nm)","Maximum Elbow Extension (Nm)","Maximum Elbow Flexion (N)"]

        self.mvt_result = []
        for i in range(len(self.MVTInfo)):
            ttk.Label(self.trial2_lf, text=self.MVTInfo[i],font=("Calibri", 10)).grid(row=self.trial2_row+6+i, column=0, padx=5, pady=5)
            e2 = ttk.Entry(self.trial2_lf,show=None)
            e2.grid(row=self.trial2_row+6+i, column=1, padx=5, pady=5)
            self.jaco_result.append(e2)

        self.MVTSub = ttk.Button(self.trial2_lf, text="Submit", command=self.trial3_Submit)
        self.MVTSub.grid(row=self.trial2_row+8,column=2, padx=5, pady=5)


    # Helper functions
    def transmit(self, header, information):
        self.data_queue.put((header, information))

    def showError(self):
        print("retrycancel: ",Messagebox.show_error(title='Oh no', message="All fields should be filled"))

    # close the window
    def close(self):
        self.transmit("Close", "close")

    # ---------------------------------------functions in frame 1---------------------------------------

    # check if all the data has been submitted in the frame 1
    def checkFields_frame1(self):
        result = []
        for i in range(4):
            result.append(self.subject_result[i].get())
        for i in range(4):
            result.append(self.jaco_result[i].get())
        for i in result:
            if i == '':
                self.showError()
                break      

    def Subject_Submit(self):
        subjectSaved = []
        for i in range(4):
            subjectSaved.append(self.subject_result[i].get())
        is_corret = True
        for i in subjectSaved:
            if i == '':
                self.showError()
                is_corret = False
                break

        if is_corret:
            self.label1 = ttk.Label(self.sub_lf, text='Successfully Input !', bootstyle=SUCCESS)
            self.label1.grid(row=9, column=2)
            for i in self.subStringVars:
                subjectSaved.append(i.get())
            
            # reset the subject saved list
            disabtes = subjectSaved.pop(2)
            subject_type = subjectSaved.pop(2)
            subjectSaved.insert(3, disabtes)
            subjectSaved.insert(5, subject_type)
            # zip
            # print (subjectSaved)
            subjectFinal = dict(zip(self.subjectInfo, subjectSaved))
            self.transmit("Subject Info", subjectFinal)

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[0],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+2, column=1, padx=5, pady=5)              

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[1],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)   

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[2],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+3, column=1, padx=5, pady=5) 

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[3],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+3, column=3, padx=5, pady=5) 

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[5],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+4, column=1, padx=5, pady=5) 

            self.input_2 = ttk.Label(self.trial2_lf, text=subjectSaved[7],font=("Calibri", 10), bootstyle=SUCCESS)
            self.input_2.grid(row=self.trial2_row+4, column=3, padx=5, pady=5)  
    # submit jacobean data
    def jacobSubmit(self):
        jacobSaved = []
        for i in range(4):
            jacobSaved.append(self.jaco_result[i].get())
        is_corret = True
        for i in jacobSaved:
            if i == '':
                self.showError()
                is_corret = False
                break
        if is_corret:
            self.label1 = ttk.Label(self.jac_lf, text='Successfully Input !', bootstyle=SUCCESS)
            self.label1.grid(row=15, column=2)
            i = 0
            jacobFinal = dict(zip(self.jacobInfo, jacobSaved))
            self.transmit("Jacobean Constants", jacobFinal)


    # ---------------------------------------functions in frame 2---------------------------------------
    def EF_maxSubmit(self):
        EF_saved = []
        EF_saved.append(self.EF_data.get())
        if self.EF_data.get() == '' or self.checkFields_frame1():
            self.showError()
        else:
            # set the MVT_EF max value
            maxFinal = dict(zip(self.maxInfo, EF_saved))
            self.transmit("EF_max", maxFinal)
            # output the text cue
            self.count_max += 1
            self.label1 = ttk.Label(self.EF_lf, text='Please push the sensor', bootstyle=DANGER)
            self.label1.grid(row=self.EF_row+6, column=0)

            
    def EF_record(self):
        self.label1.grid_forget()
        # self.EF_title.grid_forget()
        if self.EF_data.get() == '':
            self.showError()
        else:
            self.count_max += 1
            if not self.in_queue.empty():
                self.EF_queue = self.in_queue.get_nowait()
            else:
                print("Empty queue")
            self.label2 = ttk.Label(self.EF_lf, text='Trial '+ str((self.count_max)/2) + '  MVT_EF: '+str(list(self.EF_queue)[3]), bootstyle=SUCCESS)
            self.label2.grid(row=self.count_max+self.EF_row+9, column=0)
            
            self.EF_title = ttk.Label(self.EF_lf, text="Trail "+str(int((self.count_max)/2)+1), font=("Calibri", 12, "bold")).grid(row=self.EF_row+1, column=0, padx=5, pady=5)


    def Ext_maxSubmit(self):
        Ext_saved = []
        Ext_saved.append(self.Ext_data.get())
        if self.Ext_data.get() == '' or self.checkFields_frame1():
            self.showError()
        else:
            # set the MVT_Ext max value
            maxFinal = dict(zip(self.maxInfo, Ext_saved))
            self.transmit("Ext_max", maxFinal)
            # output the text cue
            self.count_max += 1
            self.label1 = ttk.Label(self.frame2, text='Please push the sensor', bootstyle=DANGER)
            self.label1.grid(row=self.Ext_row+6, column=0)

            
    def Ext_record(self):
        self.label1.grid_forget()
        if self.Ext_data.get() == '':
            self.showError()
        else:
            self.count_max += 1
            if not self.in_queue.empty():
                self.Ext_queue = self.in_queue.get_nowait()
            else:
                print("Empty queue")
            self.label2 = ttk.Label(self.frame2, text='Trial '+ str((self.count_max)/2) + '  MVT_Extension: '+str(list(self.Ext_queue)[3]), bootstyle=SUCCESS)
            self.label2.grid(row=self.count_max+self.Ext_row+9, column=0)

    # ---------------------------------------functions in frame 3---------------------------------------

    def trial2_Submit(self):
        if self.input_2_data.get() == '': # or self.checkFields_frame1()
            self.showError()
        else:
            self.input_2 = ttk.Label(self.trial2_lf, text=self.input_2_data.get(),font=("Calibri", 10), bootstyle = DANGER)
            self.input_2.grid(row=self.trial2_row+5, column=1, padx=5, pady=5)

            self.input_2 = ttk.Label(self.trial2_lf, text=str(float(self.input_2_data.get())*0.25),font=("Calibri", 10), bootstyle = DANGER)
            self.input_2.grid(row=self.trial2_row+5, column=3, padx=5, pady=5)

    def trial2_Start(self):
        trial2_saved = []
        trial2_saved.append(self.input_2_data.get())
        if self.input_2_data.get() == '': # or self.checkFields_frame1()
            self.showError()
        else:
            # submit the max mvt_ef
            trial2_maxFinal = dict(zip(self.trial2_maxinfo, trial2_saved))
            self.transmit("Trial2_automatic", trial2_maxFinal)
            
            if self.trial2_start_StinngVar.get() == "Automatic":
                # add a new progress bar
                self.add_progess_bar(1000)

                # add description on the bar
                self.trial2_up_pos = self.calculate_bar("auto")[0]
                self.trial2_in_pos = self.calculate_bar("auto")[1]
                self.trial2_upin_pos = self.calculate_bar("auto")[2]
                self.automatic_bar()

            elif self.trial2_start_StinngVar.get() == "Up direction":
                # add a new progress bar
                self.add_progess_bar(100)

                # add description on the bar
                self.trial2_up_pos = self.calculate_bar("up")
                self.up_bar()

            elif self.trial2_start_StinngVar.get() == "In direction":
                # add a new progress bar
                self.add_progess_bar(100)

                # add description on the bar
                self.trial2_in_pos = self.calculate_bar("in")
                self.in_bar()

            elif self.trial2_start_StinngVar.get() == "Up and In direction":
                # add a new progress bar
                self.add_progess_bar(100)

                # add description on the bar
                self.trial2_upin_pos = self.calculate_bar("upin")
                self.upin_bar()

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

        if mode == "up" or mode == "in" :
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
        elif mode == "upin":
            # bar time
            start = Starting_time+0.6              
            up = start+Up_time+2.0                 
            hold_1 = up+Hold_time+1.5               
            in_time = hold_1+In_time+2.0
            hold_2 = in_time+Hold_time+1.5                
            relax = hold_2+Relax_time+0.5            
            end = relax+Ending_time                
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/end)*718+12))
            bar_matrix.append(int((up/end)*718+12))
            bar_matrix.append(int((hold_1/end)*718+12))
            bar_matrix.append(int((in_time/end)*718+12))
            bar_matrix.append(int((hold_2/end)*718+12))
            bar_matrix.append(int((relax/end)*718+12))

        elif mode == "auto":
            bar_matrix_1 = self.calculate_bar("up")
            bar_matrix_2 = self.calculate_bar("in")
            bar_matrix_3 = self.calculate_bar("upin")

            i = 0
            while i < 5:
                bar_matrix_2[i] += 730
                i+=1

            j = 0
            while j < 7:
                bar_matrix_3[j] += 1460
                j+=1

            bar_matrix = [bar_matrix_1, bar_matrix_2, bar_matrix_3]

            for i in range(1, 5):
                bar_matrix_1[i] = (bar_matrix_1[i]/bar_matrix_3[6])*718
            for i in range(0, 5):
                bar_matrix_2[i] = (bar_matrix_2[i]/bar_matrix_3[6])*718
            for i in range(0, 7):
                bar_matrix_3[i] = (bar_matrix_3[i]/bar_matrix_3[6])*718
        
        return bar_matrix


    def add_progess_bar(self, bar_max):
        # delete all previous bar
        if self.is_trial2_in:
            self.delete_in_bar()
        if self.is_trial2_up:
            self.delete_up_bar()
        if self.is_trial2_upin:
            self.delete_upin_bar()
        self.title_2_fg.destroy()

        # start a new bar
        self.title_2_fg = ttk.Floodgauge(self.trial2_exp_lf, bootstyle=INFO, length=720, maximum=bar_max, font=("Calibri", 12, 'bold'),)
        self.title_2_fg.grid(row=self.trial2_row+6, column=0, columnspan=5, padx=5, pady=3)  
        self.title_2_fg.start()         

    def automatic_bar(self):
        self.up_bar()
        self.in_bar()
        self.upin_bar()
    


    def up_bar(self):
        self.trial2_up_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_up_1.place(x=self.trial2_up_pos[0],y=525)  

        self.trial2_up_2 = ttk.Label(self.frame3, text="| up ",font=("Calibri", 10, "bold"))
        self.trial2_up_2.place(x=self.trial2_up_pos[1],y=525)  

        self.trial2_up_3 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_up_3.place(x=self.trial2_up_pos[2],y=525)  

        self.trial2_up_4 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_up_4.place(x=self.trial2_up_pos[3],y=525) 

        self.trial2_up_5 = ttk.Label(self.frame3, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_up_5.place(x=self.trial2_up_pos[4],y=525) 

        self.is_trial2_up = True

    def delete_up_bar(self):
        self.trial2_up_1.place_forget()
        self.trial2_up_2.place_forget()
        self.trial2_up_3.place_forget()
        self.trial2_up_4.place_forget()
        self.trial2_up_5.place_forget()

        self.is_trial2_up = False

    def in_bar(self):
        self.trial2_in_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_in_1.place(x=self.trial2_in_pos[0],y=525)  

        self.trial2_in_2 = ttk.Label(self.frame3, text="| in ",font=("Calibri", 10, "bold"))
        self.trial2_in_2.place(x=self.trial2_in_pos[1],y=525)  

        self.trial2_in_3 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_in_3.place(x=self.trial2_in_pos[2],y=525)  

        self.trial2_in_4 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_in_4.place(x=self.trial2_in_pos[3],y=525) 

        self.trial2_in_5 = ttk.Label(self.frame3, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_in_5.place(x=self.trial2_in_pos[4],y=525) 

        self.is_trial2_in = True

    def delete_in_bar(self):
        self.trial2_in_1.place_forget()
        self.trial2_in_2.place_forget()
        self.trial2_in_3.place_forget()
        self.trial2_in_4.place_forget()
        self.trial2_in_5.place_forget()

        self.is_trial2_in = False


    def upin_bar(self):
        self.trial2_upin_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial2_upin_1.place(x=self.trial2_upin_pos[0],y=525)  

        self.trial2_upin_2 = ttk.Label(self.frame3, text="| up ",font=("Calibri", 10, "bold"))
        self.trial2_upin_2.place(x=self.trial2_upin_pos[1],y=525)  

        self.trial2_upin_3 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_upin_3.place(x=self.trial2_upin_pos[2],y=525)  

        self.trial2_upin_4 = ttk.Label(self.frame3, text="| in ",font=("Calibri", 10, "bold"))
        self.trial2_upin_4.place(x=self.trial2_upin_pos[3],y=525)  

        self.trial2_upin_5 = ttk.Label(self.frame3, text="| hold ",font=("Calibri", 10, "bold"))
        self.trial2_upin_5.place(x=self.trial2_upin_pos[4],y=525)  

        self.trial2_upin_6 = ttk.Label(self.frame3, text="| Relax ",font=("Calibri", 10, "bold"))
        self.trial2_upin_6.place(x=self.trial2_upin_pos[5],y=525) 

        self.trial2_upin_7 = ttk.Label(self.frame3, text="| End ",font=("Calibri", 10, "bold"))
        self.trial2_upin_7.place(x=self.trial2_upin_pos[6],y=525) 

        self.is_trial2_upin = True

    def delete_upin_bar(self):
        self.trial2_upin_1.place_forget()
        self.trial2_upin_2.place_forget()
        self.trial2_upin_3.place_forget()
        self.trial2_upin_4.place_forget()
        self.trial2_upin_5.place_forget()
        self.trial2_upin_6.place_forget()
        self.trial2_upin_7.place_forget()

        self.is_trial2_upin = False

    # ---------------------------------------functions in frame 3---------------------------------------


    # def close(self):
    #     self.transmit("EXIT", None)
    #     self.master.destroy()


    # def checkFields(self):
    #     result = []
    #     for i in range(4):
    #         result.append(self.subject_result[i].get())
    #     for i in range(4):
    #         result.append(self.jaco_result[i].get())
    #     for i in range(2):
    #         result.append(self.max_result[i].get())
    #     is_corret = True
    #     for i in result:
    #         if i == '':
    #             self.showError()
    #             break

    # def EF_maxSubmit(self):
    #     self.count_max += 1
    #     print(self.count_max)
    #     maxSaved = []
    #     maxSaved.append(self.max_result[0].get())
    #     is_corret = True
    #     print(maxSaved)
    #     j = 0
    #     for i in maxSaved:
    #         if i == '':
    #             j += 1
    #         if j >= 3:
    #             self.showError()
    #             is_corret = False
    #             break
    #     if is_corret:
    #         self.label1 = ttk.Label(self.frame2, text='Successfully Input !', bootstyle=SUCCESS)
    #         self.label1.grid(row=4, column=0)
    #         maxFinal = dict(zip(self.maxInfo, maxSaved))
    #         self.transmit("Maxes", maxFinal)

    # def SABD_maxSubmit(self):
    #     self.count_max += 1
    #     print(self.count_max)
    #     maxSaved = []
    #     for i in range(3):
    #         maxSaved.append(self.max_result[i].get())
    #     is_corret = True
    #     print(maxSaved)
    #     j = 0
    #     for i in maxSaved:
    #         if i == '':
    #             j += 1
    #         if j >= 3:
    #             self.showError()
    #             is_corret = False
    #             break
    #     if is_corret:
    #         self.label1 = ttk.Label(self.frame2, text='Successfully Input !', bootstyle=SUCCESS)
    #         if maxSaved[0] != ''and maxSaved[1] == ''and maxSaved[2] == '':
    #             self.label1.grid(row=4, column=0)
    #         elif maxSaved[1] != ''and maxSaved[2] == '':
    #             self.label1.grid(row=4, column=1)
    #         else:
    #             self.label1.grid(row=4, column=2)
    #         maxFinal = dict(zip(self.maxInfo, maxSaved))
    #         self.transmit("Maxes", maxFinal)

    # def start(self):
    #     generalSaved = []
    #     if self.checkFields():
    #         self.showError()
    #     else:
    #         for child in self.frame1.winfo_children():
    #             if child.winfo_class() == 'Entry':
    #                 generalSaved.append(child.get())
    #         generalFinal = dict(zip(self.maxInfo, generalSaved))
    #         self.transmit("Start", generalFinal)
    #         self.label1 = ttk.Label(self.frame2, text='Starting the trial', bootstyle=SUCCESS)
    #         self.label1.grid(row=6, column=0)

    # def pause(self):
    #     self.pauseFlag = not(self.pauseFlag)
    #     self.transmit("Pause", self.pauseFlag)

    # def end(self):
    #     self.transmit("End", 'end')

    # def save(self):
    #     if self.checkFields_frame1():
    #         self.showError()
    #     else:
    #         self.transmit("Save", "save")

    # def erase(self):
    #     self.count_max += 1
    #     self.label1 = ttk.Label(self.frame2, text='Clear the data', bootstyle=WARNING)
    #     self.label1.grid(row=8, column=0)

    #     self.label2 = ttk.Label(self.frame2, text='The value of MVT_EF is', bootstyle=WARNING)
    #     self.label2.grid(row=self.count_max+8, column=0)
    #     self.transmit("Erase", 'erase')


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
