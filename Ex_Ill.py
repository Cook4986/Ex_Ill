#EX-ILL
#Image pre-processing + Word Segmentation + TF-based transcription
#From: Gabe Pizzorno, https://github.com/githubharald/SimpleHTR, and https://stackoverflow.com/questions/53962171/perform-line-segmentation-cropping-serially-with-opencv
#Add: SampleProcessor.py, deslant, WordBeam Search
import cv2
import numpy as np
import os
import sys
import subprocess
import re

#declarations
path='xxxx'
textOut='xxxx'
listFiles=os.listdir(path)
imgNo = 1
wordNo = 0

#file/os operations
for file in sorted(listFiles):
    if not file.startswith('.'):
        imgNo=str(imgNo)
        image = cv2.imread(path+'/'+file)
        fileName=file.split('.')[0]
        opPath=("xxxx")
        if not os.path.exists(opPath):
            os.makedirs(opPath)
        
#word segmentation, by card
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,13), np.uint8)
        img_dilation = cv2.dilate(thresh, kernel, iterations=1)
        pxmin = np.min(img_dilation)
        pxmax = np.max(img_dilation)
        ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        for i, ctr in enumerate(sorted_ctrs):
            x, y, w, h = cv2.boundingRect(ctr)
            roi = image[y:y+h, x:x+w]

# pre-process individual word for transcription
            img_grey = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
            kernel = np.ones((5,5),np.uint8)
            img_bw = cv2.threshold(img_grey, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            # increase line width
            kernel = np.ones((1, 1), np.uint8)
            imgMorph = cv2.erode(img_bw, kernel, iterations = 1)
           # img_inv = cv2.bitwise_not(img_bw)
            
#write words to disk            
            cv2.imwrite("xxxx", imgMorph) 
            cv2.imwrite(opPath+fileName+"_"+str(wordNo)+'.png', imgMorph)   
            cv2.rectangle(image,(x,y),( x + w, y + h ),(90,0,255),2)
            cv2.imshow(fileName + 'marked areas', image)
            wordNo = wordNo+1
            
#locate source code and execute "Simple-HTR" per word
            print("Transcription initiated on "+fileName+"_"+"word # " + str(wordNo))
            os.chdir("xxxx")
            result = subprocess.run(['python', 'main.py'], stdout=subprocess.PIPE)
            
#print system output to txt file
            temp = sys.stdout
            sys.stdout = open(textOut + fileName +'.txt', 'a')
            print(result.stdout)
            sys.stdout.close()
            sys.stdout = temp
            cv2.waitKey(5000)
            
#open txt file output for operation 
        with open(textOut + fileName +'.txt', 'r') as f2:
            data = f2.read()
            data = str(data)

#cleanup raw text output
        print("Processing complete on " + fileName) 
        tranS = re.findall(r'\"(.+?)\"', data)
        print("The following "+ str(wordNo)+ " words and characters were transcribed from page "+fileName+":")
        print(tranS)
        print("/n")
        cv2.imwrite(opPath+fileName+"_"+str(imgNo)+'.png', image)
        imgNo = int(imgNo) + 1
        wordNo = 0
        cv2.imshow(fileName + 'marked areas', image)
        cv2.waitKey(500)
    cv2.destroyAllWindows()
