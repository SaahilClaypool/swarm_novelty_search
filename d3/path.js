//import * as d3 from "d3";
let current_time = 1;
let circles = [];
let csv_data = [];
let min_it = 0
let max_it = 0
let current_it = Math.floor(current_time * (max_it - min_it) / 2000);
function path(current_time) {
    let margin = {
        top: 20, 
        right: 20,
        bottom: 30,
        left: 50
    }

    let svg = d3.select("#vis");

    let width = +svg.attr("width") - margin.left - margin.right;
    let height = +svg.attr("height") - margin.top - margin.bottom;
    g = svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);


    var x = d3.scaleLinear()
            .rangeRound([0, width]);
    let y = d3.scaleLinear()
        .rangeRound([height, 0]);

    d3.csv("./bots_test.csv")
        .then((data) => {
            csv_data = data;
            min_it = d3.min(data, d => Number(d.iteration));
            max_it = d3.max(data, d => Number(d.iteration));
            current_it = Math.floor(current_time * (max_it - min_it) / 2000);
            x.domain([-2, 2]);
            y.domain([-2, 2]);

            g.append("g")
                .attr("transform", `translate(0, ${height})`)
                .call(d3.axisBottom(x))

            g.append("g")
                .call(d3.axisLeft(y))
                .append("text")
                .attr("fill", "#000")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", "0.71em")
                .attr("text-anchor", "end")
                .text("");

            let circles = g.selectAll(".bar");
            circles
                .data(data)
                .enter().append("circle")
                    .attr("class", "bar")
                    .attr("cx", (d) => {
                        let val = x(Number(d.px))
                        return val;
                    })
                    .attr("cy", d => {
                        let val = y(Number(d.py));
                        return val;
                    })
                    .attr("fill", color)
                    .attr("r", circ_size)
        });

}

function circ_size(d) {
    //op(d.iteration, min_it, max_it, current_it)
    let max_size = 10;
    let min_size  = 3;
    let diff = Math.abs(current_it - d.iteration);
    let percent_off = diff / (max_it - min_it) * 100;
    if (diff < 50 && current_it + 10 > d.iteration) {
        return Math.max(0, max_size - max_size * percent_off) + min_size;
    }
    else {
        return min_size;
    }
}

function color(d) {
    let base_hue = 10;
    if (d.id % 2 == 0) {
        base_hue = 235;
    }
    let opacity = op(d.iteration, min_it, max_it, current_it);
    return `hsl(${base_hue}, 100%, 50%, ${opacity}%)`;
}

function update_o() {
    current_it = Math.floor(current_time * (max_it - min_it) / 2000);
    console.log("current it", current_it, "current time", current_time)
    let svg = d3.select("#vis");
    circles = svg.select("g").selectAll("circle");
    circles.transition()
        .duration(50)
        .attr("fill", color)
        .attr("r", circ_size)
}

/**
 * want a sort of exponential decay from the current iterations
 */
function op(it, min, max, time) {
    let max_o = 70;
    let min_o  = 7;
    let diff = Math.abs(it - time);
    let percent_off = diff / (max - min) * 100;
    if (diff < 50 && it < time + 15) {
        return Math.max(0, max_o - max_o * percent_off) + min_o;
    }
    else {
        return min_o;
    }
}

function handle_slider() {
    console.log('handling sider')
    let slider = document.getElementById("slider");
    current_time = slider.value;
    update_o();
}

document.addEventListener('DOMContentLoaded', () => {
    console.log("document loaded")
    path(current_time);
    let slider = document.getElementById("slider");
    slider.addEventListener("input", handle_slider);
})



console.log("loaded script")
