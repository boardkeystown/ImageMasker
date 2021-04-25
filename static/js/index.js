/**************************Global Constants ************************/

/**The colors used to mask (really only need white)*/
const colors = ['white'];
/**the brush size used for the canvas*/
const size = [20, 40, 80];
/**the brush size names*/
const sizeNames = ['small-brush', 'medium-brush', 'large-brush'];

/**************************Global Variables  ************************/

/**
 * this is the current users loaded in.
 * seriously bad way to this. Because it defaults to use and there is 
 * is nothing to prevent sending things as user 1. TO BAD! 
*/
var CURRENT_USER = 1;


/**************************Canvas set up ************************/

/**
* Lets user put a image onto the canvas
* NOTE: A "Canvas" is really 2 one with the image behind 
* and one on top that is used to draw onto.  
* And both are resized when a image is loaded. 
* @param layer0 the name of the bottom layer (the one with the image)
* @param layer1 the name of the top layer (the one you can draw on)
* @param containerName the name of the container that needs to be resized
* @param uploadedImage the uploaded image tag 
*/
function draw(layer0, layer1, containerName, uploadedImage) {
    var ctx = document.getElementById(layer0).getContext('2d'),
        img = new Image(),
        f = document.getElementById(uploadedImage).files[0],
        url = window.URL || window.webkitURL,
        src = url.createObjectURL(f);
    var ctx2 = document.getElementById(layer1).getContext('2d');
    img.src = src;
    img.onload = function () {
        ctx2.canvas.width = img.width;
        ctx2.canvas.height = img.height;
        canvasInit(ctx2);
        ctx.canvas.width = img.width;
        ctx.canvas.height = img.height;
        resizeCanvasContainers(containerName, img.width, img.height);
        ctx.drawImage(img, 0, 0);
        url.revokeObjectURL(src);
    }
}


/**
* Lets user put a image onto the canvas
* NOTE: A "Canvas" is really 3 one with the image behind 
* and one on top that is used to draw onto.  
* And both are resized when a image is loaded. 
* @param layer0 the name of the bottom layer (the one with the image)
* @param layer1 the name of the middle layer (the one you can draw on)
* @param layer2 the name of the top layer (the one you can draw on)
* @param containerName the name of the container that needs to be resized
* @param uploadedImage the uploaded image tag 
*/
function draw3(layer0, layer1, layer2, containerName, uploadedImage) {
    var ctx = document.getElementById(layer0).getContext('2d'),
        img = new Image(),
        f = document.getElementById(uploadedImage).files[0],
        url = window.URL || window.webkitURL,
        src = url.createObjectURL(f);
    var ctx2 = document.getElementById(layer1).getContext('2d');
    var ctx3 = document.getElementById(layer2).getContext('2d');

    img.src = src;
    img.onload = function () {
        ctx2.canvas.width = img.width;
        ctx2.canvas.height = img.height;
        ctx3.canvas.width = img.width;
        ctx3.canvas.height = img.height;
        canvasInit(ctx3);
        ctx.canvas.width = img.width;
        ctx.canvas.height = img.height;
        resizeCanvasContainers(containerName, img.width, img.height);
        ctx.drawImage(img, 0, 0);
        url.revokeObjectURL(src);
    }
}

/**
 * Resize the canvas container when a image is loaded. 
 * @param containerName 
 * @param width width of the image 
 * @param height height of the image
*/
function resizeCanvasContainers(containerName, width, height) {
    var x = document.getElementById(containerName);
    x.style.width = width + "px";
    x.style.height = height + "px";
}


/** Draws the chosen image to the different canvases */
document.getElementById("upload-image").addEventListener("change", function () {
    //The truth mask 
    draw("myCanvas", "myCanvasMask", "canvas-container1", "upload-image");
    //User mask 
    //draw("myCanvasUser", "myCanvasMaskUser", "canvas-container2", "upload-image");
    draw3("myCanvasUser", "myCanvasMaskUser_truth", "myCanvasMaskUser", "canvas-container2", "upload-image");
    //Consensus mask 
    draw("myCanvasUser2", "ConsensusMask", "canvas-container3", "upload-image");
    //Final Consensus mask 
    draw("myCanvasUser3", "FinalConsensusMask", "canvas-container4", "upload-image");


    //Save the source image for later processing 
    sendSourceImageToServer("upload-image");

}, false);


/**
 * This initializes the canvas context to some default values
 * @param canvasContext the canvas context used  
*/
function canvasInit(canvasContext) {
    canvasContext.strokeStyle = colors[0]; //Set to white 
    canvasContext.fillStyle = size[0];  //set to 20 px 
}



/**This sends the source image to the server*/
function sendSourceImageToServer(uploadedImage) {

    //var file = document.querySelector('input[type=file]')['files'][0];
    file = document.getElementById(uploadedImage).files[0]
    var reader = new FileReader();
    var baseString;
    reader.onloadend = function () {
        baseString = reader.result;
        //console.log(baseString); 
        var r = new XMLHttpRequest();
        r.open("POST", "http://127.0.0.1:5000/getSourceImg", true);
        r.onreadystatechange = function () {
            if (r.readyState != 4 || r.status != 200) return;
            //alert("Success: " + r.responseText);
            console.log(r.responseText);
        };
        // Send data in below way from JS
        r.send(JSON.stringify({ "input": baseString }));
    };
    reader.readAsDataURL(file);
}


/**************************The mask canvases and listeners ************************/

//TRUTH MASK canvas  
/**The drawable truth mask layer*/
const canvasTruthMask = document.getElementById('myCanvasMask');
/*The truth mask 2d context*/
const ctxTruthMask = canvasTruthMask.getContext('2d');

//USER MASK canvas 
/**The drawable user mask layer*/
const canvasUserMask = document.getElementById('myCanvasMaskUser');
/*The user mask 2d context*/
const ctxUserMask = canvasUserMask.getContext('2d');

//TODO Add this ? 
const canvasSavedTruthMask = document.getElementById('myCanvasMaskUser_truth');
// /*The user mask 2d context*/
const ctxSavedTruthMask = canvasSavedTruthMask.getContext('2d');

//USER CONSENSUS MASK
const canvasConsensusMask = document.getElementById('ConsensusMask');
/*The user mask 2d context*/
const ctxConsensusMask = canvasConsensusMask.getContext('2d');

//FINAL CONSENSUS MASK
const canvasFinalConsensusMask = document.getElementById('FinalConsensusMask');
/*The user mask 2d context*/
const ctxFinalConsensusMask = canvasFinalConsensusMask.getContext('2d');

//TRUTH MASK LISTENERS 
//Mouse down event 
canvasTruthMask.addEventListener('mousedown', (evt) => {
    let mousePos = getMousePos(canvasTruthMask, evt);
    ctxTruthMask.beginPath();
    ctxTruthMask.moveTo(mousePos.x, mousePos.y);
    evt.preventDefault();
    canvasTruthMask.addEventListener('mousemove', mouseMove, false);
});

//Mouse up event 
canvasTruthMask.addEventListener('mouseup', () => {
    canvasTruthMask.removeEventListener('mousemove', mouseMove, false);
}, false);

//truth mask reset button 
document.getElementById('reset').addEventListener('click', () => {
    ctxTruthMask.clearRect(0, 0, canvasTruthMask.width, canvasTruthMask.height);
}, false);


/**The send button for the truth mask, 
 * sends to the server the current truth mask drawn
*/
document.getElementById("sendbutton").addEventListener('click', () => {

    //We sent the truth mask to the server to be drawn
    var image = canvasTruthMask.toDataURL();
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/truthMask", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        console.log(r.responseText);
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "input": image }));

});


/**set the red truth mask*/
function setRedTruthMask() {
    let xhr = new XMLHttpRequest();
    // Setup our listener to process compeleted requests
    xhr.onreadystatechange = function () {
        ctxSavedTruthMask.clearRect(0, 0, ctxSavedTruthMask.width, ctxSavedTruthMask.height);

        // Only run if the request is complete
        if (xhr.readyState !== 4) return;

        // Process our return data
        if (xhr.status >= 200 && xhr.status < 300) {
            // What do when the request is successful
            console.log("Red truth mask!");
            console.log(JSON.parse(xhr.responseText));
            let dataResponse = JSON.parse(xhr.responseText);
            let img = new Image();
            img.src = dataResponse.image_url;
            ctxSavedTruthMask.drawImage(img, 0, 0);
            var imageData = ctxSavedTruthMask.getImageData(0, 0, canvasSavedTruthMask.width,
                canvasSavedTruthMask.height);
            var data = imageData.data;
            //This restores alpha to the black pixels 
            var removeBlack = function () {
                for (var i = 0; i < data.length; i += 4) {
                    if (data[i] + data[i + 1] + data[i + 2] < 10) {
                        data[i + 3] = 0; // alpha
                    }
                }
                ctxSavedTruthMask.putImageData(imageData, 0, 0);
            };
            removeBlack();
        }
    };
    // Create and send a GET request
    // The first argument is the post type (GET, POST, PUT, DELETE, etc.)
    // The second argument is the endpoint URL
    xhr.open('GET', 'http://127.0.0.1:5000/getImageRedMask');
    xhr.send();
}



//USER MASK LISTENERS

//Mouse down event 
canvasUserMask.addEventListener('mousedown', (evt) => {
    let mousePos = getMousePos(canvasUserMask, evt);
    ctxUserMask.beginPath();
    ctxUserMask.moveTo(mousePos.x, mousePos.y);
    evt.preventDefault();
    canvasUserMask.addEventListener('mousemove', mouseMove, false);
});

//Mouse up event 
canvasUserMask.addEventListener('mouseup', () => {
    canvasUserMask.removeEventListener('mousemove', mouseMove, false);
}, false);

//truth mask reset button 
document.getElementById('reset2').addEventListener('click', () => {
    ctxUserMask.clearRect(0, 0, canvasUserMask.width, canvasUserMask.height);
    ctxSavedTruthMask.clearRect(0, 0, canvasSavedTruthMask.width, canvasSavedTruthMask.height);
}, false);


//truth mask reset button 
document.getElementById('hardReset').addEventListener('click', () => {
    var image = canvasTruthMask.toDataURL();
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/hardUserReset", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        console.log(r.responseText);
    };
    r.send(JSON.stringify({ "input": "foo" }));
}, false);


/**The send button for the truth mask, 
 * sends to the server the current truth mask drawn
*/
document.getElementById("sendUserMask").addEventListener('click', () => {
    //Send the user mask 
    var image = canvasUserMask.toDataURL();
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/userMask", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        setRedTruthMask();
        console.log("sent");
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "input": image }));
});


document.getElementById("getScore").addEventListener('click', () => {
    // Set up our HTTP request
    var xhr = new XMLHttpRequest();

    // Setup our listener to process compeleted requests
    xhr.onreadystatechange = function () {
        // Only run if the request is complete
        if (xhr.readyState !== 4) return;

        // Process our return data
        if (xhr.status >= 200 && xhr.status < 300) {
            // What do when the request is successful
            console.log(JSON.parse(xhr.responseText));
            let data = JSON.parse(xhr.responseText);
            //Update score 
            setUserResults(data.elo, data.grade, data.score); 
            //Show result message
            setMaskResponse(data.isCorrect, false);
            //set the bar
            resultBar(data.score,data.thresh,false);
        }
    };
    // Create and send a GET request
    // The first argument is the post type (GET, POST, PUT, DELETE, etc.)
    // The second argument is the endpoint URL
    xhr.open('GET', 'http://127.0.0.1:5000/getUserScore');
    xhr.send();
});


/**This moves the result bar to show how accurate the mask is*/
function resultBar(score, thresh, setToBlack) {
    let n = document.getElementById("myProgress");
    let x = document.getElementById("myBar");

    //We want to make the bar clear because not in use 
    if(setToBlack == true) {
        n.style.backgroundColor = "rgba(255, 0, 0, 0)";
        x.style.backgroundColor = "rgba(255, 0, 0, 0)";
        return;
    }
    n.style.backgroundColor = "rgb(86, 177, 101)"; //Set the green color

    x.style.width = 0 + "%"; //RESET THE RED WIDTH
    x.style.backgroundColor = "#af544c" //SET TO RED 


    let scoreLocal = score * -1;
    let threshLocal = thresh *-1;
    let moveAmount = 100; //BAD

    if(scoreLocal < threshLocal) {
        let temp = scoreLocal * 100;
        moveAmount = Math.floor(temp / threshLocal);
    } 

    //console.log(moveAmount)

    var elem = document.getElementById("myBar");
    var width = 1;
    var id = setInterval(frame, 10);
    function frame() {
      if (width >= moveAmount) {
        clearInterval(id);
        i = 0;
      } else {
        width++;
        elem.style.width = width + "%";
      }
    }
}

resultBar(0,0,true);


/**
 * This sets the user scores returned
*/
function setUserResults(elo, grade, score) {
    let a = document.getElementsByClassName('userElo');
    a[0].innerText = "Rank: " + elo;
    a[1].innerText = "Rank: " + elo;
    let b = document.getElementsByClassName('grade');
    b[0].innerText = "Grade: " + grade;
    let c = document.getElementsByClassName('score');
    c[0].innerText = "Par: " + score*-1;
}
/**This sets the mask response message based on whether the mask was correct or not.*/
function setMaskResponse(result, isReset) {
    let a = document.getElementsByClassName('maskResult');
    if (isReset == true) {
        a[0].innerText = "Result: ";
        return;
    }
    if (result == true) {
        a[0].innerText = "Result: " + getMessage(true);
    } else {
        a[0].innerText = "Result: " + getMessage(false);
    }
}

/**This returns either a correct message or a incorrect message*/
function getMessage(bool) {
    let index = getRandomInt(5) //random number 0-4

    let goodMessages = ["Great job!😁", "🤘You rock!🤘", "Wow Good Job!", "👏Great Match!👏", "Solid match!"];
    let badMessages = ["You suck lol", "Not quite right...", "Poor match...", "You can do better...", "Bad match..."];
    if (bool == true) {
        return goodMessages[index];
    } else {
        return badMessages[index];
    }
}

/**Generates a random int*/
function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

/**Show the ground truth mask*/
document.getElementById("getGroundTruth").addEventListener('click', () => {
    setRedTruthMask();
});


//Consensus LISTENERS
//Mouse down event 
canvasConsensusMask.addEventListener('mousedown', (evt) => {
    let mousePos = getMousePos(canvasConsensusMask, evt);
    ctxConsensusMask.beginPath();
    ctxConsensusMask.moveTo(mousePos.x, mousePos.y);
    evt.preventDefault();
    canvasConsensusMask.addEventListener('mousemove', mouseMove, false);
});

//Mouse up event 
canvasConsensusMask.addEventListener('mouseup', () => {
    canvasConsensusMask.removeEventListener('mousemove', mouseMove, false);
}, false);


/**The send button for the user consensus mask 
 * sends to the server the current consensus mask 
*/
document.getElementById("sendConsensusMask").addEventListener('click', () => {
    var image = canvasConsensusMask.toDataURL();
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/consensusMask", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        console.log("sent");
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "input": image }));
});


//Reset the consensus mask
document.getElementById('reset3').addEventListener('click', () => {
    ctxConsensusMask.clearRect(0, 0, canvasConsensusMask.width, canvasConsensusMask.height);
}, false);


//HARD RESET OF consensus mask values 
document.getElementById('hardResetConsensusMask').addEventListener('click', () => {
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/hardResetConsensusMask", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        console.log(r.responseText);
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "input": "foo" }));
}, false);


//FINAL CONSENSUS MASK
document.getElementById("getCurrentConsensusMask").addEventListener('click', () => {
    var xhr = new XMLHttpRequest();

    // Setup our listener to process compeleted requests
    xhr.onreadystatechange = function () {
        // Only run if the request is complete
        if (xhr.readyState !== 4) return;

        // Process our return data
        if (xhr.status >= 200 && xhr.status < 300) {
            // What do when the request is successful
            console.log("I got the image");
            console.log(JSON.parse(xhr.responseText));
            let dataResponse = JSON.parse(xhr.responseText);


            let img = new Image();
            img.src = dataResponse.image_url;


            ctxFinalConsensusMask.drawImage(img, 0, 0);
            var imageData = ctxFinalConsensusMask.getImageData(0, 0, canvasFinalConsensusMask.width,
                canvasFinalConsensusMask.height);
            var data = imageData.data;
            //This restores alpha to the black pixels 
            var removeBlack = function () {
                for (var i = 0; i < data.length; i += 4) {
                    if (data[i] + data[i + 1] + data[i + 2] < 10) {
                        data[i + 3] = 0; // alpha
                    }
                }
                ctxFinalConsensusMask.putImageData(imageData, 0, 0);
            };
            removeBlack();
        }
    };
    // Create and send a GET request
    // The first argument is the post type (GET, POST, PUT, DELETE, etc.)
    // The second argument is the endpoint URL
    xhr.open('GET', 'http://127.0.0.1:5000/getImage');
    xhr.send();
});


//Reset the consensus mask
document.getElementById('reset4').addEventListener('click', () => {
    ctxFinalConsensusMask.clearRect(0, 0, canvasFinalConsensusMask.width, canvasFinalConsensusMask.height);
}, false);


var WAIT_UNTIL_DONE = false;
document.getElementById('downloadIMG').addEventListener('click', () => {
    if (WAIT_UNTIL_DONE == true) {
        return;
    }

    var xhr = new XMLHttpRequest();
    // Setup our listener to process compeleted requests
    xhr.onreadystatechange = function () {
        // Only run if the request is complete
        if (xhr.readyState !== 4) return;

        // Process our return data
        if (xhr.status >= 200 && xhr.status < 300) {
            // What do when the request is successful
            console.log("I got the image");
            console.log(JSON.parse(xhr.responseText));
            let dataResponse = JSON.parse(xhr.responseText);

            saveBase64AsFile(dataResponse.image_url, "outFile.png");
            WAIT_UNTIL_DONE = false;
        }
    };
    // Create and send a GET request
    // The first argument is the post type (GET, POST, PUT, DELETE, etc.)
    // The second argument is the endpoint URL
    xhr.open('GET', 'http://127.0.0.1:5000/getFinalImage');
    xhr.send();

}, false);


function saveBase64AsFile(base64, fileName) {
    var link = document.createElement("a");
    document.body.appendChild(link);
    link.setAttribute("type", "hidden");
    //link.href = "data:text/plain;base64," + base64;
    link.href = base64;
    link.download = fileName;
    link.click();
    document.body.removeChild(link);
}




/**************************Reusable Canvas functions ************************/

/**
* Return the mouse position of a canvas 
* @param canvas the canvas used 
* @param evt the mouse event 
*/
function getMousePos(canvas, evt) {
    let rect = canvas.getBoundingClientRect();
    return {
        x: evt.clientX - rect.left,
        y: evt.clientY - rect.top
    };
}

/**
* move the mouse for the appropriate canvas 
* @param evt the mouse event 
*/
function mouseMove(evt) {
    console.log(evt.target.id);
    if (evt.target.id.localeCompare('myCanvasMask') == 0) {
        //Truth mask 
        let mousePos = getMousePos(canvasTruthMask, evt);
        ctxTruthMask.lineTo(mousePos.x, mousePos.y);
        ctxTruthMask.stroke();
    }
    if (evt.target.id.localeCompare('myCanvasMaskUser') == 0) {
        //User mask 
        let mousePos = getMousePos(canvasUserMask, evt);
        ctxUserMask.lineTo(mousePos.x, mousePos.y);
        ctxUserMask.stroke();
    }
    if (evt.target.id.localeCompare('ConsensusMask') == 0) {
        //User mask 
        let mousePos = getMousePos(canvasConsensusMask, evt);
        ctxConsensusMask.lineTo(mousePos.x, mousePos.y);
        ctxConsensusMask.stroke();
    }
}


/*
function listener(i) {
    document.getElementById(colors[i]).addEventListener('click', () => {
        ctx.strokeStyle = colors[i];
    }, false);
}
*/

//TODO: make it more generic for all the mouse buttons 
/**
 * Adds all the buttons to change the size of the line. 
 * 
*/
function fontSizes(i) {
    document.getElementById(sizeNames[i]).addEventListener('click', () => {
        ctxTruthMask.strokeStyle = "white";
        ctxTruthMask.lineWidth = size[i];
    }, false);
    document.getElementById(sizeNames[i] + "2").addEventListener('click', () => {
        ctxUserMask.strokeStyle = "white";
        ctxUserMask.lineWidth = size[i];
    }, false);
    document.getElementById(sizeNames[i] + "3").addEventListener('click', () => {
        ctxConsensusMask.strokeStyle = "white";
        ctxConsensusMask.lineWidth = size[i];
    }, false);

}

/*
for (let i = 0; i < colors.length; i++) {
    
}
*/

for (let i = 0; i < size.length; i++) {
    fontSizes(i);
}


function forText() {
    var image = canvasTruthMask.toDataURL();
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/truthMask", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) return;
        //alert("Success: " + r.responseText);
        console.log("sent");
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "input": "test" }));
}




/**************************Init Users ************************/

/*Set up the user buttons loaded in from JSON and allows the CURRENT_USER to be changed 
   respectively */
function initUsers(i, idName, idNameOther) {
    var tableRow = document.getElementById(idName)
    let x = tableRow.insertCell(tableRow.length);
    x.innerText = "user" + i;
    x.className = "users-btn";
    x.addEventListener('click', () => {
        var id = i;
        setButtonHighlight(id, idName, idNameOther);
        console.log("click form id: " + id);
        CURRENT_USER = id;
        sendCurrentUser();
    }, false);
}

/*set the button highlight*/
function setButtonHighlight(current, idNameChange, idNameChangeOther) {
    let tableRow = document.getElementById(idNameChange);
    let tableRow2 = document.getElementById(idNameChangeOther);
    kids = tableRow.children;
    kids2 = tableRow2.children;
    for (let i = 0; i < kids.length; i++) {
        kids[i].classList.remove("user-btn-select");
        kids2[i].classList.remove("user-btn-select");
    }
    kids[current - 1].classList.add("user-btn-select");
    kids2[current - 1].classList.add("user-btn-select");


}


/**sends to the server the current user selected*/
function sendCurrentUser() {
    //Send the current user
    var r = new XMLHttpRequest();
    r.open("POST", "http://127.0.0.1:5000/getCurrentUser", true);
    r.onreadystatechange = function () {
        if (r.readyState != 4 || r.status != 200) {
            //alert("Success: " + r.responseText);
            console.log(r.responseText);
            let data = JSON.parse(r.responseText);
            setUserResults(data.elo, 0.0, 0.0);
            setMaskResponse(false, true);
            resultBar(0,0,true);
            console.log("sent");
            return;
        }
    };
    // Send data in below way from JS
    r.send(JSON.stringify({ "id": CURRENT_USER }));
}


/**
 * Load in the users from the json file 
 * should set up a database. TO BAD! 
 * **/
var ONLYDOONETIME = true;
document.getElementById("loadUsers").addEventListener('click', () => {
    if (ONLYDOONETIME == true) {
        // Set up our HTTP request
        var xhr = new XMLHttpRequest();
        // Setup our listener to process compeleted requests
        xhr.onreadystatechange = function () {
            // Only run if the request is complete
            if (xhr.readyState !== 4) return;

            // Process our return data
            if (xhr.status >= 200 && xhr.status < 300) {
                // What do when the request is successful
                console.log(JSON.parse(xhr.responseText));
                data = JSON.parse(xhr.responseText);
                for (let i = 0; i < data.length; i++) {
                    initUsers(data[i], 'users', 'users2');
                    initUsers(data[i], 'users2', 'users');
                }
            }

        };
        // Create and send a GET request
        // The first argument is the post type (GET, POST, PUT, DELETE, etc.)
        // The second argument is the endpoint URL
        xhr.open('GET', 'http://127.0.0.1:5000/initUsers');
        xhr.send();
        ONLYDOONETIME = false;
    }
});