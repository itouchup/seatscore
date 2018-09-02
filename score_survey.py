# -*- coding: utf-8 -*-
"""
iCode Script
2018/08/26
Score Survey
**This is a general scoring algorthm that takes in weighted answer table
and responses, compares, and computes a score.  Weights 0 to 1.  Score average.
"""

##Import test survey and answer sheet.
##1a.  Detect all response & answer sheets and parse names into readible format.
##1b.  Allow user selection of response & answer sheet

#####
##Version 0.1 function in folder (no path navigation, bounds checks)
##
#####

import os
import csv
import pandas as pd

#I wanted to allow users to select from list of files assuming multiple classes responses stored in same directory.


def select_survey():
    file_list = [] #initialize file store
    i=0
    for root, dirs, files in os.walk("."): #call arg files in current folder
        for filename in files: #operate on filenames to get correct type
            if ("csv" in filename) or ("txt" in filename): #only using txt or csv right now
                file_list.append([i, filename])
                i = i+1
   
    for record in file_list: #Print formatted text for user selection. GUI in future
        print(record[0], "  ", record[1])           
    
    #Get user selected raw data and answers paths
    res = int(input('Enter response file #: ')) 
    res_path = os.path.abspath(str(file_list[res][1])) #report absolute path.  Might be easier to work with later.
    ans = int(input('Enter answersheet file #: '))
    ans_path = os.path.abspath(str(file_list[ans][1]))
    files_chosen = {'responses':res_path, 'answers':ans_path}

    return files_chosen

#Now to take chosen files and load them into pandas dataframes.
def read_data(files):
    ans_delim = delim_check(files['answers'])
    res_delim = delim_check(files['responses'])
    
    response_data = pd.read_csv(files['responses'], delimiter=res_delim)
    answer_data = pd.read_csv(files['answers'], delimiter=ans_delim)
    
    #first let's clear null data (no submission date: query max, re-do's)
    response_clean = response_data[response_data.submitdate.notnull()] #requires 'submitdate' column label    
    
    
    #Keeping IP and other information here as it may be used for quality checks later on
    return response_clean, answer_data

#This will check for the correct deliminator.  Exports from limesurvey have ;, while .csv exports have ,
def delim_check(filepath):
    with open(filepath, 'rb') as file:
        if (str(file.readline()).count(';')) > (str(file.readline()).count(',')):
            delim = ';'
        else:
            delim = ','
    return delim

#Check answers and score
def score_data(raw_res, raw_ans):
    #create results-only list for scoring 
    responses = raw_res[raw_ans.q_code.tolist()]
    responses['student_id'] = raw_res['q00'] #consider passing as tuple from this point as responses.loc[index#] will return a scoreset
    
    #initialize dataframe to store final results
    scored_res = pd.DataFrame(columns=['student_id','score'])
    
    ##Loop through each test and get a score
    for i in range(responses.index.size):
        #Compare responses against answers
        exam = responses.loc[i]  #creates a series
        student_id = exam['student_id']
        exam = exam.to_frame().reset_index()
        exam.columns = ['q_code', 'response']
        comp_res = raw_ans
        comp_res[student_id] = exam['response']    
        #it would be great to pass indices and get to this step faster
        comp_res['score'] = (comp_res['a_code']==comp_res[student_id])*comp_res['wgt']
        #sum new column for score!
        final_score = comp_res['score'].sum()
        #Append scored_res dataframe
        scored_res = scored_res.append({'student_id':student_id, 'score':final_score}, ignore_index=True)

    return scored_res
    
def print_data(scores, files):
    filename = input('Enter Output Filename: ')
    with open(str(filename + '.txt'), 'w+') as file:
        for i in range(scores.index.size):
            strwrite = ','.join([str(scores.loc[i].tolist()[0]), str(scores.loc[i].tolist()[1]), files['responses'], files['answers']])
            print(strwrite)
            file.write(strwrite+'\n')


#MAIN
files = select_survey()
raw_res, raw_ans = read_data(files)
scores = score_data(raw_res, raw_ans)

#Create clean results file
print_data(scores,files)



##PANDAS TRANSFORMATIONS MAY BE USEFUL
#Long to Wide Answer Format
# raw_ans.pivot(index='test', columns='q_code')









