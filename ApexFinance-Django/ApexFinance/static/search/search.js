var Site = function() {
    this.symbol = "MSFT"; // Default symbol
};

Site.prototype.Init = function() {
    // Check for a stock symbol in the URL and update this.symbol accordingly
    this.symbol = this.getURLParameter('symbol') || this.symbol; // Default to "MSFT" if none found
    $("#symbol").val(this.symbol); // Populate the input field if there's a symbol
    
    if (this.symbol) {
        this.GetQuote(); // Get quote for the symbol from the URL
    }

    // Clear the input field on click
    $("#symbol").on("click", function() {
        $(this).val("");
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

    // pull the HTTP Request
    $.ajax({
        url: "/quote?symbol=" + that.symbol,
        method: "GET",
        cache: false
    }).done(function(data) {
        // set up a data context for just what we need.
        var context = {};
        context.shortName = data.shortName;
        context.symbol = data.symbol;
        context.price = data.ask;

        if (data.quoteType === "MUTUALFUND") {
            context.price = data.previousClose;
        }

        // call the request to load the chart and pass the data context with it.
        that.LoadChart(context);
    });
};

Site.prototype.SubmitForm = function() {
    // Get the value from the input field
    this.symbol = $("#symbol").val();

    // Redirect to the search page with the query parameter
    window.location.href = "/search?symbol=" + encodeURIComponent(this.symbol);

    // Prevent default form submission (if this is being used as an event handler)
    return false;
};

Site.prototype.LoadChart = function(quote) {
    var that = this;
    $.ajax({
        url: "/history?symbol=" + that.symbol,
        method: "GET",
        cache: false
    }).done(function(data) {
        that.RenderChart(JSON.parse(data), quote);
    });
};

Site.prototype.RenderChart = function(data, quote) {
    var priceData = [];
    var dates = [];

    var title = quote.shortName + " (" + quote.symbol + ") - " + numeral(quote.price).format('$0,0.00');

    for (var i in data.Close) {
        var dt = i.slice(0, i.length - 3);
        var dateString = moment.unix(dt).format("MM/YY");
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