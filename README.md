

# ImageMaker

Crowdsourced image masking proof of concept.

# Why? 

This is a class project created for CIS 556 : Gamification Design at the University of Massachusetts Dartmouth

# Q: What is this?  

ImageMasker is a simple web application that demonstrates multiple users can be trained to mask an image and develop an accumulative score based on skill.  So that when said users are faced with a hypothetical unidentified image. They can attempt to mask it such that their collective masks will generate a reasonable consensus masking based on their collective skill i.e., weights. 
This project was inspired entirely by [Stall Catchers](https://stallcatchers.com/main) and their plan to incorporate crowdsourced masking. 

# Cool what was this made with? 

ImageMasker is made with Flask and uses jinja templates. All the image processing is done in python. All the python functions have been written such that they could be used anywhere for any images. For example, the browser does not natively support .tif images however the python image processing functions can. Additionally, all the functions are simple enough that in theory they could be ported into any language. As for the web application itself the entirety of it is written in vanilla JavaScript, html, and css. The Flask server does not have any database and writes flat files onto disk including the json files it uses. 

# Um… Ok how do I run it? 

Clone into folder. Have python installed. I used python version 3. pip install Flask. Try to run app.py. Can’t run because you are missing something? Look up how to pip install whatever library you are missing. Keep doing it until you can run it. Open browser in incognito mode and go to http://127.0.0.1:5000/
It’s simple. 

# Thanks, I guess? 

No problem. 😃

# Continuing Development Notes 

As this is a prototype and not ready for deployment below is a list of general areas that should be addressed 
in this project to continue development. 

* Optimize GET and POST request (they are slow and some times fail)
* Build a database to store images as blobs and user data (currently everything is flat files). Doing so will allow for a more dynamic server state for n users and facilitate the collection and analysis of more data.
* Optimize / develop more dynamic consensus threshold methods (easier to do when there is a database of images to use). 