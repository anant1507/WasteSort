// ! Functions that deal with button events
$(function () {
  // * Preview switch
  $("a#cam-preview").bind("click", function () {
    $.getJSON("/request_preview_switch", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * Flip horizontal switch
  $("a#flip-horizontal").bind("click", function () {
    $.getJSON("/request_flipH_switch", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * Model switch
  $("a#use-model").bind("click", function () {
    $.getJSON("/request_model_switch", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * exposure down
  $("a#exposure-down").bind("click", function () {
    $.getJSON("/request_exposure_down", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * exposure up
  $("a#exposure-up").bind("click", function () {
    $.getJSON("/request_exposure_up", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * contrast down
  $("a#contrast-down").bind("click", function () {
    $.getJSON("/request_contrast_down", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * contrast up
  $("a#contrast-up").bind("click", function () {
    $.getJSON("/request_contrast_up", function (data) {
      // do nothing
    });
    return false;
  });
});

$(function () {
  // * reset camera
  $("a#reset-cam").bind("click", function () {
    $.getJSON("/reset_camera", function (data) {
      // do nothing
    });
    return false;
  });
});

// Function to play Punjabi audio based on waste type
function playAudio(wasteType) {
    let audioFile;
    if (wasteType === "biodegradable") {
        audioFile = "static/audio/green_dustbin.mp3";
    } else if (wasteType === "non-biodegradable") {
        audioFile = "static/audio/blue_dustbin.mp3";
    } else if (wasteType === "chemical") {
        audioFile = "static/audio/black_dustbin.mp3";
    } else {
        return; // Unknown waste type
    }

    const audio = new Audio(audioFile);
    audio.play();
}

// Update detected objects list and play audio
function updateDetectedObjects(data) {
    const detectedObjectsDiv = document.getElementById("detected-objects");
    detectedObjectsDiv.innerHTML = "";

    data.forEach(([object, wasteType]) => {
        const p = document.createElement("p");
        p.textContent = `${object} (${wasteType})`;
        detectedObjectsDiv.appendChild(p);

        // Play audio announcement
        playAudio(wasteType);
    });
}

// Fetch detected objects from the server
function fetchDetectedObjects() {
    fetch("/get_detected_objects")
        .then((response) => response.json())
        .then((data) => updateDetectedObjects(data));
}

// Poll the server for detected objects every 2 seconds
setInterval(fetchDetectedObjects, 2000);