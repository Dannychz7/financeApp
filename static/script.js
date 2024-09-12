// Portfolio graph logic
const portfolioCtx = document.getElementById('portfolioGraph')?.getContext('2d');
if (portfolioCtx) {
    let portfolioChart = new Chart(portfolioCtx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
            datasets: [{
                label: 'Portfolio Value',
                data: [10000, 12000, 11000, 13000, 12500],
                borderColor: 'red',
                fill: false
            }]
        },
        options: {
            responsive: true,
            scales: {
                x: { title: { display: true, text: 'Time' } },
                y: { title: { display: true, text: 'Value ($)' } }
            }
        }
    });

    function updateGraph() {
        const timeline = document.getElementById('timeline').value;
        console.log(`Updating graph for timeline: ${timeline}`);
        // Logic for updating graph data based on the timeline
        portfolioChart.update();
    }
}

// Stock price graph logic
const stockCtx = document.getElementById('myChart')?.getContext('2d');
if (stockCtx) {
    const stockData = {
        labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        datasets: [{
            label: 'Stock Price',
            data: [120, 130, 100, 150, 125, 140, 160, 135, 170, 155, 180, 165],
            borderColor: 'red',
            borderWidth: 1,
            fill: false
        }]
    };

    const stockConfig = {
        type: 'line',
        data: stockData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    };

    new Chart(stockCtx, stockConfig);
}

// Stock search logic
function searchStock() {
    const stockSymbol = document.getElementById('stockSymbol').value || 'AAPL'; // Default to AAPL if no input

    fetch(`/stock-data?symbol=${stockSymbol}`)
        .then(response => response.json())
        .then(data => {
            displayStockData(data);
        })
        .catch(error => console.error('Error fetching stock data:', error));
}

function displayStockData(data) {
    const ctx = document.getElementById('quoteResult').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.time,
            datasets: [{
                label: 'Close Price',
                data: data.close,
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
                fill: false
            }]
        },
        options: {
            scales: {
                x: {
                    type: 'time',
                    time: {
                        unit: 'minute'
                    }
                }
            }
        }
    });
}


function buyStock() {
    console.log("Buying stock...");
    alert("Stock purchase initiated!");
}

function sellStock() {
    console.log("Selling stock...");
    alert("Stock sale initiated!");
}

// Password change logic
function changePassword() {
    const currentPassword = document.getElementById('currentPassword').value;
    const newPassword = document.getElementById('newPassword').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    if (newPassword !== confirmPassword) {
        alert("Passwords do not match!");
        return;
    }

    console.log("Changing password...");
    // Placeholder for backend call to change password
    alert("Password change requested!");
}
