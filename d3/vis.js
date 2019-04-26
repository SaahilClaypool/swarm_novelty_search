//import * as d3 from "d3";
function path() {
    console.log("main")
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

    var x = d3.scaleBand()
            .rangeRound([0, width])
            .padding(0.1);
    let y = d3.scaleLinear()
        .rangeRound([height, 0]);

    d3.tsv("./test.tsv")
        .then((data) => {
            x.domain(data.map((d) => {
                return d.Run;
            }));
            y.domain([0, d3.max(data, (d) => {
                return Number(d.Speed);
            })]);

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
                .text("Speed");

            g.selectAll(".bar")
                .data(data)
                .enter().append("rect")
                    .attr("class", "bar")
                    .attr("x", (d) => {
                        return x(d.Run);
                    })
                    .attr("y", (d) => y(Number(d.Speed)))
                    .attr("width", x.bandwidth())
                    .attr("height", (d) => {
                        val = height - y(Number(d.Speed))
                        return val;
                    });
        });

}
document.addEventListener('DOMContentLoaded', () => {
    console.log("document loaded")
    path();
})

console.log("loaded script")
