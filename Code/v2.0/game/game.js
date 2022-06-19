const camera_capture_duration = 5; // Time to capture eye direction

const container = document.querySelector('#overlay') // Overlay to show fireworks
const fireworks = new Fireworks(container, { rocketsPoint: 1, particles: 300, explosion: 10, trace: 5 }) // Init firework

// This function returns a random hand (Left or Right)
function getRandomHand() {
    return ["RIGHT", "LEFT"].sort(() => 0.5 - Math.random())[0];
}

// Welcome Message
swal({
    title: "Welcome",
    text: `Start playing by clicking the button below. Then start looking at the camera for ${camera_capture_duration}s`,
    icon: "info",
    button: "Start",
}).then(value => {
    if (!value) {
        location.reload(); // Reload page if user didn't accept the terms 
    }

    const socket = io(settings.SOCKET_SERVER, { transports: ['websocket'] }) // Open Socket (connect to raspberry module that detects eye direction)

    socket.on("connect", () => { // Successfully connected to the raspberry pi
        let current_value = camera_capture_duration;
        $("#title").removeClass("d-none").text(`Pick one ${current_value.toFixed(2)}s`); // Show a counter to user (to look at right or left)

        let timerInterval = setInterval(() => { // Interval to update the counter (with step 0.01 seconds)
            current_value -= 0.01;
            if (current_value <= 0) {
                clearInterval(timerInterval);
                return;
            }
            $("#title").text(`Pick one ${current_value.toFixed(2)}s`);
        }, 10);
    });

    socket.emit("handshake", { duration: camera_capture_duration }) // Handshake with rasberry

    socket.on("result", data => { // When result (eye direction) was received 
        direction = data.direction
        // Based on the hand chosen by the user, update the page
        if (direction === "LEFT") {
            $("#left-check-icon").addClass("active"); console.log("LEFT");
            $("#title").text("You picked left").removeClass("blink");
        } else if (direction == "RIGHT") {
            $("#right-check-icon").addClass("active"); console.log("RIGHT");
            $("#title").text("You picked right").removeClass("blink");
        }

        setTimeout(() => show_result(direction), 2000); // Show result (Win or Lose)
    });
});

// This function shows the result of the game and performs some actions on the page
function show_result(direction) {
    $("#title").addClass('d-none'); 

    randomHand = getRandomHand(); // Get a random hand

    $('.hand').attr("src", "images/open_hand.png"); // show open hands
    $(`.hand[data-hand='${randomHand}']`).attr("src", "images/full_open_hand.png"); // Show the object in the generated hand

    if (direction == randomHand) { // User won the game (guessed currectly)
        fireworks.start() // Start firework
        $("#overlay").removeClass("invisible");

        swal({ // Congrat message and play again button
            title: "Congratulation!",
            text: "You won the game",
            icon: "success",
            button: "Play again",
        }).then(value => {
            location.reload()
        });
    } else { // Game lost message and play again button
        swal({
            title: "Sorry!",
            text: "You lost the game",
            icon: "error",
            button: "Play again",
        }).then(value => {
            location.reload()
        });
    }
}