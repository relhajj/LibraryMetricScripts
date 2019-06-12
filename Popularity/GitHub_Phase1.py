'''
This script queries for 1000 repositories pushed in the last year. 
This 1000 is a configurable parameter which can be changed from the GitHubSearch.ini file by changing the variable max_size. 
These repo's are sorted from most to least stars. 

Requires:   A configuration file called GitHubSearch.ini
            Ensure a GitHub token generated by your account is in the configuration account so that the script may connect to github 
            
Output:     A text file called Top_repo.txt which has all the 1000 repository full names (which will be used in GitHub_Phase2.py)
'''

import time
import datetime
import random
import sys
from github import Github
from datetime import date

#This is a sleep function so pause the script since GitHub does not allow frequent calls.
def go_to_sleep (msg, time_of_sleep):
  
  time_stamp = time.time()
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S')   
  error_msg = "....    " + msg + str(time_of_sleep) + " seconds, Sleeping @ " + start_date
  print (error_msg) 
  
  time.sleep(time_of_sleep)  # actual Sleep
  
  time_stamp = time.time()  
  start_date = datetime.datetime.fromtimestamp(time_stamp).strftime('%Y-%m-%d %H:%M:%S') 
  error_msg = "....    " + "Waked up @ " + start_date
  print (error_msg) 

#Outputs all the repositories found into a text file
def output_to_file(repos_file, repo):
    file_name = open(repos_file, "a")
    file_name.write(str(repo))
    file_name.write("\n")
    file_name.close()
             
#This is where we query for the top repositories 
def query_repo(output_file_name, interval, base_query, github, quick_sleep, error_sleep, max_size):
   
  #check github for rate limit 
  try:
    
    #check github for rate limit 
    rate_limit = github.get_rate_limit()
    rate = rate_limit.search
    print("The rate limit is "+ str(rate.limit))
    if rate.remaining == 0:
      print(f'You have 0/{rate.limit} API calls remianing. Reset time: {rate.reset}')
      return 
    else:
      print(f'You have {rate.remaining}/{rate.limit} API calls remaining')
      
    # max_size
    print (base_query)
    final_query = base_query
    
    cnt_General = 1
    while cnt_General < max_size:
      print (final_query)
      result = github.search_repositories(final_query, sort='stars', order='desc')
      cnt = 1
      pgno = 1      
      while cnt <= 300:            
        for repo in result.get_page(pgno):
          output_to_file(output_file_name, repo.full_name)
          #res = str(pgno)+ "--" + str(cnt)+ ":" + repo.full_name + "("+str(repo.stargazers_count)+")"
          cnt = cnt + 1
          cnt_General = cnt_General + 1
          
          #res is the results THIS IS ONLY HERE FOR NOW so that I can see the script results during the run  
          res = str(cnt_General)+ ":" + str(cnt) + "in page " + str(pgno) + " Stars " + str(repo.stargazers_count) 
          print(res)
          
          stars = repo.stargazers_count
        pgno = pgno + 1  
      final_query =  base_query + " stars:<" + str(stars)
   
      go_to_sleep("Force to sleep after each iteration, Go to sleep for ", quick_sleep)

    # error detection, just in case
  except:
    go_to_sleep("Error: abuse detection mechanism detected,Go to sleep for ", error_sleep)
  
#Reads the ini file data into dict.
#NOTE TO SELF: REMOVE THIS FUNCTION AND ADD A LIBRARY THAT CAN DO THIS FOR ME ----------
def read_ini_file():
    dictKeys = {}
    with open("GitHubSearch.ini", "r") as f:
        for line in f:
            line = line.rstrip()
            loc = line.index("]")
            keyword = line[1:loc]
            line = line[loc+2:]
            loc = line.index("]")
            valuekey = line[:loc]
            dictKeys[keyword] = valuekey
    return dictKeys

#Main function where we set the variables from the configuration file and connect to github 
def main():
    
    dictContst = read_ini_file() # read all ini data    
    start_Date =  date.today() - datetime.timedelta(days=365) 
    
    quick_sleep = int (dictContst["SLEEP1"]) # regular sleep after each iteration
    error_sleep = int (dictContst["SLEEP2"]) # Sleep after a serious issue is detected from gitHib, should be around 10min, ie 600 sec
    interval = int(dictContst["INTERVAL"]) # the time span between each iteration
    max_size = int (dictContst["MAXSIZE"]) # max pages returned per gitHub call, for now it is 1000, but could be changed in the future
    
    github = None
    github = Github(dictContst["TOKEN"])   # pass the connection token 
    
    output_file_name = "Top_Repo.txt"  # this is the output file that we are going to send repo names to
    
    output_file = open(output_file_name, "w")  
    output_file.close()      
    
    query = "pushed:>" + str(start_Date) + " " + dictContst["SEARCHTERM"]          
    print (query)
   
    query_repo(output_file_name, interval, query, github, quick_sleep, error_sleep, max_size) 
             
    print ("\nFinally ..... Execution is over \n")
      
main()
