// If unused, consider removing this file.
// Otherwise, add shared utility functions or reusable logic here.
// Example: Centralized API call function

function apiCall(endpoint, method = "GET", body = null) {
    const API_BASE_URL = "http://127.0.0.1:5000";
    return fetch(`${API_BASE_URL}${endpoint}`, {
        method,
        headers: { "Content-Type": "application/json" },
        body: body ? JSON.stringify(body) : null,
    }).then(response => {
        if (!response.ok) {
            throw new Error(`API call failed: ${response.statusText}`);
        }
        return response.json();
    });
}

function formatEmailPayload(data, type) {
    if (type === "client") {
        return `
            <h2>Thank you for your booking, ${data.name}!</h2>
            <p>We have received your request for <strong>${data.serviceType || data.planType || "your order"}</strong>.</p>
            <p>Details:</p>
            <ul>
                <li><strong>Name:</strong> ${data.name}</li>
                <li><strong>Email:</strong> ${data.email}</li>
                <li><strong>Phone:</strong> ${data.phone}</li>
                <li><strong>Address:</strong> ${data.address}</li>
                ${data.date ? `<li><strong>Preferred Date:</strong> ${data.date}</li>` : ""}
                ${data.brand ? `<li><strong>AC Brand:</strong> ${data.brand}</li>` : ""}
                ${data.model ? `<li><strong>AC Model:</strong> ${data.model}</li>` : ""}
            </ul>
            <p>We will contact you shortly to confirm the details.</p>
        `;
    } else if (type === "admin") {
        return `
            <h2>New Booking/Order Received</h2>
            <p>Please find the details below:</p>
            <ul>
                <li><strong>Name:</strong> ${data.name}</li>
                <li><strong>Email:</strong> ${data.email}</li>
                <li><strong>Phone:</strong> ${data.phone}</li>
                <li><strong>Address:</strong> ${data.address}</li>
                ${data.date ? `<li><strong>Preferred Date:</strong> ${data.date}</li>` : ""}
                ${data.brand ? `<li><strong>AC Brand:</strong> ${data.brand}</li>` : ""}
                ${data.model ? `<li><strong>AC Model:</strong> ${data.model}</li>` : ""}
                ${data.serviceType ? `<li><strong>Service Type:</strong> ${data.serviceType}</li>` : ""}
                ${data.planType ? `<li><strong>AMC Plan:</strong> ${data.planType}</li>` : ""}
                ${data.order_details ? `<li><strong>Order Details:</strong> ${JSON.stringify(data.order_details)}</li>` : ""}
            </ul>
            <p>Please take the necessary follow-up actions.</p>
        `;
    }
}
