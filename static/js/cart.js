document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to quantity buttons for increasing the quantity
    document.querySelectorAll('.quantity-button-plus').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default form submission
            const productId = this.getAttribute('data-product-id');

            fetch(`/increase_quantity/${productId}`, {
                method: 'POST'
            }).then(response => {
                if (response.ok) {
                    location.reload(); // Reload the cart to see the updated quantities
                } else {
                    console.error('Failed to increase quantity:', response.statusText);
                    alert('Error increasing quantity. Please try again.');
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    });

    // Add event listeners to quantity buttons for decreasing the quantity
    document.querySelectorAll('.quantity-button-minus').forEach(button => {
        button.addEventListener('click', function(event) {
            event.preventDefault(); // Prevent the default form submission
            const productId = this.getAttribute('data-product-id');

            fetch(`/decrease_quantity/${productId}`, {
                method: 'POST'
            }).then(response => {
                if (response.ok) {
                    location.reload(); // Reload the cart to see the updated quantities
                } else {
                    console.error('Failed to decrease quantity:', response.statusText);
                    alert('Error decreasing quantity. Please try again.');
                }
            }).catch(error => {
                console.error('Error:', error);
            });
        });
    });
});