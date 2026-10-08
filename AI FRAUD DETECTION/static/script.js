document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("transactionForm");
    const amountInput = document.querySelector('input[name="amount"]');

    form.addEventListener("submit", function (event) {
        const amount = Number(amountInput.value);

        if (amountInput.value.trim() === "") {
            alert("Please enter the transaction amount.");
            event.preventDefault();
        } 
        else if (amount <= 0) {
            alert("Amount must be greater than zero.");
            event.preventDefault();
        }
    });
});
