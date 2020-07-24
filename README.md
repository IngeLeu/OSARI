# Open-Source Aniticipated Response Inhibition task (OSARI)

Written by Rebecca J Hirst[1] and Rohan Puri[2]
Edited by Jason L He[3]

[1] Trinity College Institute of Neuroscience, Trinity College Dublin
[2] University of Tasmania
[3]Russell H Morgan, Department of Radiology, School of Medicine, Johns Hopkins University 

Created in PsychoPy v3.1.2

Software created to supplement the following article:

He, J. L , Hirst, R. J , Pedapati, E., Byblow, W., Chowdhury, N., Coxon, J., Gilbert, Donald., Heathcote, A., Hinder, M., Hyde, C., Silk. T., Leunissen, I., McDonald, H., Nikitenko, T., Puri, R., Zandbelt, B., Puts, N. (In prep) Open-Source Anticipated Response Inhibition task (OSARI): a cross-platform installation and analysis guide. 

Relevant references:
    
Guthrie, M. D., Gilbert, D. L., Huddleston, D. A., Pedapati, E. V., Horn, P. S., Mostofsky, S. H., & Wu, S. W. (2018). 
Online Transcranial Magnetic Stimulation Protocol for Measuring Cortical Physiology Associated with Response Inhibition.
Journal of Visualized Experiments, (132), 1-7. http://doi.org/10.3791/56789

He, J. L., Fuelscher, I., Coxon, J., Barhoun, P., Parmar, D., Enticott, P. G., & Hyde, C. (2018). 
Impaired motor inhibition in developmental coordination disorder. Brain and Cognition, 127(August),
23-33. http://doi.org/10.1016/j.bandc.2018.09.002


Please report any issues on the github page 
    
Input (optional):
    
    3 csv files:
        practiceGoConditions.csv
        practiceMixedConditions.csv
        TestConditions.csv
    
    In all csv files each row corresponds to a trial, so number of rows will correspond to the number of trials in a block.
    0 = Go 1 = Stop 
        
Output:
    
    4 output files in format:
        s_123_OSARI_2020_Jul_19_1307.log
        s_123_OSARI_2020_Jul_19_1307.csv
        s_123_OSARI_2020_Jul_19_1307.psydat
        s_123_OSARI_2020_Jul_19_1307.txt
    
    naming format: "s_[participant ID]_OSARI_[year]_[month]_[date]_[timestamp].csv
    
    Data is contained in the .txt and .csv files. The .txt file saves the main details of interest but csv stores further details.
    
    Block: block number

    TrialType: Practice or real trial

    Trial: Trial number_text

    Signal: 0 = Go
            1 = Stop

    Response: What the participants response was ( 0 = no lift, 1 = lift)

    RT: Lift time of participants relative to the starting line (to 2 decimal places)

    SSD: Stop Signal Distance (relative to starting line) if the trial was a stop trial.
    
    For details on psydat and log files see 
        https://www.psychopy.org/general/dataOutputs.html#:~:text=PsychoPy%20data%20file%20(.-,psydat),python%20and%2C%20probably%2C%20matplotlib.


Thanks for using OSARI!! 
