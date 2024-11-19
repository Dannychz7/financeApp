var Site = function() {
    this.symbol = "MSFT"; // Default symbol
    this.period = "1d";  // Default period (1 day)
};

Site.prototype.Init = function() {
    // Check for a stock symbol and update this.symbol accordingly
    this.symbol = this.getURLParameter('symbol') || this.symbol; // Default to "MSFT" if none found
    this.period = this.getURLParameter('period') || this.period; // Default to "1d" if none found
    
    $("#symbol").val(this.symbol); // Populate the input field if there's a symbol
    $("#period").val(this.period); // Set the dropdown to the correct period

    if (this.symbol) {
        this.GetQuote(); // Get quote for the symbol from the URL
    }

    // Clear the input field on click
    $("#symbol").on("click", function() {
        $(this).val("");
    });

    // Re-fetch data when the user changes the period
    $("#period").on("change", () => {
        this.period = $("#period").val();
        this.GetQuote();
    });

    // Bind the SubmitForm method to the submit button
    $("#submit-button").on("click", () => {
        this.SubmitForm();  // Handle form submission
    });
};

// Function to handle the form submission
Site.prototype.SubmitForm = function() {
    // Get the symbol and period from the input fields
    this.symbol = $("#symbol").val();
    this.period = $("#period").val();

    // Redirect the user to the new URL with the selected symbol and period
    window.location.href = "/search?symbol=" + encodeURIComponent(this.symbol) + "&period=" + encodeURIComponent(this.period);
    return false; // Prevent form from being submitted in the traditional way
};

// Function to get URL parameters
Site.prototype.getURLParameter = function(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(window.location.href);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

Site.prototype.GetQuote = function() {
    var that = this;

    $.ajax({
        url: "/quote?symbol=" + that.symbol + "&period=" + that.period, 
        method: "GET",
        cache: false
    }).done(function(data) {
        console.log("Data received for period:", that.period, data);

        var context = {};
        context.shortName = data.shortName;
        context.symbol = data.symbol;
        context.Price = data.currentPrice || data.ask || data.regularMarketPrice || 0;
        context.period = that.period;

        if (data.quoteType === "MUTUALFUND" || data.quoteType === "ETF") {
            context.Price = data.previousClose;
        }

        // Add extra data for related stocks/ETFs
        that.LoadRelatedAssets(context);

        // Call the request to load the main chart and pass the data context with it.
        that.LoadChart(context);
    });
};

Site.prototype.LoadRelatedAssets = function(quote) {
    var that = this;

    // Log the symbol to verify the input to the related assets fetch
    console.log("Fetching related assets for symbol:", quote.symbol);

    // Determine if the symbol is a stock or ETF and fetch related assets accordingly
    var relatedAssetsUrl = "/extra-charts?symbol=" + quote.symbol;

    $.ajax({
        url: relatedAssetsUrl,
        method: "GET",
        cache: false
    })
    .done(function(data) {
        console.log("Related assets data received:", data);
        console.log("Data type:", Array.isArray(data) ? "Array" : typeof data);

        // Ensure data is an array or object with expected structure
        if (Array.isArray(data)) {
            console.log("Data is an array. Iterating over related assets...");
            data.forEach((item, index) => {
                console.log(`Related asset ${index + 1}:`, item);

                // Dynamically load charts for each related asset if applicable
                if (index === 0 && item) {
                    that.LoadExtraChart(1, item);
                } else if (index === 1 && item) {
                    that.LoadExtraChart(2, item);
                } else if (index === 2 && item) {
                    that.LoadExtraChart(3, item);
                }
            });
        } else if (typeof data === "object" && data !== null) {
            console.log("Data is an object. Attempting to load related assets...");
            if (data.related1) {
                console.log("Loading chart for related1:", data.related1);
                that.LoadExtraChart(1, data.related1);
            }
            if (data.related2) {
                console.log("Loading chart for related2:", data.related2);
                that.LoadExtraChart(2, data.related2);
            }
            if (data.related3) {
                console.log("Loading chart for related3:", data.related3);
                that.LoadExtraChart(3, data.related3);
            }
        } else {
            console.error("Unexpected data structure received:", data);
        }
    })
    .fail(function(jqXHR, textStatus, errorThrown) {
        console.error("Failed to fetch related assets. Status:", textStatus, "Error:", errorThrown);
    });
};

Site.prototype.LoadExtraChart = function(containerId, relatedAsset) {
    var that = this;
    console.log("Loading extra chart for container:", containerId, "with data:", relatedAsset);

    // Parse the Close field, which is a stringified JSON object
    var closeData = JSON.parse(relatedAsset.Close);
    var dates = [];
    var priceData = [];

    // for (var timestamp in closeData.Open) {
    //     // Convert the timestamp to a human-readable time in "HH:mm" format
    //     var date = new Date(parseInt(timestamp) * 1000); // Multiply by 1000 to convert UNIX timestamp to milliseconds
    //     var formattedTime = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false }); // Use 24-hour format
    //     dates.push(formattedTime); // Push the formatted time to dates array
    //     priceData.push(closeData.Open[timestamp]); // Push the price to priceData array
    // }
    for (var timestamp in closeData.Open) {
        // Log the raw timestamp for debugging
        console.log("Raw timestamp:", timestamp);
    
        // Convert timestamp to milliseconds if necessary
        var date = new Date(parseInt(timestamp)); 
    
        // Adjust to Eastern Time (UTC-5), if required
        // var timezoneOffset = -5 * 60; // Eastern Time offset in minutes
        var adjustedDate = new Date(date.getTime() + 1 * 60 * 1000);
    
        // Format the adjusted time
        var formattedTime = adjustedDate.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: false });
    
        // Log the formatted time for debugging
        console.log("Formatted time:", formattedTime);
    
        dates.push(formattedTime); // Push formatted time to dates array
        priceData.push(closeData.Open[timestamp]); // Push price data
    }

    console.log("Prepared chart data for container:", containerId, { dates: dates, priceData: priceData });

    // Ensure the data is valid before rendering the chart
    if (priceData.length > 0 && dates.length > 0) {
        Highcharts.chart('extra_chart_container_' + containerId, {
            title: { text: relatedAsset.shortName + " (" + relatedAsset.symbol + ") - $" + relatedAsset.Price },
            yAxis: {
                title: { text: '' },
                min: Math.min(...priceData),
                max: Math.max(...priceData),
                labels: {
                    formatter: function () {
                        return this.value.toFixed(2);
                    }
                }
            },
            xAxis: { categories: dates },
            series: [{
                type: 'area',
                color: '#00FF00',
                name: 'Price',
                data: priceData
            }],
            responsive: {
                rules: [{
                    condition: { maxWidth: 640 },
                    chartOptions: {
                        legend: {
                            layout: 'horizontal',
                            align: 'center',
                            verticalAlign: 'bottom'
                        }
                    }
                }]
            }
        });
    } else {
        console.error("Invalid data for chart rendering: Dates or Price data is empty.");
    }
};


Site.prototype.LoadChart = function(quote) {
    var that = this;

    $.ajax({
        url: "/history?symbol=" + that.symbol + "&period=" + that.period,
        method: "GET",
        cache: false
    }).done(function(data) {
        that.RenderChart(JSON.parse(data), quote);
    });
};

Site.prototype.RenderChart = function(data, quote) {
    var priceData = [];
    var dates = [];

    var title = quote.shortName + " (" + quote.symbol + ") - " + numeral(quote.Price).format('$0,0.00');

    var intervalFormat;
    if (this.period === "1d") {
        intervalFormat = "HH:mm"; // Every min for 1 day
    } else if (this.period === "5d") {
        intervalFormat = "MM/DD HH:mm"; // Every 30 min for 5 days
    } else if (this.period === "1mo" || this.period === "3mo") {
        intervalFormat = "MM/DD"; // Every day for 1 month and 3 months
    } else if (this.period === "1y" || this.period === "ytd" || this.period === "2y") {
        intervalFormat = "MM/DD"; // Every week for 1 year, ytd, and 2 years
    } else {
        intervalFormat = "MM/YY"; // Default for longer periods, i.e monthly
    }

    for (var i in data.Close) {
        var dt = i.slice(0, i.length - 3);  // Timestamp the before 
        var dateString = moment.unix(dt).format(intervalFormat); // Use the correct format
        var close = data.Close[i];
        if (close != null) {
            priceData.push(data.Close[i]);
            dates.push(dateString);
        }
    }

    // Calculate min and max for Y-axis scaling
    var yMin = Math.min(...priceData);
    var yMax = Math.max(...priceData);

    Highcharts.chart('chart_container', {
        title: {
            text: title
        },
        yAxis: {
            title: {
                text: ''
            },
            min: yMin, 
            max: yMax, 
            labels: {
                formatter: function () {
                    return this.value.toFixed(2); // Format labels to 2 decimal places
                }
            }
        },
        xAxis: {
            categories: dates,
        },
        legend: {
            layout: 'vertical',
            align: 'right',
            verticalAlign: 'middle'
        },
        plotOptions: {
            series: {
                label: {
                    connectorAllowed: false
                }
            },
            area: {}
        },
        series: [{
            type: 'area',
            color: '#FF0000',
            name: 'Price',
            data: priceData
        }],
        responsive: {
            rules: [{
                condition: {
                    maxWidth: 640
                },
                chartOptions: {
                    legend: {
                        layout: 'horizontal',
                        align: 'center',
                        verticalAlign: 'bottom'
                    }
                }
            }]
        }
    });
};

var site = new Site();

$(document).ready(() => {
    site.Init(); // Initialize on page load
});
