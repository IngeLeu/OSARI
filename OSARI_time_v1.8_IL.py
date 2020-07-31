"""
Open-Source Anticipated Response Inhibition (OSARI)
Created in PsychoPy v3.1.2
Written by: Rebecca J Hirst [1] Rohan Puri [2]
Edited by: Jason L He [3]
[1] Trinity College Institute of Neuroscience, Trinity College Dublin
[2] University of Tasmania
[3] John Hopkins School of Medicine
Mail to Author:  rj.hirst at hotmail.co.uk
Version 1.3;
Create Date 04062019;
Last edited 190720
References:

Guthrie, M. D., Gilbert, D. L., Huddleston, D. A., Pedapati, E. V., Horn, P. S., Mostofsky, S. H., & Wu, S. W. (2018).
Online Transcranial Magnetic Stimulation Protocol for Measuring Cortical Physiology Associated with Response Inhibition.
Journal of Visualized Experiments, (132), 1-7. http://doi.org/10.3791/56789
He, J. L., Fuelscher, I., Coxon, J., Barhoun, P., Parmar, D., Enticott, P. G., & Hyde, C. (2018).
Impaired motor inhibition in developmental coordination disorder. Brain and Cognition, 127(August),
23-33. http://doi.org/10.1016/j.bandc.2018.09.002

Input:

    3 csv files:
        practiceGoConditions.csv
        practiceMixedConditions.csv
        TestConditions.csv
    
    In all csv files each row corresponds to a trial, so number of rows will correspond to the number of trials in a block.
    0 = Go 1 = Stop 
    
Output:
    
    4 output files in format:
        OSARI_ExpH_123_OSARI_2020_Jul_19_1307.log
        OSARI_ExpH_123_OSARI_2020_Jul_19_1307.csv
        OSARI_ExpH_123_OSARI_2020_Jul_19_1307.psydat
        OSARI_ExpH_123_OSARI_2020_Jul_19_1307.txt
    
    For details on psydat and log files see 
        https://www.psychopy.org/general/dataOutputs.html#:~:text=PsychoPy%20data%20file%20(.-,psydat),python%20and%2C%20probably%2C%20matplotlib.
    
    Data is contained in the .txt and .csv files. The .txt file saves the main details of interest but csv stores further details.
    
    Block: block number

    TrialType: Practice or real trial

    Trial: Trial number_text

    Signal: 0 = Go
            1 = Stop

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
from psychopy import gui, visual, core, data, event, logging
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
# This section presents users with options to collect participant data 
# and set task parameters using a set of Graphic User Interfaces (GUI).
# --------------------------------------------------------------

# Participant information
expInfo={'Participant ID':'0000',
        'Age (Years)':'00',
        'Sex':['F', 'M', 'Prefer not to say'],
        'Default parameters?':True}
expName='OSARI'
dlg=gui.DlgFromDict(dictionary=expInfo, title='Participant Information',
    tip={'Default parameters?':
        'This will run the task with no additional options'})
if dlg.OK ==False: core.quit()
expInfo['date'] = data.getDateStr()

# Task Information
# Here we have two dictionaries, "taskInfo_brief" contains parameters that can be set by the user if they do not 
# want the default parameters - if the user wants to set parameters beyond this see "taskInfo" and set in the code.
taskInfo_brief={'Practice trials': True,
                'Count down':True,
                'Trial by trial feedback':True,
                'Method':['staircase', 'fixed'],
                'Trial order':['random', 'sequential'],
                'Step size (s)':0.025,
                'Lowest SSD (s)':0.05,
                'Highest SSD (s)': 0.775,
                'Total bar height (in cm)':15,
                'Number of Test Blocks': 3,
                'Spaceship':False,
                'Full Screen':True}

#Check if user ticked for use of default parameters. If not present in depth task parameter options.
if not expInfo['Default parameters?']:
    dlg=gui.DlgFromDict(dictionary=taskInfo_brief, title='Experiment Parameters',
        tip={
        'Count down':'Do you want a countdown before the bar starts filling?',
        'Trial by trial feedback':'Do you want participants to receive trial to trial feedback',
        'Method':'What SSD method do you want?',
        'Trial order':'Do you want trials to be in a random order or in the order you have set in the conditions .csv file [sequential]',
        'Step size (s)':'What do you want the step size to be in ms - e.g., 0.025 is 25ms',
        'Lowest SSD (s)':'The lowest the SSD can go in ms - e.g., 0.05 is 5ms',
        'Highest SSD (s)':'The highest the SSD can go in ms - e.g., 0.775 is 775ms',
        'Total bar height (in cm)':'The total height of the bar',
        'Number of Test Blocks':'Number of test blocks [i.e. number of times trials in .csv file will be repeated. to set trial number and proportion of stop vs. go adapt the .csv file]',
        'Spaceship':'Do you want to run this with a moving target image (i.e. a spaceship) ?',
        'Full Screen':'Do you want to run the task with Full Screen - recommended'})
    if dlg.OK ==False: core.quit()
else:
    #parameters with multiple options need their default selecting
    taskInfo_brief['Trial order']='random'
    taskInfo_brief['Method']='staircase'

# "Bar_top" is how many cm above the centre of the screen (x = 0 y = 0) the top of the bar will be drawn.
Bar_top=taskInfo_brief['Total bar height (in cm)']/2

# "Target_pos" is where the target line will be drawn. This is currently hard coded as 80%
# of the total bar length (i.e. total bar height is multiplied by .8)
Target_pos=(.8*taskInfo_brief['Total bar height (in cm)'])-Bar_top

# Additional parameters beyond "taskInfo_brief" can be set here (but not in GUI)
taskInfo={'Bar base below fixation (cm)':Bar_top,
          'Bar width (cm)':3,
          'Bar top above fixation (cm)':Bar_top,
          'Target line width (cm)':5,
          'Target line above fixation (cm)':Target_pos,
          'rise velocity (cm/sec)':15,
          'StopS start pos. (ms)':500,
          'trial length (max trial duration in seconds)':1,
          'StopS start pos. (seconds)':.5} 

# "trial_length" is the max duration of a trial in seconds i.e. the amount of time it
# takes the filling bar to fill to the top.
trial_length=taskInfo['trial length (max trial duration in seconds)']
bar_height = taskInfo_brief['Total bar height (in cm)']

#The time taken to get to the target line i.e. 80% of the total trial time
Target_time=(.8*taskInfo['trial length (max trial duration in seconds)'])

# --------------------------------------------------------------
#                     Hardware parameters
# This section presents users with options for hardware
# parameters. For example if they want to send triggers etc.,
#
# --------------------------------------------------------------

#Set up the window in which we will present stimuli
win = visual.Window(
    fullscr=taskInfo_brief['Full Screen'],
    winType='pyglet',
    monitor='testMonitor',
    color=[-1,-1,-1],
    colorSpace='rgb',
    blendMode='avg',
    mouseVisible = False,
    allowGUI=False,
    size=(1440, 900))

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

#Create the name of the output file. "Output" is the output file.
Output = _thisDir + os.sep + u'data/OSARI_%s_%s_%s' % (expInfo['Participant ID'],
    expName, expInfo['date'])
with open(Output+'.txt', 'a') as b:
    b.write('block	trialType	trial	signal	response	ssd	rt\n')

#Check if a "logfiles" folder exists in this directory, and make one if not.
if not os.path.exists(_thisDir + os.sep +'logfiles/'):
    print('Logfile folder did not exist, making one in current directory')
    os.makedirs(_thisDir + os.sep +'logfiles/')

# Measure the monitors refresh rate
expInfo['frameRate'] = win.getActualFrameRate()
#frame_dur=1000/expInfo['frameRate'] #"frame_dur" = the duration of a single frame

#print out useful info on frame rate for the interested user
print('Monitor frame rate is %s' %(expInfo['frameRate']))

stoptime=taskInfo['StopS start pos. (seconds)']
stepsize = taskInfo_brief['Step size (s)']
upper_ssd = taskInfo_brief['Highest SSD (s)']
lower_ssd = taskInfo_brief['Lowest SSD (s)']

#Use experiment handler with 2 loops, a practice loop and a main trial loop
Output_ExpH = _thisDir + os.sep + u'data/s_%s_%s_%s' % (expInfo['Participant ID'],
    expName, expInfo['date'])
thisExp = data.ExperimentHandler(
    name = 'OSARI', version = '1.73',
    extraInfo = taskInfo_brief, #this will save all of the user input for task info brief - might want also the full task info
        savePickle=True, saveWideText=True,
    dataFileName = Output_ExpH, autoLog = True)
# save a log file for detail verbose info
logFile = logging.LogFile(Output_ExpH+'.log', level=logging.DEBUG)
logging.console.setLevel(logging.WARNING)  # this outputs to the screen, not a file

#Input files that are used to create the trial list at the start of each block
conditions = data.importConditions('TestConditions.csv') #conditions file for the 'main trials'
practiceGoConditions = data.importConditions('practiceGoConditions.csv') #conditions file for the 'practice go trials'
practiceMixedConditions = data.importConditions('practiceMixedConditions.csv') #conditions file for the 'practice go and stop trials'

if taskInfo_brief['Practice trials']:
    prac_block_n=2 # number of practice blocks hard coded assuming we will always have 1 go block and 1 mixed block
    n_blocks = taskInfo_brief['Number of Test Blocks']+prac_block_n
else:
    prac_block_n=0
    n_blocks = taskInfo_brief['Number of Test Blocks']

#An "outerLoop" that corresponds to blocks, we use this loop to repeat sets of trials however many times we want
outerLoop = data.TrialHandler(trialList=[], nReps=n_blocks, name = 'Block')#note: nReps also includes our 2 practice blocks

#We start out experiment with the outerLoop
thisExp.addLoop(outerLoop)

# --------------------------------------------------------------
#                   Keyboard parameters
# This section specifies the details of how we will check for
# key presses and key lifts.
# Note:
#Known issues with using iohub on Mac with security settings
#Bypass method noted on discourse page at:
#https://discourse.psychopy.org/t/tracking-key-release/1099
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

#practice trial text 
understand=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
    text="Do you understand the task? (Y/N)", units='cm' )
practice_go_inst=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
    text="Lets start with some Go trials.\n Press any button to begin!", units='cm' )
practice_stop_inst=visual.TextStim(win, pos=[0, 0], height=1, color= [1,1,1],
    text="Great! Next, lets do some Go and Stop trials!\n Press any button to begin!", units='cm' )
    
# Instructions
instr_image=visual.ImageStim(win, image='Stimuli'+os.sep+'instr_image.png', units='cm')
instr_image_SS=visual.ImageStim(win, image='Stimuli'+os.sep+'instr_image_SS.png', units='cm')

Main_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="To begin a trial, press and hold the space key\n\nOn 'Go trials': release the space key at the target\n\nOn 'Stop trials': keep the space key pressed\n\n[press any key to continue]", units="cm")
if taskInfo_brief['Spaceship']:
    Main_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
        text="Help the alien land his ship!\n\nPress and hold the space key untill the yellow on the UFO line reaches the target \n\nIf the UFO stops rising keep holding the space key!\n\n[press any key to continue]", units='cm')
practice_prepare = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="First lets practice!", units='cm')
PressKey_instructions = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
    text="Press and hold the space key when you are ready!", units='cm')
TooSoon_text = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! You lifted too soon!\nPress space to restart countdown" , units='cm')
incorrectstop = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! You held the \nbutton for too long" , units='cm')
incorrectgo = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Oops! That was a Stop trial \nYou did not withold your response" , units='cm')
correctstop=visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="Correct!\nYou withheld your response" , units='cm')
wrongKey=visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
    text="WrongKey - Please press the space key", units='cm' )
countdown_clock=core.Clock()
number_text = visual.TextStim(win, pos=[0, Target_pos],height=1, color=[-1,-1,-1], text="1", units='cm')

# -------------------- Countdown--------------------------------
# --------------------------------------------------------------
# A function to count down the start of the trial and warn if key is lifted too soon
def countdown():
    countdown_clock.reset()
    keydown=0
    while int(countdown_clock.getTime())<4:
        remainingKeys = kb.getKeys(keyList=['space', 'escape'], waitRelease=False, clear=False)
        number_text.text="%s"%(3-int(countdown_clock.getTime()))
        if remainingKeys:# if a key was pressed <------------------------make this specific to space once integrates
            keydown=1
            for key in remainingKeys:
                if key.duration:
                    print(number_text.text)
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
        fillBar.draw()
        if taskInfo_brief['Spaceship']:
            Spaceship.draw()
        targetArrowRight.draw()
        targetArrowLeft.draw()
        if int(countdown_clock.getTime())<3:
            number_text.draw()
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
fullvert = [(bar_width_vert1,0-taskInfo['Bar base below fixation (cm)']),
            (bar_width_vert1,taskInfo['Bar top above fixation (cm)']),
            (bar_width_vert2,taskInfo['Bar top above fixation (cm)']),
            (bar_width_vert2,0-taskInfo['Bar base below fixation (cm)'])]

Bar = visual.ShapeStim(win, vertices=fullvert, fillColor='white', lineWidth=0, opacity=1, units='cm')

# ------------------ Target line--------------------------------
# --------------------------------------------------------------

# Specify the target width

target_width = 0.5

# Vertices of the target arrows
targetArrowRightvert = [(1.5,Target_pos),
        (1.5+target_width,Target_pos+(target_width/np.sqrt(3))),(1.5+target_width,Target_pos-(target_width/np.sqrt(3)))]
targetArrowRight = visual.ShapeStim(win, vertices=targetArrowRightvert, fillColor='yellow', lineWidth=0, opacity=1, units='cm')

targetArrowLeftvert = [(-1.5-target_width,Target_pos+(target_width/np.sqrt(3))),(-1.5-target_width,Target_pos-(target_width/np.sqrt(3))),
        (-1.5,Target_pos)]
targetArrowLeft = visual.ShapeStim(win, vertices=targetArrowLeftvert, fillColor='yellow', lineWidth=0, opacity=1, units='cm')

# ---------------------- Spaceship (optional) ------------------
# --------------------------------------------------------------

# Specify the spaceship object for if people want to use a spaceship
#How high is the spaceship in cm (set the position to be the
Spaceship_height_cm=2
#set it so that the line in the middle of the spaceship should eventually line up with the targetline
Spaceship=visual.ImageStim(win, image='Stimuli'+os.sep+'SpaceShip_scaled.png', pos=(0, vert[2][1]), units='cm')
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
#draw instructions
Main_instructions.draw()
if taskInfo_brief['Spaceship']:
    instr_image_SS.draw()
else:
    instr_image.draw()

win.flip()
core.wait(1)

#wait for button press
event.waitKeys()

#give warning practice
if taskInfo_brief['Practice trials']:
    practice_prepare.draw()
    win.flip()
    event.waitKeys()

ISI = 2
# --------------------------------------------------------------
# --------------------------------------------------------------
#                   START TRIALS
# --------------------------------------------------------------
# --------------------------------------------------------------

block_count=0 #blocks
for block in outerLoop:
    print(block)
    if block_count == 0 and taskInfo_brief['Practice trials']:
        trials = data.TrialHandler(trialList = practiceGoConditions, nReps = 1, method = taskInfo_brief['Trial order'], name = 'practiceGoTrials',autoLog = True)
    elif block_count ==1 and taskInfo_brief['Practice trials']:
        trials = data.TrialHandler(trialList = practiceMixedConditions, nReps = 1, method = taskInfo_brief['Trial order'], name = 'practiceMixedTrials', autoLog = True)
    else:
        trials = trials = data.TrialHandler(trialList = conditions, nReps = 1, method = taskInfo_brief['Trial order'], name = 'testBlocks', autoLog = True)
            #Note 1: nReps is the number of repetitions of the condition rows set in the 'practiceGoTrials', 'practiceMixedTrials' or 'TestConditions' file.
            #Users can control the number of trials by increasing the number of rows per condition in the conditions file OR ...
            #by changing the number of nReps. For example, if your conditions file has two rows (0 and 1), and your nReps is 3, you will have 6 trials
            #We recommend users change the number of trials using the conditions file rather than nReps
            #Note 2: method = 'random' randomly selects the conditions in the conditions files, you can also use 'sequential'
    thisExp.addLoop(trials)
    if block_count>2 and taskInfo_brief['Practice trials']:
        #set message
        Blocks_completed = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
            text="Block %s of %s complete!!\n\nPress space when ready to continue!"%(block_count-prac_block_n, n_blocks-prac_block_n), units='cm')
        Blocks_completed.draw()
        win.flip()
        core.wait(1)
        #wait for keypress
        event.waitKeys()
    elif not taskInfo_brief['Practice trials'] and block_count>0:
        #set message
        Blocks_completed = visual.TextStim(win, pos=[0, 0], height=1, color=[1,1,1],
            text="Block %s of %s complete!!\n\nPress space when ready to continue!"%(block_count-prac_block_n, n_blocks-prac_block_n), units='cm')
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

    #iterate through the set of trials we have been given for this block
    trial_count=0
    for thisTrial in trials:
        trial_count=trial_count+1 #count trials

        #Reset the colour of the target arrows
        targetArrowRight.fillColor='yellow'
        targetArrowLeft.fillColor='yellow'
        # ----------------------------------------------------------------------
        # ------------------- 1. trial loop Check if the user asked for practice
        #------------------------trials and if this is the first block
        # ----------------------------------------------------------------------
        if trial_count==1:
            if trials.name == 'practiceGoTrials':
                #draw practice "Go" trial instruction
                practice_go_inst.draw()
                trial_label='practice'
                win.flip()

                #wait for key press
                event.waitKeys()

            elif trials.name == 'practiceMixedTrials':

                #draw practice "Stop" trial instruction
                practice_stop_inst.draw()
                trial_label='practice'
                win.flip()

                #wait for key press
                core.wait(3)
                event.waitKeys()
            if trials.name == 'testBlocks' and  ((taskInfo_brief['Practice trials'] and block_count==3) or (taskInfo_brief['Practice trials']==False and block_count==1)):

                #If this is the first main trial (i.e. the trial count is 1 more than the practice trials)
                #ask the participant if they understand the task.
                understand.draw()

                #Reset the stop time so it doesn't carry over from the practice
                stoptime=taskInfo['StopS start pos. (seconds)']

                #Reset correct as well so that the loop to change stoptimes is not entered
                correct=[]

                win.flip()

                #wait for key press
                UnderstandKey = event.waitKeys(keyList=['y','n'])

                #check if the user understood the task, if not ('n') quit the task
                if UnderstandKey[0] == 'n':
                    core.quit()

                practice=False
                trial_label='main'

                trial_count=1

                #reset the stop pos to be what it should be at the start
                this_stoptime=trial_length
                #print('this_stoptime:',this_stoptime)
        trial_label=trials.name
        # ---------------------------------------------------------------
        # ------------------- 2. set position of SSD based on if previous
        #------------------------response was correct
        # ---------------------------------------------------------------

        #Find out if/where the rising bar should stop on this trial based on accuracy in previous
        if not taskInfo_brief['Method']=='fixed':
            if correct==-1 and round(stoptime,3) > round(lower_ssd,3):#if they incorrectly lifted on a StopS trial (checking success count allows us to check if the trial restarted)
                stoptime=stoptime-stepsize
            elif correct == -1 and round(stoptime,3) == round(lower_ssd,3):
                stoptime = lower_ssd
            elif correct ==2 and round(stoptime,3) < round(upper_ssd,3):#if they correctly stopped on the StopS trial
                stoptime=stoptime+stepsize
            elif correct == 2 and round(stoptime,3) == round(upper_ssd,3):# never equal floats in python. so we use round.
                stoptime = upper_ssd

        elif taskInfo_brief['Method']=='fixed':
            stoptime=thisTrial['fixedStopTime']
            print(stoptime)

        #reset correct
        correct=[]
        #set the stop time based on if this is a 'Go' or 'Stop' trial
        #if Signal = 0, then trial type = Go,
        #if Signal = 1, then trial type = Stop
        #if this is a go trial, the stop time is the maximum trial time (i.e. time taken to fill bar)
        Signal =thisTrial['Signal']

        if Signal==0:
            this_stoptime=trial_length
        else:
            this_stoptime = stoptime #stop time is the trial length - the time taken to travel from the target to the top - the current step size)

        #print('this_stoptime:', this_stoptime)
        # ---------------------------------------------------------------
        # ------------------- 3. Participant pushes key
        #---------------------- Start of trial
        # ---------------------------------------------------------------
        #draw instructions to hold key down
        PressKey_instructions.draw()
        win.flip()

        #wait for keypress
        kb.start() # we need to start watching the keyboard before a key is pressed
        kb.clearEvents ()
        k = event.waitKeys()

        #check for if user wishes to esc
        if k[0]=='escape':
            print('User pressed escape, quiting now')
            win.close()
            core.quit()

        #reset the vertices to their begining position
        fillBar.vertices = original_vert#vert
        if taskInfo_brief['Spaceship']:
            Spaceship.pos=(0, original_vert[2][1])

        #Count down before trial starts
        if taskInfo_brief['Count down']:
            countdown()

        targetArrowRight.setAutoDraw(True)
        targetArrowLeft.setAutoDraw(True)

        Bar.setAutoDraw(True)
        fillBar.setAutoDraw(True)
        
        # Set autoDraw for the stimulus elements before trial starts
        #   (Note: draw order is defined by the order in which setAutoDraw is called)
        if taskInfo_brief['Spaceship']:
            Spaceship.setAutoDraw(True)
        #Record the frame intervals for the interested user
        win.frameIntervals=[]
        win.recordFrameIntervals = True

        #"waiting" = variable to say if we are waiting for the key to be lifted
        waiting=1
        height=0
        #print('current vert:', vert[1][1])
        time_elapsed=0#we want this to be 0 at this point
        win.callOnFlip(kb.clock.reset)
        win.flip()
        #kb.clock.reset()
        while time_elapsed<trial_length and waiting==1:#whilst we are waiting for the button to be lifted
            # Watch the keyboard for a response
            remainingKeys = kb.getKeys(keyList=['space', 'escape'], waitRelease=False, clear=False)

            # How much time has elapsed since the start of the trial
            time_elapsed=kb.clock.getTime()
            # Calculate "height" - the current height of the bar in cm
            # this will be added to the vertices position to adjust the size of
            # the filling (blue) bar.
            if time_elapsed<this_stoptime:
                height = (time_elapsed*bar_height)/trial_length
            elif time_elapsed>=this_stoptime:
                height = (this_stoptime*bar_height)/trial_length#max_height

            # If a key has been pressed (i.e. there is something in the keyboard events)
            # we will draw the filling bar. This will stop if key lift detected.
            if remainingKeys:
                for key in remainingKeys:

                    if key.duration:
                        lift_time = kb.clock.getTime()
                        kd=key.duration
                        krt=key.rt
                        kd_start_synced=key.duration-np.abs((key.tDown-kb.clock.getLastResetTime()))#<----can just do key.duration - key.rt
                        #print('lift time:', lift_time, 'duration:', kd, 'duration_startsynced', kd_start_synced)
                        kb.clearEvents() #clear the key events
                        #say we are not waiting anymore and break the loop
                        waiting=0
                    #Set the vertices of the filling bar
                    vert[1]=(vert[1][0], vert[1][1]+height)#left corner
                    vert[2]=(vert[2][0], vert[2][1]+height)#right corner
                    # Optional print for debuggins (prints the coordinates of the top two vertices)
                    #print('y vertices top left:', vert[1][1])
                    #print('y vertices top right:', vert[2][1])
                    fillBar.vertices = vert
                    if taskInfo_brief['Spaceship']:
                        Spaceship.pos=(0, vert[2][1])
                    lastvert=vert[2]
                    # Reset vertices to original position
                    vert[1]=(vert[1][0], vert[1][1]-height)# left corner
                    vert[2]=(vert[2][0], vert[2][1]-height)# right corner
                    win.flip()

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
            kd_start_synced='NaN'
            # Optional prints for debugging
            #print('trial length:',trial_length)
            lifted=0#<-------------------------------------------Are the variables lifted
            RT='NaN'
            #if this was a go trial feedback that the participant incorrectly stopped
            if Signal==0:
                feedback=incorrectstop
                # Change the colour of the target arrows
                targetArrowRight.fillColor='Red'
                targetArrowLeft.fillColor='Red'
                correct=-2
            # If this was a stop trial feedback that the participant correctly stopped
            elif Signal==1:# The participant must have continued holding untill the end of the total trial length
                correct=2
                #change the colour of the target Arrows
                targetArrowRight.fillColor='Green'
                targetArrowLeft.fillColor='Green'
                feedback=correctstop
                correct_StopSs=correct_StopSs+1
        # If the key was lifted before the bar filled
        else:
            # If this was a stop trial feedback that the participant incorrectly stopped
            lifted=1
            RT = lift_time
            if Signal==0:# Give feedback they correctly lifted and time in ms from target
                correct=1
                feedback_synced = round(abs(((trial_length*.8)-lift_time)*1000)) #this used the kb.clock.getTime we used previously and saw was binned
                targetArrowRight.fillColor='Green'
                targetArrowLeft.fillColor='Green'
                correctgo = visual.TextStim(win, pos=[-8, 0], height=1, color=[1,1,1],
                text="You stopped the bar \n %.0f ms from the target!"%(feedback_synced), units='cm') # <--------------------------- the ".8" is hard coded here - do we want it flexible this is the proportion of the trial time where the target is
                feedback_list.append(feedback_synced)
                if trial_label=="main":# Only add to the feedback if this is a main trial (i.e. dont count the practice trials)
                    correct_gos=correct_gos+1
                feedback=correctgo
            elif Signal==1:# Give feedback they incorrectly lifted -- and this is an unsuccessfull trial, so the trial should restart (it will be noted in the output that the trial restarted)
                feedback=incorrectgo
                targetArrowRight.fillColor='Red'
                targetArrowLeft.fillColor='Red'
                correct=-1
        if taskInfo_brief['Trial by trial feedback']:
            feedback.setAutoDraw(True)
        win.flip()
        if Signal == 0:
            this_stoptime = 'NaN'
        with open(Output+'.txt', 'a') as b:
            b.write('%s	%s	%s	%s	%s	%s	%s\n'%(block_count, trial_label, trial_count, Signal, lifted, this_stoptime, kd_start_synced))
        trials.addData('block', block_count)
        trials.addData('trialType', trial_label)
        trials.addData('trial', trial_count)
        trials.addData('signal', Signal)
        trials.addData('response', lifted)
        trials.addData('ssd', this_stoptime)
        trials.addData('rt', kd_start_synced)
        thisExp.nextEntry()
        core.wait(ISI)
        # Reset visual stimuli for next trial
        feedback.setAutoDraw(False)
        targetArrowRight.setAutoDraw(False)
        targetArrowLeft.setAutoDraw(False)
        fillBar.setAutoDraw(False)
        Bar.setAutoDraw(False)
        if taskInfo_brief['Spaceship']:
            Spaceship.setAutoDraw(False)
        count=count+1# Only add to the trial could if we have been successfull

    # Write a nice thank-you message and some feedback on performance
    EndMessage = visual.TextStim(win, pos=[0, 0.4], height=.1, color=[1,1,1],
        text="The End!\nThanks for taking part!\n[press a key to end]")
        #text="The End!\n\nAverage time from target: %.3f\n\nCorrect Go: %s out of %s\n\nCorrect Stop: %s out of %s"%(
#        np.average(feedback_list), correct_gos, taskInfo_brief['n_go_trials (per block)']*taskInfo_brief['n blocks'], correct_StopSs, taskInfo_brief['n_stop_trials (per block)']*taskInfo_brief['n blocks']))
# --------------------------------------------------------------
# --------------------------------------------------------------
#                   END TRIALS
# --------------------------------------------------------------
# --------------------------------------------------------------

#play fun video
mov = visual.MovieStim3(win, 'Stimuli/Astronaught_floss_test.mp4', size=(320, 240),
    flipVert=False, flipHoriz=False, loop=False)

while mov.status != visual.FINISHED:
    mov.draw()
    EndMessage.draw()
    win.flip()
    if event.getKeys():
        break
# Be nice and thank participant.
EndMessage.draw()
win.flip()

# Wait for button press
event.waitKeys()
core.quit()
