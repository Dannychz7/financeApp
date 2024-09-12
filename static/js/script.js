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
const stockCtx = document.getElementById('quoteResultCanvas')?.getContext('2d');
if (stockCtx) {
    // Fetch the stock data when the page loads
    fetchStockData();

    function fetchStockData() {
        const stockSymbol = new URLSearchParams(window.location.search).get('stockSymbol') || 'AAPL';
        
        fetch(`/api/stock-data?symbol=${stockSymbol}`)
            .then(response => response.json())
            .then(data => {
                displayStockData(data);
            })
            .catch(error => console.error('Error fetching stock data:', error));
    }

    function displayStockData(data) {
        if (data.length === 0) {
            console.log('No data available for the selected stock symbol.');
            return;
        }

        const labels = data.map(entry => new Date(entry.Date).toLocaleDateString());
        const prices = data.map(entry => entry.Close);

        new Chart(stockCtx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: `Stock Price for ${stockSymbol}`,
                    data: prices,
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 1,
                    fill: false
                }]
            },
            options: {
                scales: {
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        },
                        type: 'time',
                        time: {
                            unit: 'day'
                        }
                    },
                    y: {
                        title: {
                            display: true,
                            text: 'Price ($)'
                        },
                        beginAtZero: false
                    }
                }
            }
        });
    }
}

// Stock search logic
function searchStock() {
    const stockSymbol = document.getElementById('stockSymbol').value || 'AAPL'; // Default to AAPL if no input

    window.location.href = `/search?stockSymbol=${stockSymbol}`;
}

// Functionality for Buy/Sell buttons
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
