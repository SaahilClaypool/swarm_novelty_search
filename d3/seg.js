//import * as d3 from "d3";
let seg_csv_data = [];
let seg_min_it = 0
let seg_max_it = 0

let get_it = () => {
    let current_it = Math.floor(current_time * (seg_max_it - seg_min_it) / 5000);
    return current_it;
}

function plot_seg() {
    let margin = {
        top: 20, 
        right: 20,
        bottom: 30,
        left: 50
    }

    let seg_svg = d3.select("#seg");

    let width = +seg_svg.attr("width") - margin.left - margin.right;
    let height = +seg_svg.attr("height") - margin.top - margin.bottom;
    seg_g = seg_svg.append("g").attr("transform", `translate(${margin.left}, ${margin.top})`);


    let x = d3.scaleLinear()
            .rangeRound([0, width]);
    let y = d3.scaleLinear()
        .rangeRound([height, 0]);

    d3.csv(PREFIX + "/bots_clean.csv")
        .then((data) => {
            seg_csv_data = data;
            seg_min_it = d3.min(data, d => Number(d.iteration));
            seg_max_it = d3.max(data, d => Number(d.iteration));
            current_it = get_it();
            x.domain([seg_min_it, seg_max_it]);
            y.domain([
                d3.min(data, d => Math.min(0, d.dist_dev, d.dist_dev1, d.dist_dev2)), 
                d3.max(data, d => Math.max(1, d.dist_dev, d.dist_dev1, d.dist_dev2)), 
            ]);

            seg_g.append("g")
                .attr("transform", `translate(0, ${height})`)
                .call(d3.axisBottom(x))

            seg_g.append("g")
                .call(d3.axisLeft(y))
                .append("text")
                .attr("fill", "#000")
                .attr("transform", "rotate(-90)")
                .attr("y", 6)
                .attr("dy", "0.71em")
                .attr("text-anchor", "end")
                .text("Distance Deviation");

            let total_seg  = d3.line()
                .x((d, _i) => x(d.iteration))
                .y((d, _i) => y(d.dist_dev))
                .curve(d3.curveMonotoneX);
                
            seg_g.append("path")
                .datum(data)
                .attr("class","line")
                .attr("d", total_seg);

            seg_g.selectAll(".dot .distdev")
                .data(data)
                .enter().append("circle")
                    .attr("class", "dot")
                    .attr("class", "distdev")
                    .attr("cx", d => x(d.iteration))
                    .attr("cy", d => y(d.dist_dev))
                    .attr("r", seg_size)

            let seg1  = d3.line()
                .x((d, _i) => x(d.iteration))
                .y((d, _i) => y(d.dist_dev1))
                .curve(d3.curveMonotoneX);
                
            seg_g.append("path")
                .datum(data)
                .attr("class","line")
                .attr("d", seg1);

            seg_g.selectAll(".dot .dev1")
                .data(data)
                .enter().append("circle")
                    .attr("class", "dot")
                    .attr("class", "dev1")
                    .attr("cx", d => x(d.iteration))
                    .attr("cy", d => y(d.dist_dev1))
                    .attr("r", seg_size)

            let seg2  = d3.line()
                .x((d, _i) => x(d.iteration))
                .y((d, _i) => y(d.dist_dev1))
                .curve(d3.curveMonotoneX);
                
            seg_g.append("path")
                .datum(data)
                .attr("class","line")
                .attr("d", seg2);

            seg_g.selectAll(".dot .dev2")
                .data(data)
                .enter().append("circle")
                    .attr("class", "dot")
                    .attr("class", "dev2")
                    .attr("cx", d => x(d.iteration))
                    .attr("cy", d => y(d.dist_dev2))
                    .attr("r", seg_size)


                    
        })
}

function update_size () {
    let dots = seg_g.selectAll("circle");
    dots.transition()
        .duration(10)
        .attr("r", seg_size)
}

function seg_size(d) {
    let min_size = 2; 
    let max_size = 10;
    if (Math.abs(d.iteration - get_it()) > 20) {
        return min_size;
    } else {
        let diff = Math.abs(d.iteration - get_it());
        let percent_off = (diff / (20));
        return Math.max(0, max_size - percent_off * max_size) + min_size;
    }
}

function seg_handle_slider() {
    let slider = document.getElementById("slider");
    current_time = slider.value;
    update_size();
}

document.addEventListener('DOMContentLoaded', () => {
    plot_seg(current_time);
    let slider = document.getElementById("slider");
    console.log(slider)
    slider.addEventListener("input", seg_handle_slider);
})
