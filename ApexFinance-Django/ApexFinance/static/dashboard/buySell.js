var Site = function() {
    this.symbol = "MSFT"; // Default symbol
    this.period = "1d";  // Default period (1 month)
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
    console.log("URL Parameter for " + name + ": ", results ? results[1] : null); // Check this
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

        // Update stock info in the page

        that.UpdateStockInfo(data);

		//console.log(context) // USED FOR DEBUGGING
		//console.log("Load Chart GetQuote context ", context);
		console.log("Load Chart GetQuote data ", data);
        // Call the request to load the chart and pass the data context with it.
        that.LoadChart(context);
    });
};

// Function to update stock info in the HTML section
Site.prototype.UpdateStockInfo = function(quote) {

    console.log(quote)
    if(quote.quoteType == "ETF") {
        let currPrice = quote.navPrice || quote.ask || quote.regularMarketPrice || 0;
        console.log("Here I am now")

        // ETF-specific information
        var etfInfoHtml = `
            <p><strong>ETF Name:</strong> ${quote.longName || 'N/A'}</p>
            <p><strong>Symbol:</strong> ${quote.symbol || 'N/A'}</p>
            <p><strong>Category:</strong> ${quote.category || 'N/A'}</p>
            <p><strong>Fund Family:</strong> ${quote.fundFamily || 'N/A'}</p>
            <p><strong>Price:</strong> $${currPrice ? currPrice.toFixed(2) : 'N/A'}</p>
            <p><strong>Currency:</strong> ${quote.currency || 'N/A'}</p>
            <p><strong>Day's Range:</strong> $${quote.dayLow ? quote.dayLow.toFixed(2) : 'N/A'} - $${quote.dayHigh ? quote.dayHigh.toFixed(2) : 'N/A'}</p>
            <p><strong>52 Week High:</strong> $${quote.fiftyTwoWeekHigh ? quote.fiftyTwoWeekHigh.toFixed(2) : 'N/A'}</p>
            <p><strong>52 Week Low:</strong> $${quote.fiftyTwoWeekLow ? quote.fiftyTwoWeekLow.toFixed(2) : 'N/A'}</p>
            <p><strong>5 Year Avg Return:</strong> ${quote.fiveYearAverageReturn ? (quote.fiveYearAverageReturn * 100).toFixed(2) + "%" : 'N/A'}</p>
        `;
        var extraEtfInfoHtml = `
            <p><strong>3 Year Avg Return:</strong> ${quote.threeYearAverageReturn ? (quote.threeYearAverageReturn * 100).toFixed(2) + "%" : 'N/A'}</p>
            <p><strong>Trailing PE:</strong> ${quote.trailingPE ? quote.trailingPE.toFixed(2) : 'N/A'}</p>
            <p><strong>Trailing Annual Dividend Rate:</strong> $${quote.trailingAnnualDividendRate ? quote.trailingAnnualDividendRate.toFixed(2) : 'N/A'}</p>
            <p><strong>Trailing Annual Dividend Yield:</strong> ${quote.trailingAnnualDividendYield ? (quote.trailingAnnualDividendYield * 100).toFixed(2) + "%" : 'N/A'}</p>
            <p><strong>Total Assets:</strong> $${quote.totalAssets ? quote.totalAssets.toLocaleString() : 'N/A'}</p>
            <p><strong>Volume:</strong> ${quote.volume ? quote.volume.toLocaleString() : 'N/A'}</p>
            <p><strong>Exchange:</strong> ${quote.exchange || 'N/A'}</p>
            <p><strong>Fund Inception Date:</strong> ${quote.fundInceptionDate ? new Date(quote.fundInceptionDate * 1000).toLocaleDateString() : 'N/A'}</p>
            <p><strong>Beta (3-Year):</strong> ${quote.beta3Year ? quote.beta3Year.toFixed(2) : 'N/A'}</p>
            <p><strong>Average Daily Volume (10-Day):</strong> ${quote.averageDailyVolume10Day ? quote.averageDailyVolume10Day.toLocaleString() : 'N/A'}</p>

        `;
        // Insert the HTML into the stock info section
        $('#extra_info').html(extraEtfInfoHtml);
        $('#stock_info').html(etfInfoHtml);
        
    } else {
        currPrice = quote.currentPrice || quote.ask || quote.regularMarketPrice || 0;
        var stockInfoHtml = `
            <p><strong>Company Name:</strong> ${quote.shortName || 'N/A'}</p>
            <p><strong>Symbol:</strong> ${quote.symbol || 'N/A'}</p>
            <p><strong>Price:</strong> $${currPrice ? currPrice.toFixed(2) : 'N/A'}</p>
            <p><strong>Market Cap:</strong> $${quote.marketCap ? quote.marketCap.toLocaleString() : 'N/A'}</p>
            <p><strong>Sector:</strong> ${quote.sector || 'N/A'}</p>
            <p><strong>Industry:</strong> ${quote.industry || 'N/A'}</p>
            <p><strong>Previous Close:</strong> $${quote.previousClose ? quote.previousClose.toFixed(2) : 'N/A'}</p>
            <p><strong>Open:</strong> $${quote.open ? quote.open.toFixed(2) : 'N/A'}</p>
            <p><strong>52 Week High:</strong> $${quote.fiftyTwoWeekHigh ? quote.fiftyTwoWeekHigh.toFixed(2) : 'N/A'}</p>
            <p><strong>Currency:</strong> ${quote.currency ? quote.currency : 'N/A'}</p>
            <p><strong>52 Week Change:</strong> ${quote["52WeekChange"] ? (quote["52WeekChange"] * 100).toFixed(2) + "%" : 'N/A'}</p>
        `;
    
        // Extra info HTML
        var extraInfoHtml = `
            <p><strong>52 Week Low:</strong> $${quote.fiftyTwoWeekLow ? quote.fiftyTwoWeekLow.toFixed(2) : 'N/A'}</p>
            <p><strong>Dividend Yield:</strong> ${quote.dividendYield ? (quote.dividendYield * 100).toFixed(2) + "%" : 'N/A'}</p>
            <p><strong>PE Ratio:</strong> ${quote.forwardPE ? quote.forwardPE.toFixed(2) : 'N/A'}</p>
            <p><strong>EPS:</strong> $${quote.forwardEps ? quote.forwardEps.toFixed(2) : 'N/A'}</p>
            <p><strong>Beta:</strong> ${quote.beta ? quote.beta.toFixed(2) : 'N/A'}</p>
            <p><strong>Avg Volume:</strong> ${quote.averageVolume ? quote.averageVolume.toLocaleString() : 'N/A'}</p>
            <p><strong>Day's Range:</strong> $${quote.dayLow ? quote.dayLow.toFixed(2) : 'N/A'} - $${quote.dayHigh ? quote.dayHigh.toFixed(2) : 'N/A'}</p>
            <p><strong>Volume:</strong> ${quote.volume ? quote.volume.toLocaleString() : 'N/A'}</p>
            <p><strong>Float Shares:</strong> ${quote.floatShares ? quote.floatShares.toLocaleString() : 'N/A'}</p>
            <p><strong>Dividend Rate:</strong> ${quote.dividendRate ? '$' + quote.dividendRate.toFixed(2): 'N/A'}</p>
            <p><strong>Earnings Growth:</strong> ${quote.earningsGrowth ? (quote.earningsGrowth * 100).toFixed(2) + "%" : 'N/A'}</p>
        `;
        
        // Insert the HTML into the stock info section
        $('#extra_info').html(extraInfoHtml);
        $('#stock_info').html(stockInfoHtml);
    }

};

Site.prototype.SubmitForm = function() {
    // Get the value from the input field
    console.log($("#symbol").val())
    
    this.symbol = $("#symbol").val();
    this.period = $("#period").val();
    console.log(this.symbol)

    // Redirect to the search page with the query parameter
    window.location.href = "/buySell?symbol=" + encodeURIComponent(this.symbol) + "&period=" + encodeURIComponent(this.period);

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
			min: yMin, // Set minimum value for Y-axis
            max: yMax, // Set maximum value for Y-axis
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
            color: 'red', // Line color
            type: 'area', // Highlight the area below the line
            fillColor: {
                linearGradient: [0, 0, 0, 300], // Vertical gradient
                stops: [
                    [0, 'rgba(255, 0, 0, 0.5)'], // Semi-transparent red at the top
                    [1, 'rgba(255, 0, 0, 0)'] // Transparent at the bottom
                ]
            },
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