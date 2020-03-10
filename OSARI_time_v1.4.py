"""
Open-Source Anticipated Response Inhibition (OSARI) 
Created in PsychoPy v3.1.2

Written by: Rebecca J Hirst [1] Rohan Puri [2]
Edited by: Jason L He [3]

[1] Trinity College Institute of Neuroscience, Trinity College Dublin
[2] University of Tasmania
[3] John Hopkins School of Medicine 

Mail to Author:  HirstR@tcd.ie or rj.hirst@hotmail.co.uk
Version 1.3;
Create Date 04062019;
Last edited 110220

References:
    
Guthrie, M. D., Gilbert, D. L., Huddleston, D. A., Pedapati, E. V., Horn, P. S., Mostofsky, S. H., & Wu, S. W. (2018). 
Online Transcranial Magnetic Stimulation Protocol for Measuring Cortical Physiology Associated with Response Inhibition.
Journal of Visualized Experiments, (132), 1-7. http://doi.org/10.3791/56789

He, J. L., Fuelscher, I., Coxon, J., Barhoun, P., Parmar, D., Enticott, P. G., & Hyde, C. (2018). 
Impaired motor inhibition in developmental coordination disorder. Brain and Cognition, 127(August),
23-33. http://doi.org/10.1016/j.bandc.2018.09.002

To Do:
    Add triggers for EEG/TMS (from final column of input file)
    Implement KeyBoard module 
Input (optional):
    
    txt file contianing 3 columns:
        Col 1: Trial n
        Col 2: Trial type (0 = StopS, 1 = go)
        Col 3: Stop time
        Col 4: Trigger time (time relative to start of trial) 
        
Output:
    
    Block: block number 
    
    TrialType: Practice or real trial 
    
    Trial: Trial number_text
    
    Signal: 1 = Go
            0 = Stop
    
    Response: What the participants response was ( 0 = no lift, 1 = lift)
    
    RT: Lift time of participants relative to the starting line (to 2 decimal places)
    
    SSD: Stop Signal Distance (relative to starting line) if the trial was a stop trial.
    Note: 
        Make sure the resolution of "testMonitor" in monitor centre matches actual screen resolution 
"""
# --------------------------------------------------------------
#                     Import modules                       
# --------------------------------------------------------------
from __future__ import absolute_import, division
from psychopy import gui, visual, core, data, event
import numpy as np  # whole numpy lib is available, prepend 'np.'
import os  # handy system and path functions
import sys  # to get file system encoding
import pyglet
import math
from psychopy.hardware import keyboard
_thisDir = os.path.dirname(os.path.abspath(__file__))
os.chdir(_thisDir)

# set the keyboard 
kb = keyboard.Keyboard(bufferSize=10, waitForStart=True)

# --------------------------------------------------------------
#                     Task parameters                           
# This section presents users with options for task parameters  
# in the form of a Graphic User Interface (GUI).                
# Info gathered about the participant and about the task     
# The parameters set here are also used to set several aspects  
# of the stimuli (i.e. bar height)                              
#                                                               
# --------------------------------------------------------------

#About participant
expInfo={'Participant ID':0000, 'Age (Years)':00, 'Sex':['F', 'M', 'Prefer not to say'], 
    'Default parameters?':True, 'Spaceship':False}
expName='OSARI'
dlg=gui.DlgFromDict(dictionary=expInfo, title='Participant Information', 
    tip={'Default parameters?': 
        'This will run the behavioural task with no additional options'})
if dlg.OK ==False: core.quit()
expInfo['date'] = data.getDateStr()

# About the task 
# Here we have two dictionaries, "taskInfo_brief" contains the info that is presented to the user as default
# "task_info" is presented if the user selects that they do not want to default parameters.
taskInfo_brief={'Count down':True,'Trial by trial feedback':True, 'Step size (ms)':25, 'Stop limit (ms)':150, 
    'n_go_trials (per block)':48, 'n_stop_trials (per block)':16
        , 'n blocks':3, 'practice trials':True, 'n practice go trials':5, 
        'n practice stop trials':3, 'Full Screen':True, 'Total bar height (in cm)':15}

# "Bar_top" is how many cm above the point of fixation the top of the bar will be drawn 
# depending on what size the user specified. This assumes the user always wants the bar to be centred
# on the point of fixation. 
Bar_top=taskInfo_brief['Total bar height (in cm)']/2

# "Target_pos" is where the target line will be drawn. This is currently hard coded as 80%
# of the total bar length (hence why total bar height is multiplied by .8)
Target_pos=(.8*taskInfo_brief['Total bar height (in cm)'])-Bar_top

# "taskInfo" gives the users a further opportunity to specify more task parameters (but not in GUI)
taskInfo={'Bar base below fixation (cm)':Bar_top, 'Bar width (cm)':3, 
    'Bar top above fixation (cm)':Bar_top, 'Target line width (cm)':5, 
        'Target line above fixation (cm)':Target_pos, 'rise velocity (cm/sec)':15
        , 'StopS start pos. (ms)':300, 'trial length (max trial duration in seconds)':1,
        'StopS start pos. (seconds)':.3}#<-----------------------------do you want this in ms?

# "trial_length" is the max duration of a trial in seconds, this should be the amount of time it 
# takes the filling bar to fill to the top. 
trial_length=taskInfo['trial length (max trial duration in seconds)']
bar_height = taskInfo_brief['Total bar height (in cm)']

#The time taken to get to the target line should be 80% of the total trial time <------------ this substituted "Target_pos" in the time approach (delete Target_pos later)
Target_time=(.8*taskInfo['trial length (max trial duration in seconds)'])

#Check if user ticked for use of default parameters. If not present in depth task parameter options.
if not expInfo['Default parameters?']:
    dlg=gui.DlgFromDict(dictionary=taskInfo_brief, title='Experiment Parameters',
        tip={
        'Count down':'Do you want a countdown before the bar starts filling?',
        '% StopS':'Percentage of trials that are StopS, remember to ensure percentage is compatible with n trials',
        'n trials':'Total number of main trials', 
        'Step size (ms)':'If participant fails to stop the next Stop will be this much earlier in ms (i.e. staircase step size)', 
        'Stop limit (ms)':'What is the closest to the target the StopS trial can be?'})
    if dlg.OK ==False: core.quit()

# --------------------------------------------------------------
#                     Hardware parameters                       
# This section presents users with options for hardware         
# parameters. For example if they want to send triggers ect.    
# This also gives the user the chance to import a txt file      
# with preset trials. This is useful if the user wants a set    
# trial order (e.g. to pseudorandomise in advance or to present
# triggers on set trial types).                                 
#                                                               
# --------------------------------------------------------------

#Set up the window in which we will present stimuli
win = visual.Window(
    fullscr=taskInfo_brief['Full Screen'],
    winType='pyglet',
    monitor='testMonitor', color=[-1,-1,-1], colorSpace='rgb',
    blendMode='avg', mouseVisible = False, allowGUI=False)
    
hardwareInfo={'Parallel port triggers':False, 'Import trial info file':False, 
    'Trigger file path':'example_input.txt'}
if not expInfo['Default parameters?']:
    dlg=gui.DlgFromDict(dictionary=hardwareInfo, title='Hardware requirements')
    if dlg.OK ==False: core.quit()

#get the trigger file 
if hardwareInfo['Import trial info file']:
    b = open(hardwareInfo['Trigger file path'], "r").readlines()
    line = b[0].split()#work through each row by doing this 
    line[0]#get each col value for each trial by doing this 


# --------------------------------------------------------------
#                     Trial parameters                       
# This section sets the structure of the trials either based on
# an imported .txt file or based on the parameters set in the   
# GUI.                                                          
#                                                               
# --------------------------------------------------------------

#check if we should use an imported txt file or the GUI input
if hardwareInfo['Import trial info file']:
    n_trials=len(b)
    trials=[]
    stoptimes=[]
    for trial in range(0, len(b)):
        line = b[trial].split()
        trials.append(int(line[1]))#the info regarding the trial type is in the second column
        stoptimes.append(float(line[2]))#the info regarding the stoptime is in the third column
else:
    trials=[0]*taskInfo_brief['n_stop_trials (per block)']+[1]*taskInfo_brief['n_go_trials (per block)']

# Randomly shuffle the trials
# Note: this will not randomise the trials if an imported file is used. 
if not hardwareInfo['Import trial info file']:
    np.random.shuffle(trials)

#Create practice trials and associated instructions
#Note: practice trials are only created if specified.
if taskInfo_brief['practice trials']:
    #Add on the practice trials to the list of trials 
    practice_trials =[1]*taskInfo_brief['n practice go trials']+[0]*taskInfo_brief['n practice stop trials']
    trials_no_prac=trials
    trials=practice_trials+trials
    practice_go_inst=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
        text="Ready for %s practice Go trials?"%(taskInfo_brief['n practice go trials']), units='cm' )
    practice_stop_inst=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
        text="Ready for %s practice Stop trials?"%(taskInfo_brief['n practice stop trials']), units='cm' )
    understand=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
        text="Do you understand the task? (Y/N)", units='cm' )

# --------------------------------------------------------------
#                    Data output parameters                     
# This section specifies the details of where the data will be  
# saved, including filenames ect. Two folders are created "data"
# contains all task related data and "logfiles" which contain   
# additional details on the task parameters and techy details   
# such as if any frames were dropped.                           
#                                                               
# --------------------------------------------------------------

#Check if a "data" folder exists in this directory, and make one if not.
if not os.path.exists(_thisDir + os.sep +'data/'):
    print('Data folder did not exist, making one in current directory')
    os.makedirs(_thisDir + os.sep +'data/')
    

#Create the name of te output file. "Output" is the output file.
Output = _thisDir + os.sep + u'data/OSARI_%s_%s_%s' % (expInfo['Participant ID'], 
    expName, expInfo['date'])
with open(Output+'.txt', 'a') as b:
    b.write('Block	TrialType	Trial	Signal	Response	RT	SSD\n')
    

#Check if a "logfiles" folder exists in this directory, and make one if not.
if not os.path.exists(_thisDir + os.sep +'logfiles/'):
    print('Logfile folder did not exist, making one in current directory')
    os.makedirs(_thisDir + os.sep +'logfiles/')

# Measure the monitors refresh rate
expInfo['frameRate'] = win.getActualFrameRate()
#"frame_dur" = the duration of a single frame
frame_dur=1000/expInfo['frameRate']

#print out useful info on frame rate for the interested user
print('Monitor frame rate is %s' %(expInfo['frameRate']))


Target_pos_adjusted=taskInfo['Target line above fixation (cm)']

stoptime=taskInfo['StopS start pos. (ms)']
stoptime=taskInfo['StopS start pos. (seconds)']

stepsize = taskInfo_brief['Step size (ms)']/1000

stoplimit = taskInfo_brief['Stop limit (ms)']

# --------------------------------------------------------------
#                   Keyboard parameters                         
# This section specifies the details of how we will check for   
# key presses and key lifts.
# Note: 
#Known issues with using iohub on Mac with security settings 
#Bypass method noted on discourse page at: https://discourse.psychopy.org/t/tracking-key-release/1099
#                                                               
# --------------------------------------------------------------

key=pyglet.window.key
keyboard = key.KeyStateHandler()
win.winHandle.push_handlers(keyboard)

# --------------------------------------------------------------
#                   Stimulus parameters                         
#                                                               
# --------------------------------------------------------------


# ----------------- Instructions--------------------------------
# --------------------------------------------------------------

# Instructions
Main_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="Press and hold the space key untill the bar reaches the target\n\nIf the bar stops rising keep holding the space key", units='cm')
if expInfo['Spaceship']:
    Main_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
        text="Help the alien land his ship!\n\nPress and hold the space key untill the yellow on the UFO line reaches the yellow target line\n\nIf the UFO stops rising keep holding the space key!", units='cm')
practice_prepare = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="First lets practice!", units='cm')
PressKey_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="Press and hold the space key when ready!", units='cm')
TooSoon_text = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! Finger lifted too soon!\nPress space to restart countdown" , units='cm')
incorrectstop = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! Bar full! Button held too long" , units='cm')
incorrectgo = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! That was a Stop trial" , units='cm')
correctstop=visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Correct stop!" , units='cm')
wrongKey=visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="WrongKey - Please press the space key", units='cm' )
countdown_clock=core.Clock()
number_text = visual.TextStim(win, pos=[0, 0],height=.1, color=[-1,-1,-1], text="1")

# -------------------- Countdown--------------------------------
# --------------------------------------------------------------
# A function to count down the start of the trial and warn if key is lifted too soon
def countdown():
    countdown_clock.reset()
#    while countdown_clock.getTime()<4:#whilst less than 4 seconds
    keydown=0
    #kb.clearEvents () #clear the events cache of previous events (i.e. lift events) 
    while int(countdown_clock.getTime())<4:
        remainingKeys = kb.getKeys(keyList=['space', 'escape'], waitRelease=False, clear=False)
        number_text.text="%s"%(3-int(countdown_clock.getTime()))
        if remainingKeys:# if a key was pressed <------------------------make this specific to space once integrates 
            keydown=1
            for key in remainingKeys:
                if key.duration:
                    keydown = 0 # a key has been lifted
                    kb.clearEvents () #clear the key events
                    kb.clock.reset() #reset the keyboard clock
                    TooSoon_text.draw() #tell the participant they lifted their finger too soon (during the countdown)
                    win.flip() # draw the "too soon" message
                    k = event.waitKeys() # wait for the key to be pressed again 
                    if k[0]=='escape':#make sure the user can still quit in this loop
                        print('User pressed escape, quiting now')
                        win.close()
                        core.quit()
                    countdown_clock.reset() # reset the countdown clock 
        Bar.draw()
        if expInfo['Spaceship']:
            Spaceship.draw()
        targetLine.draw()
        if int(countdown_clock.getTime())<3:
            number_text.draw()
        fillBar.draw()
        win.flip()

# ----------------- Filling bar---------------------------------
# --------------------------------------------------------------
# Specify the filling and static bar 
bar_width_vert1=0-(taskInfo['Bar width (cm)']/2)
bar_width_vert2=(taskInfo['Bar width (cm)']/2)

# "vert" = vertices (corners) of filling bar in x y coordinates ([0, 0] = centre)
vert = [(bar_width_vert1,0-taskInfo['Bar base below fixation (cm)']), (bar_width_vert1,0-taskInfo['Bar base below fixation (cm)']+.01), 
        (bar_width_vert2,0-taskInfo['Bar base below fixation (cm)']+.01), (bar_width_vert2,0-taskInfo['Bar base below fixation (cm)'])]

original_vert=vert

fillBar= visual.ShapeStim(win, fillColor='skyblue', lineWidth=0, opacity=1, units='cm', vertices=vert)

# ------------------ Static bar---------------------------------
# --------------------------------------------------------------
# "fullvert" = vertices of the static background bar
fullvert = [(bar_width_vert1,0-taskInfo['Bar base below fixation (cm)']),(bar_width_vert1,taskInfo['Bar top above fixation (cm)']),
        (bar_width_vert2,taskInfo['Bar top above fixation (cm)']),(bar_width_vert2,0-taskInfo['Bar base below fixation (cm)'])]

Bar = visual.ShapeStim(win, vertices=fullvert, fillColor='white', lineWidth=0, opacity=1, units='cm')

# ------------------ Target line--------------------------------
# --------------------------------------------------------------

# Specify the target line
# "TL_width_vert1" = vertices of the target line based on info in GUI 
TL_width_vert1=0-(taskInfo['Target line width (cm)']/2)
TL_width_vert2=(taskInfo['Target line width (cm)']/2)

# "targetLinevert" = vertices of the targetline
targetLinevert = [(TL_width_vert1,Target_pos_adjusted-.1),(TL_width_vert1,Target_pos_adjusted+.1),
        (TL_width_vert2,Target_pos_adjusted+.1),(TL_width_vert2,Target_pos_adjusted-.1)]

targetLine = visual.ShapeStim(win, vertices=targetLinevert, fillColor='yellow', lineWidth=0, opacity=1, units='cm')

# ---------------------- Spaceship (optional) ------------------
# --------------------------------------------------------------

# Specify the spaceship object for if people want to use a spaceship
#How high is the spaceship in cm (set the position to be the 
Spaceship_height_cm=2
#set it so that the line in the middle of the spaceship should eventually line up with the targetline 
Spaceship=visual.ImageStim(win, image='Stimuli'+os.sep+'Spaceship.png', pos=(0, vert[2][1]-(Spaceship_height_cm/2)), units='cm')
Spaceship_practice_im=visual.ImageStim(win, image='Stimuli'+os.sep+'Practice_Image.png', pos=(10, 0), units='cm')


# --------------------------------------------------------------
#                   Initialize trials                         
#                                                              
# --------------------------------------------------------------

# --------------------------------------------------------------
#Trial loop
inc=0
height = 0
correct=[]

#keep track of feedback to give individual feedback at the end
feedback_list=[]
correct_gos=0
correct_StopSs=0

count=0
#"block_count" keeps track of how many blocks there have been 
block_count=0
#"trial_count" keeps track of how many trials there have been 
trial_count=0
practice=True

# ------------------- clocks  ----------------------------------
# --------------------------------------------------------------
#A clock to keep track of the trial time 
#trialClock=core.Clock()

#control stimulus presentation based on time 
# a clock to keep track of time so we know that the top of moving bar is where it should be at that point in time
stimClock=core.Clock()


#draw instructions
Main_instructions.draw()

if expInfo['Spaceship']:
    Spaceship_practice_im.draw()

win.flip()
core.wait(1)

#wait for button press
event.waitKeys()

#give warning practice 
practice_prepare.draw()
win.flip()
#wait for button press
event.waitKeys()

ISI = 2
# --------------------------------------------------------------
# --------------------------------------------------------------
#                   START TRIALS                         
# --------------------------------------------------------------
# --------------------------------------------------------------

# ------------------- Block loop  ------------------------------
# ------------------(trial loop nested in block)----------------
for block in range(taskInfo_brief['n blocks']):
    
    # if this is not the first block (i.e. we are in t break) give the participant a 
    # break message
    if block_count>0:
        
        #set message
        Blocks_completed = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
            text="Block %s of %s complete!!\n\nPress space when ready to continue!"%(block_count, taskInfo_brief['n blocks']), units='cm')
        #draw message
        Blocks_completed.draw()
        win.flip()
        core.wait(1)
        #wait for keypress
        event.waitKeys()
    
    #note what block we are on
    block_count=block_count+1
    
# ------------------- trial loop  ------------------------------
# --------------------------------------------------------------
    # On each iteration of the trial loop we will:
    # 1. Check if this is the first block -> if it is did user request practice trials?
    #           -> if yes present go practice trials and stop practice trials (label as 
    #               practice in output (i.e. "trial_label") --> check if they understood the task --> if yes continue 
    # 2. Set the position of the SSD based on if they were correct or not on previous trial 
    # 3. participant pushes key and we start the trial 
    # 4. trial complete compile feedback and save data 
    
    for trial in trials:
        
        #note what trial we are on
        trial_count=trial_count+1
        
        #Reset the colour of the target line
        targetLine.fillColor='yellow'
        
        # ----------------------------------------------------------------------
        # ------------------- 1. trial loop Check if the user asked for practice 
        #------------------------trials and if this is the first block
        # ----------------------------------------------------------------------
        if taskInfo_brief['practice trials'] and block_count==1:
            if trial_count <=len(practice_trials):
                if trial_count==1 and practice:
                    
                    #draw practice "Go" trial instruction
                    practice_go_inst.draw()
                    trial_label='practice'
                    win.flip()
                    
                    #wait for key press
                    event.waitKeys()
                    
                elif taskInfo_brief['n practice go trials']+1==trial_count and practice:
                    
                    #draw practice "Stop" trial instruction
                    practice_stop_inst.draw()
                    trial_label='practice'
                    win.flip()
                    
                    #wait for key press
                    event.waitKeys()
            elif trial_count==taskInfo_brief['n practice go trials']+taskInfo_brief['n practice stop trials']+1 and practice:
                
                #If this is the first main trial (i.e. the trial count is 1 more than the practice trials)
                #ask the participant if they understand the task.
                understand.draw()
                win.flip()
                
                #wait for key press
                UnderstandKey = event.waitKeys(keyList=['y','n'])
                
                #check if the user understood the task, if not ('n') quit the task 
                if UnderstandKey[0] == 'n':
                    core.quit()
                    
                practice=False 
                trial_label='main'
                
                #reset the trial list to be the trials without the practice trials
                trials=trials_no_prac
                trial_count=1
                
                #reset the stop pos to be what it should be at the start
                this_stoptime=trial_length
                print('this_stoptime:',this_stoptime)
        else:
            trial_label='main'
        # ---------------------------------------------------------------
        # ------------------- 2. set position of SSD based on if previous
        #------------------------response was correct 
        # ---------------------------------------------------------------
        
        #Find out if/where the rising bar should stop on this trial based on accuracy in previous 
        #trial
        if not hardwareInfo['Import trial info file']:
            if correct == -1 and round(stoptime) == round(stoplimit):#(stoptime>stoplimit-frame_dur and stoptime<=stoplimit):
                stoptime=stoplimit
            elif correct==-1 and stoptime>stoplimit:#if they incorrectly lifted on a StopS trial (checking success count allows us to check if the trial restarted)
                stoptime=stoptime+stepsize
            elif correct ==2:#if they correctly stopped on the StopS trial
                stoptime=stoptime-stepsize
        else:
            stoptime=stoptimes[count]#index the stop time from the preset file 
        
        #reset correct 
        correct=[]
        #set the stop time based on if this is a go or StopS trial
        #"trial" = trial type. 1 = Go, 0 = Stop
        #if this is a go trial the stop time is the maximum trial time (i.e. time taken to fill bar)
        if trial==1:
            this_stoptime=trial_length
        else:
            this_stoptime = Target_time-stoptime #stop time is the trial length - the time taken to travel from the target to the top - the current step size)
            
        print('this_stoptime:', this_stoptime)
        # ---------------------------------------------------------------
        # ------------------- 3. Participant pushes key 
        #---------------------- Start of trial 
        # ---------------------------------------------------------------
        #draw instructions to hold key down
        PressKey_instructions.draw()
        win.flip()
        
        #wait for keypress
        kb.start() # we need to start watching the keyboard before a key is pressed 
        k = event.waitKeys()
        
        #check for if user wishes to esc
        if k[0]=='escape':
            print('User pressed escape, quiting now')
            win.close()
            core.quit()
            
        #reset the vertices to their begining position
        fillBar.vertices = original_vert#vert
        
        #If we have a spaceship - draw it here 
        if expInfo['Spaceship']:
           # Spaceship.pos=(0, vert[2][1]-(Spaceship_height_cm/2))
            Spaceship.pos=(0, original_vert[2][1])#<--------------------------------------------------------do we want the spaceship to be the top or on the line
        
        #Count down before trial starts
        if taskInfo_brief['Count down']:
            countdown()
        
        #Reset the trial clock to indicate start of a trial
        #trialClock.reset()
        #stimClock measures the time at the start of every frame <---------------------------------should we rename this "frameClock"?
        stimClock.reset()
        
        #Note the time that we are starting the trial
        start_time=stimClock.getTime()
        #Print for debugging
        print('start_time:', start_time)
        
        #Record the frame intervals for the interested user 
        win.frameIntervals=[]
        win.recordFrameIntervals = True
        
        #"waiting" = variable to say if we are waiting for the key to be lifted 
        waiting=1  
        height=0
        print('current vert:', vert[1][1])
        time_elapsed=(stimClock.getTime())-start_time
        win.callOnFlip(kb.clock.reset())
        #kb.clock.reset()
        while time_elapsed<trial_length and waiting==1:#whilst we are waiting for the button to be lifted 
            # Watch the keyboard for a response
            remainingKeys = kb.getKeys(keyList=['space', 'escape'], waitRelease=False, clear=False)
            
            # How much time has elapsed since the start of the trial 
            time_elapsed=(stimClock.getTime())-start_time
            
            # Calculate "height" - the current height of the bar in cm 
            # this will be added to the vertices position to adjust the size of 
            # the filling (blue) bar. 
            if time_elapsed<this_stoptime:
                height = (time_elapsed*bar_height)/trial_length
            elif time_elapsed>=this_stoptime:
              #  max_height = (time_elapsed*bar_height)/trial_length
                height = (this_stoptime*bar_height)/trial_length#max_height
#            elif time_elapsed>this_stoptime:
#                height = (this_stoptime*bar_height)/trial_length#max_height
         #   print('time elapsed:', time_elapsed) #Optional print for debugging 
         #   print('height:', height)
            
            # If a key has been pressed (i.e. there is something in the keyboard events)
            # we will draw the filling bar. This will stop if key lift detected. 
            if remainingKeys:
                
                #Draw the background bar
                Bar.setAutoDraw(True)
                #Set the vertices of the filling bar 
                vert[1]=(vert[1][0], vert[1][1]+height)#left corner
                vert[2]=(vert[2][0], vert[2][1]+height)#right corner 
                # Optional print for debuggins (prints the coordinates of the top two vertices) 
                #print('y vertices top left:', vert[1][1])
                #print('y vertices top right:', vert[2][1])
                fillBar.vertices = vert
                if expInfo['Spaceship']:
                   # Spaceship.pos=(0, vert[2][1]-(Spaceship_height_cm/2))
                    Spaceship.pos=(0, vert[2][1])#<--------------------------------------------------------do we want the spaceship to be the top or on the line
                fillBar.setAutoDraw(True) 
                # Reset vertices to original position
                vert[1]=(vert[1][0], vert[1][1]-height)# left corner
                vert[2]=(vert[2][0], vert[2][1]-height)# right corner 
                if expInfo['Spaceship']:
                    Spaceship.setAutoDraw(True)
                # Draw target line last so it overlays all stimuli
                targetLine.setAutoDraw(True)
                win.flip()
                
                for key in remainingKeys:
                    if key.duration:
                        lift_time = kb.clock.getTime()
                        print('lift time:', lift_time)
                        kb.clock.reset() #reset the keyboard clock<---------------------might want to check where we are reseting the kb clock
                        kb.clearEvents () #clear the key events
                        #say we are not waiting anymore and break the loop 
                        waiting=0 
        #stop recording frame intervals 
        win.recordFrameIntervals = False
        #if this was a stop trial then the above while loop will have broken when the stoplimit was
        #reached. but, we still want to wait untill the end of the trial to make sure they 
        #actually hold and don't lift as soon as the stop limit is reached
        # ---------------------------------------------------------------
        # ------------------- 4. trial complete 
        #---------------------- compile feedback and save data 
        # ---------------------------------------------------------------
        kb.stop() # stop watching the keyboard
        #if the bar has filled but we are still waiting for the key to lift
        if waiting==1:
            # Optional prints for debugging
            #print('current time:',(stimClock.getTime())-start_time)
            #print('trial length:',trial_length)
            lifted=0#<-------------------------------------------Are the variables lifted 
            RT='NaN'
            #if this was a go trial feedback that the participant incorrectly stopped
            if trial==1:
                feedback=incorrectstop
                # Change the colour of the target line
                targetLine.fillColor='Red'
                correct=-2
            # If this was a stop trial feedback that the participant correctly stopped
            elif trial==0:# The participant must have continued holding untill the end of the total trial length
                correct=2
                #change the colour of the target line
                targetLine.fillColor='Green'
                feedback=correctstop
                correct_StopSs=correct_StopSs+1
        # If the key was lifted before the bar filled
        else:
            # If this was a stop trial feedback that the participant incorrectly stopped
            lifted=1
            #RT=trialClock.getTime()
            RT = lift_time 
            if trial==1:# Give feedback they correctly lifted and time in ms from target
                correct=1
                feedback_ms=abs(((trial_length*.8)-lift_time)*1000)#<-------------------gives the feedback in absolute terms
                targetLine.fillColor='Green'
                correctgo = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
                text="%.0f ms from target!"%(feedback_ms), units='cm') # <--------------------------- the ".8" is hard coded here - do we want it flexible this is the proportion of the trial time where the target is 
                feedback_list.append(feedback_ms)
                if trial_label=="main":# Only add to the feedback if this is a main trial (i.e. dont count the practice trials)
                    correct_gos=correct_gos+1
                feedback=correctgo
            elif trial==0:# Give feedback they incorrectly lifted -- and this is an unsuccessfull trial, so the trial should restart (it will be noted in the output that the trial restarted)
                feedback=incorrectgo
                targetLine.fillColor='Red'
                correct=-1
        if taskInfo_brief['Trial by trial feedback']:
            feedback.setAutoDraw(True)
        win.flip()
        with open(Output+'.txt', 'a') as b:
            b.write('%s	%s	%s	%s	%s	%s	%s\n'%(block_count, trial_label, trial_count, trial, lifted, RT, this_stoptime))
        core.wait(ISI)
        # Reset visual stimuli for next trial
        feedback.setAutoDraw(False)
        targetLine.setAutoDraw(False)
        fillBar.setAutoDraw(False) 
        Bar.setAutoDraw(False)
        if expInfo['Spaceship']:
            Spaceship.setAutoDraw(False)
        count=count+1# Only add to the trial could if we have been successfull
        
    # Write a nice thank-you message and some feedback on performance
    EndMessage = visual.TextStim(win, pos=[0, 0], height=.1, color=[1,1,1],
        text="The End!\n\nAverage time from target: %.3f\n\nCorrect Go: %s out of %s\n\nCorrect Stop: %s out of %s"%(
        np.average(feedback_list), correct_gos, taskInfo_brief['n_go_trials (per block)']*taskInfo_brief['n blocks'], correct_StopSs, taskInfo_brief['n_stop_trials (per block)']*taskInfo_brief['n blocks']))
# --------------------------------------------------------------
# --------------------------------------------------------------
#                   END TRIALS                         
# --------------------------------------------------------------
# --------------------------------------------------------------

# Be nice and thank participant.
EndMessage.draw()
win.flip()

# Wait for button press
event.waitKeys()
core.quit()
