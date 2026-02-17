document.addEventListener("DOMContentLoaded", function () {
    const searchInputs = document.querySelectorAll(".live-search");

    searchInputs.forEach(input => {
        input.addEventListener("keyup", function () {
            const filter = input.value.toLowerCase();
            const table = input.closest(".container").querySelector("table");
            const rows = table.querySelectorAll("tbody tr");
            let visibleCount = 0;

            rows.forEach(row => {
                const cells = Array.from(row.querySelectorAll("td"));
                const rowText = cells.map(td => td.innerText.toLowerCase()).join(" ");

                if (rowText.includes(filter)) {
                    row.style.display = "";
                    visibleCount++;

                    cells.forEach(td => {
                        td.innerHTML = td.innerText; // Reset previous highlights
                        if (filter !== "") {
                            const regex = new RegExp(`(${filter})`, "gi");
                            td.innerHTML = td.innerText.replace(regex, "<span class='highlight'>$1</span>");
                        }
                    });
                } else {
                    row.style.display = "none";
                }
            });

            // Handle "No results found"
            let noMsg = table.querySelector(".no-results");
            if (!noMsg) {
                noMsg = document.createElement("tr");
                noMsg.className = "no-results";
                noMsg.innerHTML = `<td colspan="${table.querySelectorAll('th').length}" style="text-align:center;">No results found</td>`;
                table.querySelector("tbody").appendChild(noMsg);
            }
            noMsg.style.display = visibleCount === 0 ? "" : "none";
        });
    });
});

function confirmDelete() {
    return confirm("Are you sure you want to delete this book?");
}
