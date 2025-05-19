function deleteCustomer(customerId) {
    if (!confirm("Are you sure you want to delete this customer?")) return; // 🔥 Prevent accidental deletion

    fetch("http://127.0.0.1:5000/delete-customer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id: customerId })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to delete customer. Server responded with an error.");
        }
        return response.json();
    })
    .then(result => {
        if (!result.error) {
            alert("Customer deleted successfully!");
            fetchCustomerList(); // ✅ Refreshes only customer list instead of full page
        } else {
            alert(result.error || "Failed to delete customer. Try again.");
        }
    })
    .catch(error => {
        console.error("Error in deleteCustomer:", error);
        alert("An error occurred while deleting the customer. Please try again.");
    });
}

function submitOrder(event) {
    event.preventDefault();
    const formData = new FormData(event.target);
    const data = Object.fromEntries(formData.entries());
    data.order_details = cart; // Attach cart items

    fetch("http://127.0.0.1:5000/send-order-email", { 
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Server responded with an error");
        }
        return response.json();
    })
    .then(result => {
        console.log("Order response:", result);
        // If no error property, then report success.
        if (!result.error) {
            showSuccessModal(
                "Order Placed Successfully!", 
                "Thank you for your purchase. You will receive an order confirmation email shortly."
            );
        } else {
            alert("Failed to place order. Please try again.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        alert("An error occurred while placing the order.");
    });

    // Clear cart and reset form
    cart = [];
    updateCartCount();
    closeCheckoutModal();
    event.target.reset();
}

function showSuccessModal(title, message) {
    const successModal = document.createElement("div");
    successModal.className = "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50";
    successModal.innerHTML = `
        <div class="bg-white rounded-lg p-6 max-w-sm mx-4">
            <div class="text-center">
                <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <i class="ri-check-line text-3xl text-green-500"></i>
                </div>
                <h3 class="text-xl font-semibold mb-2">${title}</h3>
                <p class="text-gray-600 mb-4">${message}</p>
                <button class="bg-primary text-white px-6 py-2 !rounded-button whitespace-nowrap hover:bg-opacity-90" onclick="this.closest('.fixed').remove()">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(successModal);
}