#EX-ILL
#Image pre-processing + Word Segmentation + TF-based transcription
#From: Gabe Pizzorno, https://github.com/githubharald/SimpleHTR, and https://stackoverflow.com/questions/53962171/perform-line-segmentation-cropping-serially-with-opencv
import cv2
import numpy as np
import os
import sys
import subprocess
import re

#declarations
path='xxx'
textOut='xxx'
listFiles=os.listdir(path)
imgNo = 1
wordNo = 0

#file/os operations
for file in sorted(listFiles):
    if not file.startswith('.'):
        imgNo=str(imgNo)
        image = cv2.imread(path+'/'+file)
        fileName=file.split('.')[0]
        opPath=("xxx"+fileName+"/")
        if not os.path.exists(opPath):
            os.makedirs(opPath)
        
#gray, binary, dilation, contouring individual cards
        gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        ret,thresh = cv2.threshold(gray,127,255,cv2.THRESH_BINARY_INV)
        kernel = np.ones((5,20), np.uint8)
        img_dilation = cv2.dilate(thresh, kernel, iterations=1)
        pxmin = np.min(img_dilation)
        pxmax = np.max(img_dilation)
        ctrs, hier = cv2.findContours(img_dilation.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#sort contours + get bounding boxes for individual words
        sorted_ctrs = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        for i, ctr in enumerate(sorted_ctrs):
            x, y, w, h = cv2.boundingRect(ctr)
            roi = image[y:y+h, x:x+w]

# increase contrast per word
            pxmin = np.min(roi)
            pxmax = np.max(roi)
            imgContrast = (roi - pxmin) / (pxmax - pxmin) * 255
            kernel = np.ones((3, 3), np.uint8)
            imgMorph = cv2.erode(imgContrast, kernel, iterations = 3)
            
#write words to disk            
            cv2.imwrite("xxx/temp/word.png", imgMorph) 
            cv2.imwrite(opPath+fileName+"_"+str(wordNo)+'.png', imgMorph)   
            cv2.rectangle(image,(x,y),( x + w, y + h ),(90,0,255),2)
            cv2.imshow(fileName + 'marked areas', image)
            wordNo = wordNo+1
            
#locate source code and execute "Simple-HTR"
            print("Transcription initiated on "+fileName+"_"+"word # " + str(wordNo))
            os.chdir(".../SimpleHTR-master/src")
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
        print("The following words and characters were transcribed from page "+fileName+":")
        print(tranS)
#        cv2.imwrite(opPath+fileName+"_"+str(imgNo)+'.png', image)
        imgNo = int(imgNo) + 1
        cv2.imshow(fileName + 'marked areas', image)
        cv2.waitKey(500)
    cv2.destroyAllWindows()
