

# ImageMasker

Crowdsourced image masking proof of concept.

![image](https://user-images.githubusercontent.com/43831063/116169594-0ceb7580-a6d3-11eb-884b-044eee75f6f3.png)


# Why? 

This is a class project created for CIS 556 : Gamification Design at the University of Massachusetts Dartmouth

# What is this?  

ImageMasker is a simple web application that demonstrates multiple users can be trained to mask an image and develop an accumulative score based on skill.  So that when said users are faced with a hypothetical unidentified image. They can attempt to mask it such that their collective masks will generate a reasonable consensus masking based on their collective skill i.e., weights. 
This project was inspired entirely by [Stall Catchers](https://stallcatchers.com/main) and their plan to incorporate crowdsourced masking. 

# Cool what was this made with? 

ImageMasker is made with Flask and uses jinja templates. All the image processing is done in python. All the python functions have been written such that they could be used anywhere for any images. For example, the browser does not natively support .tif images however the python image processing functions can. Additionally, all the functions are simple enough that in theory they could be ported into any language. As for the web application itself the entirety of it is written in vanilla JavaScript, html, and css. The Flask server does not have any database and writes flat files onto disk including the json files it uses. 

# Um… Ok how do I run it? 

It’s simple. Clone into folder. Have python installed. I used python version 3. pip install Flask. Try to run app.py. Can’t run because you are missing something? Look up how to pip install whatever library you are missing. Keep doing it until you can run it. Open browser in incognito mode and go to http://127.0.0.1:5000/


# Thanks, I guess? 

No problem. 😃

# Wait I got it run how do I use it? 
Oh yeah, no problem. Recall that I said there is no database and that everything is flat files. The app works in sequence. 
#### Truth Mask
You open a source image (currently works with only with .png images in the browser albeit the Python should work with any images). Choose a brush, then mask an image. And SEND it to the server. 
#### Train user 
LOAD THE USERS. Choose a user, then a brush, then mask. SEND it to the server. SHOW RESULTS to update the user score. You can also click SEE GROUND TRUTH to see the truth mask. Click reset image to clear the canvas. RESET ALL USERS clears the json for all the users.  
#### Consensus masking 
Same procedure in train user. But Hard Reset All clears the json that stores the information for the mask. You can always save it if you want to test for some reason. Everything is flat files.
#### Consensus Mask 
Show mask will calculate the current mask. Only works for n+2 user mask. If it does not show up just smash the button until it does (it’s slow flat files). Download will apply the current mask to the source image. 


And have fun don’t worry. You can also change the current sub folder in the code or adjust thresholds for training users by changing the constants at the start of app.py 

SEE: 
* GRADETHRESH 0 to 100
* MISSINGTHRESH 0 to -n
* currentSubPath = 0 to n (this is the sub folder all the images and data will be saved into) Handy you want to save and test the results of different trained users and source images.

# Continuing Development Notes 

As this is a prototype and not ready for deployment below is a list of general areas that should be addressed in this project to continue development. 

* Optimize GET and POST request (they are slow and sometimes fail)
* Build a database to store images as blobs and user data (currently everything is flat files). Doing so will allow for a more dynamic server state for n users and facilitate the collection and analysis of more data.
* Optimize / develop more dynamic consensus threshold methods (easier to do when there is a database of images to use).
