const apiBase = "";

function formatCurrency(value) {
    return `$${value.toFixed(2)}`;
}

async function loadExpenses() {
    const response = await fetch(`${apiBase}/get-expenses`);
    const expenses = await response.json();
    renderExpenses(expenses);
    refreshAnalytics();
    refreshForecast();
}

function renderExpenses(expenses) {
    const tbody = document.querySelector("#expenses-table tbody");
    tbody.innerHTML = "";
    expenses.forEach(exp => {
        const row = document.createElement("tr");
        row.innerHTML = `
            <td>${exp.id}</td>
            <td>${exp.description}</td>
            <td>${exp.category}</td>
            <td>${formatCurrency(exp.amount)}</td>
            <td>${exp.date}</td>
            <td>
                <button class="secondary" onclick="editExpense(${exp.id})">Edit</button>
                <button class="secondary" onclick="deleteExpense(${exp.id})">Delete</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

async function submitExpense(event) {
    event.preventDefault();
    const id = document.querySelector("#expense-id").value;
    const payload = {
        description: document.querySelector("#description").value,
        category: document.querySelector("#category").value,
        amount: parseFloat(document.querySelector("#amount").value),
        date: document.querySelector("#date").value,
    };
    if (!payload.description || !payload.category || !payload.date) {
        return;
    }
    const url = id ? `${apiBase}/update-expense` : `${apiBase}/add-expense`;
    const body = id ? { id: Number(id), ...payload } : payload;
    const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    });
    if (response.ok) {
        clearForm();
        loadExpenses();
    } else {
        console.error("Expense request failed", await response.text());
    }
}

function clearForm() {
    document.querySelector("#expense-id").value = "";
    document.querySelector("#description").value = "";
    document.querySelector("#category").value = "";
    document.querySelector("#amount").value = "";
    document.querySelector("#date").value = "";
}

async function editExpense(id) {
    const response = await fetch(`${apiBase}/get-expenses`);
    const expenses = await response.json();
    const expense = expenses.find(item => item.id === id);
    if (!expense) return;
    document.querySelector("#expense-id").value = expense.id;
    document.querySelector("#description").value = expense.description;
    document.querySelector("#category").value = expense.category;
    document.querySelector("#amount").value = expense.amount;
    document.querySelector("#date").value = expense.date;
}

async function deleteExpense(id) {
    const response = await fetch(`${apiBase}/delete-expense`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ id }),
    });
    if (response.ok) {
        loadExpenses();
    } else {
        console.error("Delete failed", await response.text());
    }
}

async function refreshAnalytics() {
    const response = await fetch(`${apiBase}/analytics`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ period: "monthly" }),
    });
    const data = await response.json();
    renderAnalytics(data);
}

async function refreshForecast() {
    const response = await fetch(`${apiBase}/predict`);
    const data = await response.json();
    renderForecast(data);
}

function renderAnalytics(data) {
    const summary = document.querySelector("#analytics-summary");
    summary.innerHTML = "";
    const categories = Object.keys(data.category_summary || {});
    if (!categories.length) {
        summary.innerHTML = "<p>No analytics available yet.</p>";
    } else {
        categories.forEach(category => {
            const values = data.category_summary[category];
            const item = document.createElement("div");
            item.className = "forecast-card";
            item.innerHTML = `<strong>${category}</strong>: ${formatCurrency(values.reduce((sum, item) => sum + item.total, 0))}`;
            summary.appendChild(item);
        });
    }
    const monthlyTrend = data.monthly_trend || [];
    drawLineChart(document.querySelector("#trend-chart"), monthlyTrend.map(row => row.period), monthlyTrend.map(row => row.total), "Monthly Total");
    const categoryTrends = data.category_trends || {};
    const latest = [];
    Object.keys(categoryTrends).forEach(category => {
        const list = categoryTrends[category];
        if (list.length) {
            latest.push({ category, total: list[list.length - 1].total });
        }
    });
    drawBarChart(document.querySelector("#category-chart"), latest.map(item => item.category), latest.map(item => item.total), "Category Spend");
}

function renderForecast(data) {
    const card = document.querySelector("#forecast-card");
    card.innerHTML = `
        <div class="forecast-card">
            <strong>Next period:</strong> ${data.next_period}<br />
            <strong>Forecast:</strong> ${formatCurrency(data.forecast)}
        </div>
    `;
}

function drawBarChart(canvas, labels, values, title) {
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#111827";
    ctx.font = "18px Inter";
    ctx.fillText(title, 14, 24);
    if (!labels.length) {
        ctx.fillStyle = "#6b7280";
        ctx.font = "16px Inter";
        ctx.fillText("No data available.", 14, 60);
        return;
    }
    const padding = 50;
    const barWidth = Math.max(20, (width - padding * 2) / labels.length * 0.7);
    const maxValue = Math.max(...values, 1);
    labels.forEach((label, index) => {
        const barHeight = (values[index] / maxValue) * (height - padding * 2);
        const x = padding + index * ((width - padding * 2) / labels.length) + (barWidth * 0.15);
        const y = height - padding - barHeight;
        ctx.fillStyle = "#2563eb";
        ctx.fillRect(x, y, barWidth, barHeight);
        ctx.fillStyle = "#374151";
        ctx.font = "12px Inter";
        ctx.fillText(label, x, height - 16);
    });
}

function drawLineChart(canvas, labels, values, title) {
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = "#111827";
    ctx.font = "18px Inter";
    ctx.fillText(title, 14, 24);
    if (!labels.length) {
        ctx.fillStyle = "#6b7280";
        ctx.font = "16px Inter";
        ctx.fillText("No data available.", 14, 60);
        return;
    }
    const padding = 50;
    const maxValue = Math.max(...values, 1);
    const minValue = Math.min(...values, 0);
    const range = maxValue - minValue || 1;
    ctx.beginPath();
    labels.forEach((label, index) => {
        const x = padding + (index / Math.max(1, labels.length - 1)) * (width - padding * 2);
        const y = height - padding - ((values[index] - minValue) / range) * (height - padding * 2);
        if (index === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
        ctx.fillStyle = "#2563eb";
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fill();
    });
    ctx.strokeStyle = "#2563eb";
    ctx.lineWidth = 3;
    ctx.stroke();
    ctx.fillStyle = "#374151";
    ctx.font = "12px Inter";
    labels.forEach((label, index) => {
        const x = padding + (index / Math.max(1, labels.length - 1)) * (width - padding * 2);
        ctx.fillText(label, x - 18, height - 18);
    });
}

function appendChat(message, sender) {
    const box = document.querySelector("#chat-box");
    const item = document.createElement("div");
    item.className = `chat-message ${sender}`;
    item.innerText = message;
    box.appendChild(item);
    box.scrollTop = box.scrollHeight;
}

async function sendChat(event) {
    event.preventDefault();
    const input = document.querySelector("#chat-input");
    const message = input.value.trim();
    if (!message) return;
    appendChat(message, "user");
    input.value = "";
    const response = await fetch(`${apiBase}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: message }),
    });
    const data = await response.json();
    appendChat(data.answer || "Sorry, could not process the question.", "assistant");
}

document.addEventListener("DOMContentLoaded", () => {
    document.querySelector("#expense-form").addEventListener("submit", submitExpense);
    document.querySelector("#clear-button").addEventListener("click", clearForm);
    document.querySelector("#refresh-expenses").addEventListener("click", loadExpenses);
    document.querySelector("#chat-form").addEventListener("submit", sendChat);
    loadExpenses();
});
