#!/usr/bin/python3
import sys;
import os;



def compareRuleFiles (sourceFile,modifiedFile):
    with open(sourceFile) as sf:
        source_data=sf.readlines()
        
    source_data=[item.strip() for item in source_data]
    sorted(source_data)
    with open(modifiedFile) as sf:
        modified_data=sf.readlines()
        
    modified_data=[item.strip() for item in modified_data]
    sorted(modified_data)

    for so_spam_lot in source_data :
        for mo_spam_lot in modified_data :
            if(so_spam_lot.split(",")[0]==mo_spam_lot.split(",")[0]):
                if(so_spam_lot.split(",")[1]!=mo_spam_lot.split(",")[1]):
                    print("score " + mo_spam_lot.split(',')[0]+" "+mo_spam_lot.split(",")[1])


compareRuleFiles(sys.argv[1],sys.argv[2])
