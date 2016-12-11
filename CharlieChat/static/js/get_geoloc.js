$(document).ready(function() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    }
});

function getLocation() {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(showPosition);
    } else {
        document.getElementById("geo_loc").innerHTML =
        "Geolocation is not supported by this browser.";
    }
}

function showPosition(position) {
    document.getElementById("geo_loc").value =
    position.coords.latitude + "," + position.coords.longitude;
}

function clearLocation() {
  document.getElementById("geo_loc").value = "";
}
