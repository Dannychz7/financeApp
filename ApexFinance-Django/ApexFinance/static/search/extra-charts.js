// // Function to load additional charts based on the stock symbol
// function loadExtraCharts(symbol) {
//     console.log("Loading extra charts for symbol:", symbol);

//     $.ajax({
//         url: "/extra-charts?symbol=" + symbol, 
//         method: "GET",
//         cache: false
//     }).done(function(data) {
//         console.log("Received data for extra charts:", data);

//         // Check if data contains multiple stocks and render charts
//         if (data && Array.isArray(data) && data.length > 0) {
//             data.forEach((item, index) => {
//                 RenderAdditionalChart(item, symbol, index);
//             });
//         } else {
//             console.error('Invalid or empty data received for extra charts.');
//         }
//     }).fail(function() {
//         console.error('Failed to fetch extra chart data.');
//     });
// }

// // Function to render each additional chart
// function RenderAdditionalChart(data, symbol, index) {
//     const priceData = [];
//     const dates = [];
//     const containerId = `extra_chart_container_${index + 1}`; // This will target your existing containers

//     // Ensure the container exists in the DOM
//     const container = document.getElementById(containerId);
//     if (!container) {
//         console.error(`Container with ID ${containerId} not found.`);
//         return;
//     }

//     // Ensure the index is within range of available containers (0-2 for 3 containers)
//     if (index < 3) {
//         // Handle date and price data
//         for (const timestamp in data.Close) {
//             console.log("Raw timestamp:", timestamp);
//             // Convert the timestamp to the correct format
//             const dateString = moment.unix(timestamp).format("HH:mm");  // Adjust format if needed
//             const close = data.Close[timestamp];
//             if (close != null) {
//                 priceData.push(close);
//                 dates.push(dateString);
//             }
//         }

//         // Log price and date data for debugging
//         console.log("Raw timestamp:", timestamp);
//         console.log(`Chart ${index + 1}: Dates - `, dates);
//         console.log(`Chart ${index + 1}: Price Data - `, priceData);

//         // Ensure Highcharts is loaded and chart can be rendered
//         if (typeof Highcharts !== 'undefined') {
//             // Render chart using Highcharts
//             Highcharts.chart(containerId, {
//                 chart: {
//                     type: 'line'  // You can change this to 'area' if you want an area chart
//                 },
//                 title: {
//                     text: `${symbol} - Additional Chart ${index + 1}`
//                 },
//                 xAxis: {
//                     categories: dates,
//                     title: {
//                         text: 'Time'
//                     }
//                 },
//                 yAxis: {
//                     title: {
//                         text: 'Price (USD)'
//                     },
//                     min: Math.min(...priceData) - 5,  // Adding a margin to the minimum value
//                     max: Math.max(...priceData) + 5   // Adding a margin to the maximum value
//                 },
//                 tooltip: {
//                     pointFormat: '{point.x:%H:%M}: <b>${point.y}</b>',
//                     shared: true,
//                 },
//                 series: [{
//                     name: 'Price',
//                     data: priceData,
//                     color: '#007bff',  // Customize line color
//                     marker: {
//                         enabled: true,  // Enable markers for each data point
//                         symbol: 'circle',
//                         radius: 3
//                     }
//                 }],
//                 responsive: {
//                     rules: [{
//                         condition: {
//                             maxWidth: 600
//                         },
//                         chartOptions: {
//                             legend: {
//                                 layout: 'horizontal',
//                                 align: 'center',
//                                 verticalAlign: 'bottom'
//                             },
//                             xAxis: {
//                                 labels: {
//                                     rotation: -45
//                                 }
//                             }
//                         }
//                     }]
//                 }
//             });
//         } else {
//             console.error('Highcharts is not loaded or not available.');
//         }
//     } else {
//         console.error(`No container found for extra chart ${index + 1}.`);
//     }
// }
