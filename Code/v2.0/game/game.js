const camera_capture_duration = 5;

const container = document.querySelector('#overlay')
const fireworks = new Fireworks(container, { rocketsPoint: 1, particles: 300, explosion: 10, trace: 5 })

function getRandomHand() {
    return ["RIGHT", "LEFT"].sort(() => 0.5 - Math.random())[0];
}

swal({
    title: "Welcome",
    text: `Start playing by clicking the button below. Then start looking at the camera for ${camera_capture_duration}s`,
    icon: "info",
    button: "Start",
}).then(value => {
    if (!value) {
        location.reload();
    }

    const socket = io("http://192.168.1.102:4343", { transports: ['websocket'] })

    socket.on("connect", () => {
        let current_value = camera_capture_duration;
        $("#title").removeClass("d-none").text(`Pick one ${current_value.toFixed(2)}s`);

        let timerInterval = setInterval(() => {
            current_value -= 0.01;
            if (current_value <= 0) {
                clearInterval(timerInterval);
                return;
            }
            $("#title").text(`Pick one ${current_value.toFixed(2)}s`);
        }, 10);
    });

    socket.emit("handshake", { duration: camera_capture_duration })

    socket.on("result", data => {
        direction = data.direction
        if (direction === "LEFT") {
            $("#left-check-icon").addClass("active"); console.log("LEFT");
            $("#title").text("You picked left").removeClass("blink");
        } else if (direction == "RIGHT") {
            $("#right-check-icon").addClass("active"); console.log("RIGHT");
            $("#title").text("You picked right").removeClass("blink");
        }

        setTimeout(() => show_result(direction), 2000);
    });
});

function show_result(direction) {
    $("#title").addClass('d-none');

    randomHand = getRandomHand();

    $('.hand').attr("src", "images/open_hand.png");
    $(`.hand[data-hand='${randomHand}']`).attr("src", "images/full_open_hand.png");

    if (direction == randomHand) {
        fireworks.start()
        $("#overlay").removeClass("invisible");

        swal({
            title: "Congratulation!",
            text: "You won the game",
            icon: "success",
            button: "Play again",
        }).then(value => {
            location.reload()
        });
    } else {
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