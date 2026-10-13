document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("transactionForm");

    if (!form) {
        return;
    }

    const amountInput = form.querySelector('input[name="amount"]');

    if (!amountInput) {
        return;
    }

    form.addEventListener("submit", function (event) {
        const amount = Number(amountInput.value);

        if (amountInput.value.trim() === "") {
            alert("Please enter the transaction amount.");
            event.preventDefault();
        } else if (!Number.isFinite(amount) || amount <= 0) {
            alert("Amount must be greater than zero.");
            event.preventDefault();
        }
    });
});
