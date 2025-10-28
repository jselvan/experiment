var socket = io.connect("http://" + document.domain + ":" + location.port);

function sendCommand(action) {
    socket.emit('command', { action: action });
}

socket.on('response', function(data) {
    document.getElementById("response").innerText = data.message;
});

function fetchBehaviour() {
    fetch('/behaviour_summary')
    .then(response=>response.json())
    .then(data => {
        document.getElementById("behaviour_summary").textContent = JSON.stringify(data, null, 2)
    })
}
socket.on('trial_end', function(data) {
    fetchBehaviour()
})
fetchBehaviour()