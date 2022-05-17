from multiprocessing import Process, Queue
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import time

class GUI:
    def __init__(self, master, conn, in_conn=None):
        # queues for multiprocessing
        self.data_queue = conn
        self.in_queue = in_conn

        self.master = master
        self.notebk = ttk.Notebook(self.master)

        # Tabs for each section
        self.frame1 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame2 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame3 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame4 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame5 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)

        self.notebk.add(self.frame1, text = 'Constant')
        self.notebk.add(self.frame2, text = 'Trial Type 1: Maximum measurements')
        self.notebk.add(self.frame3, text = 'Trial Type 2: Pre-motor assessment')
        self.notebk.add(self.frame4, text = 'Trial Type 3: Matching trials')
        self.notebk.add(self.frame5, text = "Trial Type 4: Baseline sEMG's")
        self.notebk.pack(expand = 1, fill="both")

        # --------------------------- Frame 1 ----------------------------------------------
        self.title = ttk.Label(self.frame1, text="-----------------------------------Please Input the Subject Information-----------------------------------", bootstyle=DANGER)
        self.title.grid(column=0, row=0, columnspan=4, padx=5, pady=5)
        # Subject Info Pane
        self.subjectInfo = ['Subject Number', 'Age', 'Gender', 'Subject Type', 'Disabetes', 'Years since stroke', 
                             'Dominant Arm', 'Testing Arm']

        self.subject_result = []
        # Text entry fields
        for i in range(len(self.subjectInfo)):
            ttk.Label(self.frame1, text=self.subjectInfo[i]).grid(row=i+1, column=0, padx=5, pady=5)
            if self.subjectInfo[i] not in ['Gender', 'Disabetes', 'Dominant Arm', 'Testing Arm']:
                e1 = ttk.Entry(self.frame1,show=None)
                e1.grid(row=i+1, column=1, padx=5, pady=5)
                self.subject_result.append(e1)
        
        # Option Menus
        # Gender
        self.genders_StinngVar = ttk.StringVar(self.master)
        self.genders_First = 'Select a gender'
        self.genders_StinngVar.set(self.genders_First)
        self.genders_Type = ["Male", "Female", "Other"]
        self.genders_Menu = ttk.OptionMenu(self.frame1, self.genders_StinngVar, self.genders_Type[0], *self.genders_Type,)
        self.genders_Menu.grid(row=3, column=1, padx=5, pady=5)
    
        # Disabetes
        self.disabetes_StinngVar = ttk.StringVar(self.master)
        self.disabetes_First = 'YES/NO'
        self.disabetes_StinngVar.set(self.disabetes_First)
        self.disabetes_Type = ['YES','NO']
        self.disabetes_Menu = ttk.OptionMenu(self.frame1, self.disabetes_StinngVar, self.disabetes_Type[0], *self.disabetes_Type)
        self.disabetes_Menu.grid(row=5, column=1, padx=5, pady=5)

        # Dominant Arm
        self.domArm_StinngVar = ttk.StringVar(self.master)
        self.domArm_First = 'Left/Right'
        self.domArm_StinngVar.set(self.domArm_First)
        self.domArm_Type = ['Left','Right']
        self.domArm_Menu = ttk.OptionMenu(self.frame1, self.domArm_StinngVar, self.domArm_Type[0], *self.domArm_Type)
        self.domArm_Menu.grid(row=7, column=1, padx=5, pady=5)

        # Test Arm
        self.TestArm_StinngVar = ttk.StringVar(self.master)
        self.TestArm_First = 'Left/Right'
        self.TestArm_StinngVar.set(self.TestArm_First)
        self.TestArm_Type = ['Left','Right']
        self.TestArm_Menu = ttk.OptionMenu(self.frame1, self.TestArm_StinngVar, self.TestArm_Type[0], *self.TestArm_Type)
        self.TestArm_Menu.grid(row=8, column=1, padx=5, pady=5)

        # Submit subject information
        self.jacobSub = ttk.Button(self.frame1, text="Submit", bootstyle=(INFO, OUTLINE), command=self.Subject_Submit)
        self.jacobSub.grid(row=9,column=1, padx=5, pady=5)
       
        # Input Jacobean
        self.title = ttk.Label(self.frame1, text="-----------------------------------Please Input the Jacobean Constant-----------------------------------", bootstyle=DANGER)
        self.title.grid(row=10, column=0,columnspan=4, padx=5, pady=5)

        # Jacobean Constants Pane
        self.jacobInfo = ["Shoulder Abduction Angle (degree)","Elbow Flexion Angle (degree)","Arm Length (m)",
                          "Midload cell to elbow joint (m)"]

        self.jaco_result = []
        for i in range(len(self.jacobInfo)):
            ttk.Label(self.frame1, text=self.jacobInfo[i]).grid(row=i+11, column=0, padx=5, pady=5)
            e2 = ttk.Entry(self.frame1,show=None)
            e2.grid(row=i+11, column=1, padx=5, pady=5)
            self.jaco_result.append(e2)

        # Submit
        self.subStringVars = [self.genders_StinngVar, self.disabetes_StinngVar, self.domArm_StinngVar, self.TestArm_StinngVar]
        self.subFirsts = [self.genders_First, self.disabetes_First, self.domArm_First, self.TestArm_First]

        self.jacobSub = ttk.Button(self.frame1, text="Submit and Save", bootstyle=(INFO, OUTLINE), command=self.jacobSubmit)
        self.jacobSub.grid(row=len(self.jacobInfo)+11,column=1, padx=5, pady=5)

        self.quit = ttk.Button(self.frame1, text='Exit', command=self.close)
        self.quit.grid(row=len(self.jacobInfo)+11, column=3, padx=5, pady=5)

        # --------------------------- Frame 2 ----------------------------------------------
        # Title
        self.title = ttk.Label(self.frame2, text="------------------------------Trial Type 1: Maximum measurements (sEMGs, elbow and shoulder torques)------------------------------", bootstyle=DANGER)
        self.title.grid(row=0, column=0, columnspan=4, padx=5, pady=5)

        # set initial value of MVT
        self.setInfo = ["SET 1 Max torque flexion paretic", "SET 2 Max torque shoulder abduction", "SET 3 Synergy while holding 40% Max Shoulder Abduction"]
        self.maxInfo = ["Input a initial value of MVT_EF (elbow flexion)","Input a initial value of MVT_SABD (shoulder abduction)", "Input a initial value of EMG"]

        self.count_max = 0

        ### MVT_EF
        self.EF_row = 1
        ttk.Label(self.frame2, text=self.setInfo[0]).grid(row=self.EF_row, column=0, padx=5, pady=5)
        ttk.Label(self.frame2, text=self.maxInfo[0]).grid(row=self.EF_row+1, column=0, padx=5, pady=5)
        self.EF_data = ttk.Entry(self.frame2,show=None)
        self.EF_data.grid(row=self.EF_row+2, column=0, padx=5, pady=5)

        # submit EF
        self.MVTSub = ttk.Button(self.frame2, text="Start", command=self.EF_maxSubmit)
        self.MVTSub.grid(row=self.EF_row+3,column=0, padx=5, pady=5)
        
        # record
        self.save = ttk.Button(self.frame2, text='Record', command=self.EF_record)
        self.save.grid(row=self.EF_row+8, column=0, padx=5, pady=5)

        ##########################################Fake##############################
        # ### MVT_extension
        # self.EF_row = 1
        # ttk.Label(self.frame2, text=self.setInfo[1]).grid(row=self.EF_row, column=1, padx=5, pady=5)
        # ttk.Label(self.frame2, text=self.maxInfo[1]).grid(row=self.EF_row+1, column=1, padx=5, pady=5)
        # self.EF_data = ttk.Entry(self.frame2,show=None)
        # self.EF_data.grid(row=self.EF_row+2, column=1, padx=5, pady=5)

        # # submit EF
        # self.MVTSub = ttk.Button(self.frame2, text="Start", command=self.EF_maxSubmit)
        # self.MVTSub.grid(row=self.EF_row+3,column=1, padx=5, pady=5)
        
        # # record
        # self.save = ttk.Button(self.frame2, text='Record', command=self.EF_record)
        # self.save.grid(row=self.EF_row+8, column=1, padx=5, pady=5)
    
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
        self.quit = ttk.Button(self.frame2, text='Exit', command=self.close)
        self.quit.grid(row=30, column=2, padx=5, pady=5)


        # --------------------------- Frame 3 ----------------------------------------------
        self.frame3_row = 0
        self.trial2_maxinfo = ["Maximum elbow flexion value"]
        # Title
        self.title = ttk.Label(self.frame3, text="------------------------------Trial Type 2: Pre-motor assessment------------------------------", bootstyle=DANGER)
        self.title.grid(row=self.frame3_row, column=0, columnspan=4, padx=5, pady=5)

        # description
        self.description_2 = ttk.Label(self.frame3, text="Description: This section is used to do a pre-motor assessment, the subject will do a small test with 25% MVT", bootstyle=PRIMARY)
        self.description_2.grid(row=self.frame3_row+1, column=0, columnspan=4, padx=5, pady=5)

        # INPUT MVT
        self.input_2 = ttk.Label(self.frame3, text="Input the maximum elbow flexion value: ")
        self.input_2.grid(row=self.frame3_row+2, column=0, padx=5, pady=5)

        self.input_2_data = ttk.Entry(self.frame3,show=None)
        self.input_2_data.grid(row=self.frame3_row+2, column=1, padx=5, pady=5)

        # submit EF
        self.MVTSub = ttk.Button(self.frame3, text="Start", command=self.trial2_Submit)
        self.MVTSub.grid(row=self.frame3_row+2,column=2, padx=5, pady=5)


        # End 
        self.quit = ttk.Button(self.frame3, text='Exit', command=self.close)
        self.quit.grid(row=30, column=2, padx=5, pady=5)



    # Helper functions
    def transmit(self, header, information):
        self.data_queue.put((header, information))

    def showError(self):
        print("retrycancel: ",Messagebox.show_error(title='Oh no', message="All fields should be filled"))

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
            self.label1 = ttk.Label(self.frame1, text='Successfully Input !', bootstyle=SUCCESS)
            self.label1.grid(row=9, column=2)
            for i in self.subStringVars:
                subjectSaved.append(i.get())
            
            # reset the subject saved list
            disabtes = subjectSaved.pop(2)
            subject_type = subjectSaved.pop(2)
            subjectSaved.insert(3, disabtes)
            subjectSaved.insert(5, subject_type)
            # zip
            subjectFinal = dict(zip(self.subjectInfo, subjectSaved))
            self.transmit("Subject Info", subjectFinal)

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
            self.label1 = ttk.Label(self.frame1, text='Successfully Input !', bootstyle=SUCCESS)
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
            self.label1 = ttk.Label(self.frame2, text='Please push the sensor', bootstyle=DANGER)
            self.label1.grid(row=self.EF_row+6, column=0)

            
    def EF_record(self):
        self.label1.grid_forget()
        if self.EF_data.get() == '':
            self.showError()
        else:
            self.count_max += 1
            if not self.in_queue.empty():
                self.EF_queue = self.in_queue.get_nowait()
            else:
                print("Empty queue")
            self.label2 = ttk.Label(self.frame2, text='Trial '+ str((self.count_max)/2) + '  MVT_EF: '+str(list(self.EF_queue)[3]), bootstyle=SUCCESS)
            self.label2.grid(row=self.count_max+self.EF_row+9, column=0)

    # ---------------------------------------functions in frame 3---------------------------------------

    def trial2_Submit(self):
        trial2_saved = []
        trial2_saved.append(self.input_2_data.get())
        if self.input_2_data.get() == '' or self.checkFields_frame1():
            self.showError()
        else:
            # set the MVT_EF max value
            trial2_maxFinal = dict(zip(self.trial2_maxinfo, trial2_saved))
            self.transmit("trial2_max", trial2_maxFinal)

    # close the window
    def close(self):
        self.transmit("Close", "close")







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
