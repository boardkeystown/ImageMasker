#Flask stuff 
from flask import Flask, render_template, url_for, request,jsonify, json, after_this_request, send_file
import base64

#use matplotlib to graph image 
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

#Use pillow to open the image 
from PIL import Image

#use cv2 to convert .tif into array 
import cv2

#user for getting files paths 
import glob

#for files stuff
import os
import io

#for add time stamp to the file 
# using datetime module
import datetime

#used to find minima 
from scipy import optimize
import scipy.ndimage.filters as filters
import scipy.ndimage.morphology as morphology


#App constants 
GRADETHRESH = 60   
MISSINGTHRESH = -4500
LOWSCOREFILTER = 0.1

#Folder Path Constants  
MAINDIR = "data"
SUBDIR = "sub"
IMAGEDIR = "img"
CONIMAGEDIR = "consensusMask"
USERJSONDIR = "userJson"
CONJSONDIR = "consensusMaskJson"

#These are all the cases for the different paths that are need 
#to be kept track of from the data folder and their corresponding 
#folder paths @see def setAndGetDataFolderPath()
GET_TRUTH_MASK_PATH = 0
GET_TRUTH_MASK_RED_PATH = 1
GET_SOURCE_PATH = 2
GET_USERJSON_PATH = 3
GET_CURRENT_USER_MASK_DIR_PATH = 4
GET_CURRENT_CONSENSUS_MASK_DIR_PATH = 5
GET_CONSENSUS_JSON_DIR_PATH = 6
GET_CURRENT_CONSENSUS_PATH = 7
GET_CURRENT_IMG_DIR_PATH = 8
GET_SOURCE_MASKED_PATH = 9
GET_USER_JSON_DIR_PATH = 10

#globals 
currentUser = 1        #The current user. see java script. 
totalNumberOfUsers = 5 #The total number of users.
currentSubPath = 4     #This can be changed run time. It the the sub path that all data is sotred in.
currentUserPath = "img\\userMask.png"      # These are just global paths passed between functions 
consensusMaskPath = "img\\consensusMask"   #
consensusMaskJsonPath = "consensusMaskJson"#


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
    #return "hello world"

#This saves the truth mask as a .png 
@app.route('/truthMask', methods=['POST'])
def set_truthMask():
    print("Got the data")
    imageString = json.loads(request.data.decode())["input"]
    imageString = imageString.split(',')[1]
    nparr = np.fromstring(base64.b64decode(imageString), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #cv2.imwrite("img\\truthMask.png", img)
    cv2.imwrite(setAndGetDataFolderPath(GET_TRUTH_MASK_PATH), img)
    #then make a red copy of it for later 
    #get the input image 
    #input_img_source = Image.open("img\\truthMask.png")
    input_img_source = Image.open(setAndGetDataFolderPath(GET_TRUTH_MASK_PATH))
    width, height = input_img_source.size
    #convert into array 
    #input_img_array = cv2.imread("img\\truthMask.png")
    input_img_array = cv2.imread(setAndGetDataFolderPath(GET_TRUTH_MASK_PATH))
    red_mask = getImageToMask(input_img_array)
    red_input_img_array = applyRedMask(red_mask,input_img_array,width,height)
    #cv2.imwrite("img\\truthMask_red.png", red_input_img_array)
    cv2.imwrite(setAndGetDataFolderPath(GET_TRUTH_MASK_RED_PATH), red_input_img_array)

    return "truth mask sent"

#retrun the source image that was opened in the browser 
@app.route('/getSourceImg', methods=['POST'])
def set_getSourceImg():
    print("Got the data")
    imageString = json.loads(request.data.decode())["input"]
    imageString = imageString.split(',')[1]
    nparr = np.fromstring(base64.b64decode(imageString), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #cv2.imwrite("img\\sourceImg.png", img)
    cv2.imwrite(setAndGetDataFolderPath(GET_SOURCE_PATH), img)

    return "Image sent"

#this hard resets the values in the users json 
@app.route('/hardUserReset', methods=['POST'])
def set_userJsonHardReset():
    #hard_reset_users(USERJSONDIR)
    hard_reset_users(setAndGetDataFolderPath(GET_USER_JSON_DIR_PATH))
    return "values rest"


#this hard resets the values in the users json 
@app.route('/hardResetConsensusMask', methods=['POST'])
def set_userJsonResetConsensusMask():
    #hard_reset_user_consensus(CONJSONDIR)
    hard_reset_user_consensus(setAndGetDataFolderPath(GET_CONSENSUS_JSON_DIR_PATH))
    return "values rest"


#This retruns to the browser truth mask previously converted to a red mask
#so the user can see what the ground truth is 
@app.route('/getImageRedMask', methods=['GET'])
def get_RedTruthMask():
    #Send the current consensusMask
    image = get_encoded_img(setAndGetDataFolderPath(GET_TRUTH_MASK_RED_PATH))
    #image = get_encoded_img("img\\truthMask_red.png")
    #image = "img\\truthMask.png"
    return jsonify({'image_url': image})

#this gets the current users 
@app.route('/getCurrentUser', methods=['POST'])
def set_getCurrentUser():
    global currentUser
    print("Got the data")
    data = json.loads(request.data.decode())["id"]
    currentUser = data
    print("user switched to {}".format(currentUser))

    #also return the elo score of the current user 
     #grab the current user scores
    #data, outPath = loadJsonDataObj("userJson\\*.json")
    data, outPath = loadJsonDataObj(setAndGetDataFolderPath(GET_USERJSON_PATH))

    #get the current scores for the current users
    elo, correctMatches, incorrectMatches = getUserScoreFromJson(data, currentUser)

    jsonResp = {'elo' :elo}
    return jsonify(jsonResp)

#this gets the current user created mask from the browser 
#and saves it to a directory which corrcosponds the the current user 
@app.route('/userMask', methods=['POST'])
def set_userMask():
    global currentUser, currentUserPath
    print("Got the data")
    imageString = json.loads(request.data.decode())["input"]
    imageString = imageString.split(',')[1]
    nparr = np.fromstring(base64.b64decode(imageString), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    #make the folder we need for the user to store the image 
    #PATH = "img"+os.path.sep+"user"+str(currentUser)
    #checkIfPathExistToMake(PATH)
    PATH = setAndGetDataFolderPath(GET_CURRENT_USER_MASK_DIR_PATH)
    #make a time stamp for the image 
    timeNow = datetime.datetime.now()
    timeString = timeNow.strftime("_%m-%d-%Y_%H-%M-%S-%f")
    IMGPATH = PATH+os.path.sep+"user"+str(currentUser)+timeString+".png"
    currentUserPath = IMGPATH #set the current user path
    #save the image 
    #cv2.imwrite("img\\userMask.png", img)
    cv2.imwrite(IMGPATH, img) 
    return "sent"


#This calculates the current user score, based on their current masked image
#then saves the data in the json, then sends it back to the browser 
@app.route('/getUserScore', methods=['GET'])
def get_userScore():
    global currentUserPath, currentUser
    # @after_this_request #what the heck does this even do?
    # def add_header(response):
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response

    #get the truth mask 
    #truthMask_source = Image.open("img\\truthMask.png")
    truthMask_source = Image.open(setAndGetDataFolderPath(GET_TRUTH_MASK_PATH))

    width, height = truthMask_source.size
   #truthMask_array = cv2.imread("img\\truthMask.png")
    truthMask_array = cv2.imread(setAndGetDataFolderPath(GET_TRUTH_MASK_PATH))

    truth_mask = getImageToMask(truthMask_array)

    # #get the user mask 
    #user1_img = cv2.imread("img\\userMask.png")
    user1_img = cv2.imread(currentUserPath)
    print("USER PATH:= {}".format(currentUserPath))
    user1_mask = getImageToMask(user1_img)

    # #calculate score
    grade, score = getUserMaskAccuracy(user1_mask, truth_mask, width, height)

    #grab the current user scores
    #data, outPath = loadJsonDataObj("userJson\\*.json")
    data, outPath = loadJsonDataObj(setAndGetDataFolderPath(GET_USERJSON_PATH))


    #get the current scores for the current users
    elo, correctMatches, incorrectMatches = getUserScoreFromJson(data, currentUser)
    
    #get accumulative score 
    elo, numCorrect, numIncorrect = getAccumulativeScore(grade, GRADETHRESH, score, MISSINGTHRESH, correctMatches,incorrectMatches)
    print("numCorrect {}".format(numCorrect))
    print("numIncorrect {}".format(numIncorrect))


    #tell whether the mask was correct or not
    result = False
    if (numCorrect > correctMatches):
        result = True

    #save them back to the json file 
    data = setUserScoreFromJson(data, currentUser, elo,numCorrect,numIncorrect)
    saveJsonDataObjToFile(data,outPath)

    jsonResp = {'elo' : elo, 'grade' : grade, 'score' : score, "isCorrect" : result, "thresh": MISSINGTHRESH }
    #jsonResp = {'elo' : 5, 'grade' : 5, 'score' : 5}
    print("--------------------------------------------------")
    print("Current User[{}]".format(currentUser))
    print(jsonResp)
    print("--------------------------------------------------")

    return jsonify(jsonResp)



#this gets the current user consensus mask from the browser 
# and saves it to the consensus mask folder  
# then it records that path image path and the user elo score with it  
@app.route('/consensusMask', methods=['POST'])
def set_userconsensusMask():
    global currentUser, currentUserPath, consensusMaskPath, consensusMaskJsonPath

    #-------------------------------------------------------
    #save the image 
    print("Got the data")
    imageString = json.loads(request.data.decode())["input"]
    imageString = imageString.split(',')[1]
    nparr = np.fromstring(base64.b64decode(imageString), np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    #make the folder we need for the user to store the image 
    # PATH = "img"+os.path.sep+"consensusMask"
    # checkIfPathExistToMake(PATH)
    PATH = setAndGetDataFolderPath(GET_CURRENT_CONSENSUS_MASK_DIR_PATH)

    #make a time stamp for the image 
    timeNow = datetime.datetime.now()
    timeString = timeNow.strftime("_%m-%d-%Y_%H-%M-%S-%f")
    IMGPATH = PATH+os.path.sep+"user"+str(currentUser)+timeString+".png"
    consensusMaskPath = IMGPATH #set the current user path
    #save the image 
    cv2.imwrite(IMGPATH, img) 
    #-------------------------------------------------------
    #record the elo and image path 
       #grab the current user scores
    #data, outPath = loadJsonDataObj("userJson\\*.json")
    data, outPath = loadJsonDataObj(setAndGetDataFolderPath(GET_USERJSON_PATH))
    #get the current scores for the current users
    elo, correctMatches, incorrectMatches = getUserScoreFromJson(data, currentUser)

    #prevent large negative user score from being entered
    if (elo < 0):
        elo = LOWSCOREFILTER   
    #save to the json for later use 
    #setConsensusMaskJson(consensusMaskJsonPath, elo, IMGPATH,currentUser)
    setConsensusMaskJson(setAndGetDataFolderPath(GET_CONSENSUS_JSON_DIR_PATH), elo, IMGPATH,currentUser)
    return "sent"


#This retruns to the browser the current consensus mask 
#based on user consensus maskings 
@app.route('/getImage', methods=['GET'])
def get_Image():
    global consensusMaskJsonPath
    #Based on the images in the consensus mask folder calculate the current mask

    #save the current consensusMask 
    #computeConsensusMaskAndSave(consensusMaskJsonPath,"img")
    computeConsensusMaskAndSave(setAndGetDataFolderPath(GET_CONSENSUS_JSON_DIR_PATH),setAndGetDataFolderPath(GET_CURRENT_IMG_DIR_PATH))
    #Send the current consensusMask
    #image = get_encoded_img("img\\currentConsensus.png")
    image = get_encoded_img(setAndGetDataFolderPath(GET_CURRENT_CONSENSUS_PATH))


    return jsonify({'image_url': image})



#this loads the current users from the json to the browser 
@app.route('/initUsers', methods=['GET'])
def initUsers():
    #open the json file with the user info 
    #files = basicFileReader("userJson\\users.json")
    files = basicFileReader(setAndGetDataFolderPath(GET_USERJSON_PATH))
    with open(files[0]) as f:
        data = json.load(f)
    f.close()

    #copy out the id numbers and save to a json array 
    listTest = []
    for i in range(0,len(data['users'])):
        listTest.append(data['users'][i]['id'])

    #convert to json send to the browser
    return jsonify(listTest)


#This retruns to the browser the final applied mask!  
@app.route('/getFinalImage', methods=['GET'])
def get_FinalImage():    
    #open the current consensus mask 
    #input_img_source = Image.open("img\\currentConsensus.png")
    input_img_source = Image.open(setAndGetDataFolderPath(GET_CURRENT_CONSENSUS_PATH))
    width, height = input_img_source.size
    #conMaskImg = cv2.imread("img\\currentConsensus.png")
    conMaskImg = cv2.imread(setAndGetDataFolderPath(GET_CURRENT_CONSENSUS_PATH))

    #Convert to a mask 
    conMask = getImageToMask(conMaskImg)
    print(conMask[300][250])

    #open the source image 
    #sourceImage = cv2.imread("img\\sourceImg.png")
    sourceImage = cv2.imread(setAndGetDataFolderPath(GET_SOURCE_PATH))

    #apply the mask
    sourceImage = applyMask(conMask,sourceImage,width,height)

    #save the image TODO: should be a to just send it without saving...
    #cv2.imwrite("img\\sourceImgMasked.png", sourceImage)
    cv2.imwrite(setAndGetDataFolderPath(GET_SOURCE_MASKED_PATH), sourceImage)

    #Send the final mask to the user! 
    #image = get_encoded_img("img\\sourceImgMasked.png")
    image = get_encoded_img(setAndGetDataFolderPath(GET_SOURCE_MASKED_PATH))
    return jsonify({'image_url': image})



#*******************************************************My functions*********************************************************************

def setAndGetDataFolderPath(case):
    """This sets, creates, and and returns folder paths and file paths 
    for the app.
    """
    global currentSubPath, totalNumberOfUsers, currentUser
    
    pathResult = ""

    #TODO: should not have to check this part every time but rather should check it only on start and if a sub path is changed...

    #check if the data folder exists if it does not make it
    #data
    checkIfPathExistToMake(MAINDIR)
    #check if the sub folder we are in exist if not make it 
    #data\subX
    checkIfPathExistToMake(MAINDIR+os.path.sep+SUBDIR+str(currentSubPath))
    #check if the img folder we are in exist if not make it 
    #data\subX\img
    checkIfPathExistToMake(MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR)
    #check if the userJson Folder we are in exist if not we need to make it 
    #data\subX\userJson
    checkIfPathExistToMake(MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+USERJSONDIR)
    #check if the json file exist if not we need to make it
    #data\subX\userJson\users.json 
    ifNoUserJsonFillWithDefault(MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+USERJSONDIR+os.path.sep+"users.json",totalNumberOfUsers)
    #check if the consensus mask folder we are in exist if not we need to make it
    #data\subX\img\consensusMask
    checkIfPathExistToMake(MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+CONIMAGEDIR)
   
    #return a truth mask 
    if (case == GET_TRUTH_MASK_PATH):
        #data\subX\img\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"truthMask.png"
    elif (case == GET_TRUTH_MASK_RED_PATH):
        #data\subX\img\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"truthMask_red.png"
    elif (case == GET_SOURCE_PATH):
        #data\subX\img\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"sourceImg.png"
    elif (case == GET_SOURCE_MASKED_PATH):
        #data\subX\img\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"sourceImgMasked.png"
    elif (case == GET_USERJSON_PATH):
        #data\subX\userJson\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+USERJSONDIR+os.path.sep+"users.json"
    elif (case == GET_USER_JSON_DIR_PATH):
        #data\subX\userJson\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+USERJSONDIR
    elif (case == GET_CURRENT_USER_MASK_DIR_PATH):
        #data\subX\img\userX
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"user"+str(currentUser)
        checkIfPathExistToMake(pathResult) #make this folder if it does not exist 
    elif (case == GET_CURRENT_CONSENSUS_MASK_DIR_PATH):
        #data\subX\img\consensusMask
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+CONIMAGEDIR
    elif (case == GET_CONSENSUS_JSON_DIR_PATH):
        #data\subX\consensusMaskJson
        #note the function this is passed to makes the folder and json if it does not exist...
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+CONJSONDIR
    elif (case == GET_CURRENT_CONSENSUS_PATH):
        #data\subX\img\
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR+os.path.sep+"currentConsensus.png"
    elif (case == GET_CURRENT_IMG_DIR_PATH):
        #data\subX\img\  JUST THE PATH 
        pathResult = MAINDIR+os.path.sep+SUBDIR+str(currentSubPath)+os.path.sep+IMAGEDIR
    print(pathResult)
    return pathResult

def ifNoUserJsonFillWithDefault(path,numberOfUsers):
    """If there isn't a user json file here we need to make it and 
    fill it with default values so that it can be used. 
    """
    CHECK_FOLDER = os.path.isfile(path)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        jsonDefaultData = "{\"users\": []}"
        #make the file 
        with open(path, 'w') as f:
            f.write(jsonDefaultData)
        f.close()
        #load the file 
        dataJson, filePath = loadJsonDataObj(path)
        #append default data into it 
        for i in range(0,numberOfUsers):
            dataJson['users'].append({
                "id": (i+1),
               "elo": 0,
              "correctMatches": 0,
               "incorrectMatches": 0
            })
        #save the file with the new data in it 
        with open(filePath, 'w') as outfile:
            json.dump(dataJson, outfile)
        outfile.close()

def hard_reset_users(inputPath):
    """This resets the userJson to all 0 values when called 
    """
    #open the json 
    data, outPath = loadJsonDataObj(inputPath+os.sep+"users.json")
    #rest the values
    for i in range(0,len(data['users'])):
        # print(data['users'][i]['elo'])
        data['users'][i]['elo'] = 0
        # print(data['users'][i]['correctMatches'])
        data['users'][i]['correctMatches'] = 0
        # print(data['users'][i]['incorrectMatches'])
        data['users'][i]['incorrectMatches'] = 0
    #save the current values 
    saveJsonDataObjToFile(data,outPath)

def hard_reset_user_consensus(jsonPath):
    """This hard resets the user consensus masks json data by removing it
    """
    if os.path.exists(jsonPath+os.sep+"data.json"):
        os.remove(jsonPath+os.sep+"data.json")

def get_encoded_img(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        image_file.close()
    print(encoded_string)
    theString = str(encoded_string)
    # with open("out.txt", 'w') as outfile:
    #     theString = str(encoded_string)
    #     outfile.write("data:image/png;base64,"+theString[2:len(theString)-1])
    #     outfile.close()
    return "data:image/png;base64,"+theString[2:len(theString)-1]
    #return "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAoAAAAHgCAIAAAC6s0uzAAAIi0lEQVR4Ae3BAQpFWXUEwO79L/oEBEFJJEoyPfPur6oGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYawCAuQYAmGsAgLkGAJhrAIC5BgCYa4A/3t3l39Y2wOsa4A92d/kPtQ3wtAb4N9xdhtoGeFoD/Gt3lz9J2wDvaoD/5u7yF9A2wKMa4J/dXf4a2gZ4VAP8zd3lr6dtgBc18MPuLn95bQM8p4Hfc3f5jrYBntPAL7m7fFDbAG9p4DfcXT6rbYC3NPAD7i4f1zbAQxp43d3lCW0DvKKBp91dXtE2wCsaeNfd5S1tAzyhgUfdXZ7TNsATGnjU3eVFbQN8XwMvurs8qm2A72vgRXeXd7UN8HENPOfu8rS2AT6ugefcXZ7WNsDHNfCcu8vT2gb4uAaec3d5XdsAX9bAc+4ur2sb4MsaeM7d5XVtA3xZA8+5u/yAtgE+q4Hn3F1+QNsAn9XAc+4uv6FtgG9q4Dl3l622d5e5tgG+qYHn3F1W2ia5u/wZ2gb4pgaec3eZaJu/ubv8GdoG+KYGnnN3WWl7d/mTtA3wTQ085+7yG9oG+KYGnnN3+Q1tA3xTA8+5u/yMtgE+qIHn3F1+RtsAH9TAc+4uP6NtgA9q4Dl3l5/RNsAHNfCiu8tvaBvggxp40d3lN7QN8EENvOju8hvaBvigBl50d/kNbQN8UAMvurv8hrYBPqiBF91dfkPbAB/UwIvuLr+hbYAPauBFd5ff0DbABzXworvLb2gb4IMaeNTd5XVtA3xTA++6u7yrbYDPauBpd5cXtQ3wZQ087e7ynLYBPq6Bp91d3tI2wPc18LS7yyvaBnhFA6+7u3xf2wAPaeAH3F2+rG2AtzTwG+4u39Q2wHMa+Bl3l69pG+BFDfySu8tHtA3wrgZ+zN3lr61tgNc18JPuLn8xbQP8jAZ+1d3lr6FtgB/TwK+6u/yp2gb4VQ38sLvLUNsA/E0DP+zustI2AH/XwG+7u/zx2gbgHzTw8+4uf6S2AfhnDZDcXf4AbQPwP2mAv7m7/P9pG4B/rQH+7u7yf9Y2AP+bBvgHd5f/XNsA/CcaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYK4BAOYaAGCuAQDmGgBgrgEA5hoAYO6/AIjy3+HYnuNoAAAAAElFTkSuQmCC"
  
def getImageToMask(image):
    """Returns a pixel-by-pixel mask true for every white pixel.
    : param image: cv2.imread() 
    """ 
    #for every pixel in the image if it is > 1
    #then set it to true
    mask = image > 1 
    return mask

def applyMask(mask,imageArray, width, height):
    """Return a mask applied and blacked out   
    :param mask: byte array pixel-by-pixel for the image 
    :param image: cv2.imread()
    :param width: the width of the image 
    :param height: the height of the image 
    """
    result = imageArray.copy()
    black = [0,0,0]
    for i in range(0,height):
        for j in range (0,width):
            if(mask[i][j].all() == True):
            #paint pixels black 
                result[i][j] = black
    return result

def applyWhiteMask(mask,imageArray, width, height):
    """Return a mask applied and white out   
    :param mask: byte array pixel-by-pixel for the image 
    :param image: cv2.imread()
    :param width: the width of the image 
    :param height: the height of the image 
    """
    result = imageArray.copy()
    white = [255,255,255]
    for i in range(0,height):
        for j in range (0,width):
            if(mask[i][j].all() == True):
            #paint pixels black 
                result[i][j] = white
    return result

def applyRedMask(mask,imageArray, width, height):
    """apply a red mask to a image. This will turn all white pixels red 
    """
    result = imageArray.copy()
    red = [0,0,255]
    for i in range(0,height):
        for j in range (0,width):
            if(mask[i][j].all() == True):
            #paint pixels red 
                result[i][j] = red
    return result


def boolCounter(mask, width, height):
    """count the number of trues from a mask and return the count
    :param mask: the mask 
    :width: the width of the image 
    :height: the height of the image
    """
    result = 0
    for i in range(0, height):
        for j in range (0,width):
            if(mask[i][j].all() == True):
                result += 1
    return result

def getGradeAndAccuracyScore(turthMaskTotal,userCorrectMaskTotal,userOverlapTotal):
    """ This is a simple score for the user mask of the truth mask and returns a grade and accuracy score.
    The closer the score is to 0 the better because it would mean 100% accuracy.  

    100       truth mask 
    --- X ------------------     = grade
     x     correct user mask 
    score = [(grade/100) * overlap] - overlap  
    :prams turthMaskTotal: the number of trues from the truth mask 
    :pramas userCorrectMaskTotal: the number trues between the user mask and the truth mask
    :pramas userOverlapTotal: the number of trues that overlap the area of the truth mask
    """
    grade = (userCorrectMaskTotal * 100) / turthMaskTotal
    #accuracyScore = ((grade/100) * userOverlapTotal) -userOverlapTotal
    accuracyScore = userOverlapTotal*-1
    #print(userOverlapTotal)
    #if((grade/100) == 1):
    #    accuracyScore = -userOverlapTotal
    return grade, accuracyScore

def getUserMaskAccuracy(user_mask, truth_mask, width, height):
    """This returns the grade and accuracy score of the truth mask and the user mask
    :return grade, accuracyScore: grade is a latter grade, and accuracyScore is the number of pixels that go over. The lower the number the better the score.  
    """
    #we calculate the number of pixels from the truth mask
    turthMaskTotal = boolCounter(truth_mask,width,height)
    #find the logical and array of turth mask and user mask 
    # (the coverage of the user on the turth mask)
    mask_and = user_mask & truth_mask
    #we calculate the number of pixels form the and mask 
    userCorrectMaskTotal = boolCounter(mask_and,width,height) 
    #we find the logical xor of the user mask and the turth mask 
    mask_xor = user_mask ^ truth_mask
     #we calculate the number of pixels from the xor mask
     # (the number of missed coverage by the user) 
    userOverlapTotal = boolCounter(mask_xor,width,height)
    return getGradeAndAccuracyScore(turthMaskTotal,userCorrectMaskTotal,userOverlapTotal)

def getAccumulativeScore(grade, gradeThreshold, accuracyScore, accuracyScoreThreshold, numberofCorrectMatches, numberofIncorrectMatches):
    """Accumulative score: This increments the number of games played by one. And has logic to handle the event of a first-time player. This return the new EloScore, the numberOfCorrectMatches, and the numberOfIncorrectMatches. 
    :param grade: the grade score of a mask 
    :param gradeThreshold: the threshold that prevents it from counting has being correct
    :parma accuracyScore: the accuracy score (number of overlapping pixels)
    :parma accuracyScoreThreshold: the threshold that prevents it form count has being correct
    :param numberOfGamesPlayed: the number of masked made by a player
    """
    #Score Constants
    value = 400 #the elo constant for score 
    firstTimeAdjust = .5 #the adjustment for a first time player (to prevent a high first score) 
    result = 0 #Do we consider this a correct match?
    #return value
    newElo = 0
    if (grade >= gradeThreshold and accuracyScore >= accuracyScoreThreshold):
        result += 1
    if(result == 1): #this means consider this a match
        numberofCorrectMatches += 1
    else:            #this means we do not consier this a match 
        numberofIncorrectMatches += 1
    
    TotalNumberOfGamesPlayed = numberofCorrectMatches+numberofIncorrectMatches
    if(numberofCorrectMatches == 0): 
        newElo = (value*firstTimeAdjust-value*numberofIncorrectMatches)/(firstTimeAdjust+numberofIncorrectMatches)
    elif (numberofIncorrectMatches == 0):
        newElo = (value*numberofCorrectMatches-value*firstTimeAdjust)/(firstTimeAdjust*numberofCorrectMatches)
    else: 
        newElo = (value*numberofCorrectMatches-value*numberofIncorrectMatches)/TotalNumberOfGamesPlayed
    newElo = newElo/400
    return newElo, numberofCorrectMatches, numberofIncorrectMatches

def basicFileReader(path):
    """This returns a list of files from the provided path. 
    path e.g, "foo\\*.ext"
    """
    filesList = []
    filesList = glob.glob(path)
    return filesList

def loadJsonDataObj(path):
    """This takes a path to the userJson file
        then then returns a python json object
    """
    #open the path with the json in it and safe the files  
    files = basicFileReader(path)
    #should be only the first one, and we want to turn 
    # the json into a object so it can be returned  
    with open(files[0]) as f:
        data = json.load(f)
    f.close()
    return data, files[0]

def getUserScoreFromJson(data,currentUser):
    """Retruns elo, correctMatches, and incorrectMatches
       for a given current user
    """
    elo = 1
    correctMatches = 1
    incorrectMatches = 1
    isFound = False
    for i in range(0,len(data['users'])):
        if data['users'][i]['id'] == currentUser:
            # print(data['users'][i]['elo'])
            elo = data['users'][i]['elo']
            # print(data['users'][i]['correctMatches'])
            correctMatches = data['users'][i]['correctMatches']
            # print(data['users'][i]['incorrectMatches'])
            incorrectMatches = data['users'][i]['incorrectMatches']
            isFound = True
    if isFound != True:
        print("Error: user id={} NOT FOUND".format(currentUser))
    return elo, correctMatches, incorrectMatches

def setUserScoreFromJson(data,currentUser, elo,correctMatches,incorrectMatches):
    """Sets the elo, correctMatches, and incorrectMatches
    for a given current user. And return the data
    """
    isFound = False
    for i in range(0,len(data['users'])):
        if data['users'][i]['id'] == currentUser:
            data['users'][i]['elo'] =  elo
            data['users'][i]['correctMatches'] = correctMatches
            data['users'][i]['incorrectMatches'] = incorrectMatches
            isFound = True
    if isFound != True:
        print("Error: user id={} NOT FOUND".format(currentUser))
    return data

def saveJsonDataObjToFile(data,outPath):
    """This takes a json data object and saves it the outPath
    """
    with open(outPath,'w') as outfile:
        json.dump(data, outfile)
    outfile.close()

def checkIfFileExistToMake(path, include):
    """Checks if a from the provided path exist and
    if it does not it creates it.
    Example use: "foo"+os.path.sep+"bar.ext"
    :include: the stuff you want in the file as a default 
    """
    CHECK_FOLDER = os.path.isfile(path)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
        with open(path, 'w') as f:
            f.write(include)
        f.close()

def setConsensusMaskJson(jsonPath,currentEloScore,imageFilePath,userId):
    """This saves the consensus mask with the image path and score data 
       to a json file. It only appends.
    :jsonPath: the folder path 
    """
    jsonDefaultData = "{\"conMasks\": []}"
    #check if the path exist to see if we need to make it 
    checkIfPathExistToMake(jsonPath)
    #check if we already have a data.json and whether we need to make it 
    checkIfFileExistToMake(jsonPath+os.sep+"data.json", jsonDefaultData)
    #open the json file and append to it
    dataJson, filePath = loadJsonDataObj(jsonPath+os.sep+"data.json")  
    #append the file with the new data 
    dataJson['conMasks'].append({
        'path': imageFilePath,
        'currentElo': currentEloScore,
        'user': userId})
    #save the file with the new data in it 
    with open(filePath, 'w') as outfile:
        json.dump(dataJson, outfile)
    outfile.close()

def checkIfPathExistToMake(path):
    """Checks if the directory from the provided path exist and
        if it does not it creates it.
        Example use: "foo"+os.path.sep+"bar"
    """
    CHECK_FOLDER = os.path.isdir(path)
    # If folder doesn't exist, then create it.
    if not CHECK_FOLDER:
     os.makedirs(path)

def makeGroupMask(groupMaskValues):
    """This takes a mask and fills it with empty false values as 
        it is the group mask. This returns a group mask of empty 
        float values
    """
    result = groupMaskValues.copy()
    result.fill(False)
    result = result.astype('float64')
    return result

def addToGroupMask(elo,groupMaskValues,imageMaskArray,width,height):
    """This takes the accumulative score of a user and adds it as a weight to
    the group mask values based on the consensus mask 
    """
    for i in range(0,height):
        for j in range (0,width):
            if(imageMaskArray[i][j].all() == True):
                groupMaskValues[i][j] += elo
    return groupMaskValues

def getConsensusMask(threshold,groupMaskValues,imageMaskArray,width,height):
    """This takes a threshold value and the groupMaskValues and based on the mask 
    retruns a consensus mask. 
    """
    result = imageMaskArray.copy()
    result = result ^ result #clear all true values 
    thresholdList = [threshold,threshold,threshold] 
    for i in range(0,height):
        for j in range (0,width):
            if((groupMaskValues[i][j] >= thresholdList).all()):
                result[i][j].fill(True)
    return result

def findTheLowestOfTheValues(max,groupMaskValues, height, width):
    """Find the loweset value of the groupMask values because the size 
        need needs to be removed from the threshold used otherwise the 
        threshold value will be off. 
     """
    result = max
    for i in range(0,height):
        for j in range (0,width):
            if(groupMaskValues[i][j][0] < result):
                result = groupMaskValues[i][j][0]
                print(result)
    return result

def computeConsensusMaskAndSave(jsonPath,outPath):
    """This calculates the consensus mask then saves the current consensus mask
    based on the data in the consensus mask json path 
    """
    jsonDataOBJ, files = loadJsonDataObj(jsonPath+os.sep+"data.json") #consensusMaskJsonPath+os.sep+"data.json"
    #open the first image to get the width and height of it 
    
    print(jsonDataOBJ['conMasks'][0]['path'])

    #get the input image 
    input_img_source = Image.open(jsonDataOBJ['conMasks'][0]['path'])
    width, height = input_img_source.size
    #convert into array 
    input_img_array = cv2.imread(jsonDataOBJ['conMasks'][0]['path'])
    #make covert to a mask 
    temp = getImageToMask(input_img_array)
    #create empty group mask of float values 
    groupMaskValues = makeGroupMask(temp)
    #create a boolean group mask of the initial image 
    groupMask = temp

    #get the values for the consensus threshold
    #which is thresh = total - avg
    total = 0
    #for each consensus image we have add the weights to the group mask 
    for i in range(0,len(jsonDataOBJ['conMasks'])):
      #Convert the first image to a mask 
      temp = getImageToMask(cv2.imread(jsonDataOBJ['conMasks'][i]['path']))
      #update group mask values based on the user accumulative score  
      groupMaskValues = addToGroupMask(jsonDataOBJ['conMasks'][i]['currentElo'],groupMaskValues,temp,width,height)
      #logical or the values from temp to the groupMask 
      groupMask = groupMask | temp
      #get the total score of weights  
      total = total + jsonDataOBJ['conMasks'][i]['currentElo']

    #compute the threshold value 
    avg = total / len(jsonDataOBJ['conMasks'])
    threshTemp = total - avg
    lowest = findTheLowestOfTheValues(total,groupMaskValues,height,width)
    thresh = threshTemp - lowest

    print("Current Consensus Mask Values-----")
    print("Total Possable Consensus    :{}".format(total)) 
    print("Average Possable Consensus  :{}".format(avg))
    print("Lowest Value Of Masks       :{}".format(lowest))
    print("Number of Masks             :{}".format(len(jsonDataOBJ['conMasks'])))
    print("thresh = total - avg        :{}".format(threshTemp))
    print("thresh = threshTemp - lowest:{}".format(thresh))
    print("----------------------------------")

    #save the full mask of all values
    # make the initial image all black so we can save the mask to it 
    temp = input_img_array * 0 
    temp = applyWhiteMask(groupMask,temp,width,height)
    cv2.imwrite(outPath+os.path.sep+"absoluteConsensus.png",temp)
    
    #get the consensus mask 
    groupMask = getConsensusMask(thresh,groupMaskValues,groupMask,width,height)

    #save the current consensusMask
    temp = input_img_array * 0 
    temp = applyWhiteMask(groupMask,temp,width,height) 
    cv2.imwrite(outPath+os.path.sep+"currentConsensus.png",temp)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
    #app.run(debug=True)
    #app.run()