var RUNNING_ANIMATION = false;


function start_timer() {
    if (!RUNNING_ANIMATION) {
        RUNNING_ANIMATION = true; 
        let animation_time = 5000; 
        let timer_steps = 5000;
        let tick_len = animation_time / timer_steps / 1000;
        console.log("starting timer with time of: ", tick_len);
        let slider = document.getElementById("slider");
        let step_len = 35;
        window.setTimeout(() => next_iteration(tick_len, Number(slider.value), step_len), tick_len);
    } else {
        RUNNING_ANIMATION = false;
    }
}

function next_iteration(timeout_len, current_it, step_len) {
    let next = (current_it + step_len) % 5000;
    let slider = document.getElementById("slider");
    console.log(`slider value is`, current_it);
    slider.value = current_it; 
    slider.dispatchEvent(new Event("input"));
    if (RUNNING_ANIMATION) {
        let next_call = () => next_iteration(timeout_len, next, step_len);
        window.setTimeout(next_call, timeout_len);
    }
}

function setup() {
    let button = document.createElement("button");
    button.textContent = "Toggle Animation";
    button.onclick = start_timer;
    let slidercont = document.getElementById("slidercontainer");
    console.log("button", button)
    console.log("slidercont", slidercont)
    slidercont.insertAdjacentElement("afterend", button);
}


document.addEventListener('DOMContentLoaded', setup);
