document.getElementById('create-account-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const email = document.getElementById('email').value;

    fetch('/create-account/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            // other data
        }),
    })
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => { throw new Error(text); });
        }
        return response.json();
    })
    .then(data => {
        console.log('Success:', data);
        alert(data.message);
    })
    .catch((error) => {
        console.error('Error:', error);
        alert('An error occurred: ' + error.message);
    });
});