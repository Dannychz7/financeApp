var Site = function() {
    this.symbol = "MSFT"; // Default symbol
    this.period = "1mo";  // Default period (1 month)
};

Site.prototype.Init = function() {
    // Check for a stock symbol and update this.symbol accordingly
    this.symbol = this.getURLParameter('symbol') || this.symbol; // Default to "MSFT" if none found
    this.period = this.getURLParameter('period') || this.period; // Default to "1mo" if none found
    
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
};

// Function to get URL parameters
Site.prototype.getURLParameter = function(name) {
    name = name.replace(/[\[]/, '\\[').replace(/[\]]/, '\\]');
    var regex = new RegExp('[\\?&]' + name + '=([^&#]*)');
    var results = regex.exec(window.location.href);
    return results === null ? '' : decodeURIComponent(results[1].replace(/\+/g, ' '));
};

Site.prototype.GetQuote = function() {
    // store the site context.
    var that = this;

    // pull the HTTP Request for the stock quote
    $.ajax({
        url: "/quote?symbol=" + that.symbol + "&period=" + that.period, 
        method: "GET",
        cache: false
    }).done(function(data) {
        console.log("Data received for period:", that.period, data);  // Log to debug

        // set up a data context for just what we need.
        var context = {};
        context.shortName = data.shortName;
        context.symbol = data.symbol;
        context.Price = data.currentPrice || data.ask || data.regularMarketPrice || 0;
		context.period = that.period;     // Add the period to the context

		//console.log(data) // USED FOR DEBUGGING
        if (data.quoteType === "MUTUALFUND" || data.quoteType === "ETF") {
            context.Price = data.previousClose;
        }

		//console.log(context) // USED FOR DEBUGGING
		console.log("Load Chart GetQuote context ", context);
		console.log("Load Chart GetQuote data ", data);
        // Call the request to load the chart and pass the data context with it.
        that.LoadChart(context);
    });
};

Site.prototype.SubmitForm = function() {
    // Get the value from the input field
    this.symbol = $("#symbol").val();
    this.period = $("#period").val();

    // Redirect to the search page with the query parameter
    window.location.href = "/search?symbol=" + encodeURIComponent(this.symbol) + "&period=" + encodeURIComponent(this.period);

    // Prevent default form submission (if this is being used as an event handler)
    return false;
};

Site.prototype.LoadChart = function(quote) {
    var that = this;

    // pull the HTTP Request for the stock history with the selected period
    $.ajax({
        url: "/history?symbol=" + that.symbol + "&period=" + that.period,
        method: "GET",
        cache: false
    }).done(function(data) {
		// console.log("Load Chart Function data ", data);
        that.RenderChart(JSON.parse(data), quote);
    });
};

Site.prototype.RenderChart = function(data, quote) {
    var priceData = [];
    var dates = [];

    var title = quote.shortName + " (" + quote.symbol + ") - " + numeral(quote.Price).format('$0,0.00');

	// Determine the format based on the selected period/interval
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

    // Log the data to check the response, DEBUGGING PURPOSES
    // console.log("Data received:", data);
	// console.log("Here is the intervalFormat", intervalFormat);

	// Calculate min and max for Y-axis scaling
	var yMin = Math.min(...priceData) * 0.95; // 5% below the minimum price
	var yMax = Math.max(...priceData) * 1.05; // 5% above the maximum price

    for (var i in data.Close) {
        var dt = i.slice(0, i.length - 3);  // Timestamp the before 
        var dateString = moment.unix(dt).format(intervalFormat); // Use the correct format
        var close = data.Close[i];
        if (close != null) {
            priceData.push(data.Close[i]);
            dates.push(dateString);
        }
    }

    Highcharts.chart('chart_container', {
        title: {
            text: title
        },
        yAxis: {
            title: {
                text: ''
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
            color: '#85bb65',
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