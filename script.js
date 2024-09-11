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
function searchStock(event) {
    event.preventDefault(); // Prevent the default form submission
    const stockSymbol = document.getElementById('stockSymbol').value;
    console.log(`Searching for stock: ${stockSymbol}`);
    // Placeholder for API call
    document.getElementById('quoteResult').innerHTML = `Stock Price for ${stockSymbol}: $100`;
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
