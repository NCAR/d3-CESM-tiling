L.GridLayer.Test = L.GridLayer.extend({
    createTile: function (coords) {
        var tile = document.createElement('div');
        tile.innerHTML = [coords.x, coords.y, coords.z].join(', ');
        tile.style.outline = '1px solid red';

        fetch('/tiles/' + coords.z.toString() + '/' + coords.x.toString() + '/' + coords.y.toString(), {
            method: 'GET',
        })
        .then(response => response.json())
        .then(data => {
            // call a function to process the received dataframe with d3.js and plot it
            console.log(data)
            let coordinateArray = data.array;

            data = JSON.parse(dataframe)

            console.log(data)
            var svg_tile = d3.select(tile)
                    .append("svg")
                    .attr("width", "100%")
                    .attr("height", "100%");
            data = data.data
            data.forEach(element => {
                svg_tile.append("rect")
                            .attr("x", element.x)
                            .attr("y", element.y)
                            .attr("width", 10)
                            .attr("height", 10)
                            .attr("fill", "white");
                })

        })
        .catch(error => {
            console.error('Error:', error);
        });

        return tile;
    }
});

L.gridLayer.test = function(opts) {
    return new L.GridLayer.Test(opts);
};