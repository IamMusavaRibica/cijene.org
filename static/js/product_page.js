const quantities = new Set();
const rows = [];
const filters = {quantity: new Set()};

// parse the offers table, extract all rows and relevant data
document.querySelectorAll('#offers tbody tr').forEach(row => {
    if (row.querySelector('th'))
        return;

    let getTextContent = selector => row.querySelector(selector)?.textContent.trim() || '';
    const name = getTextContent('td.name .name-flex span');
    const store = getTextContent('td.store span.only-wide');
    const quantity = getTextContent('td.quantity');
    const price = getTextContent('td.price span.price');
    const unitPrice = getTextContent('td.unit-price span.price');

    quantities.add(quantity);
    // console.log(`Name: ${name}, Store: ${store}, Quantity: ${quantity}, Price: ${price}, Unit Price: ${unitPrice}`);
    rows.push({ name, store, quantity, price, unitPrice, handle: row });
});

// dynamically create the checkboxes for filtering quantities
const fq = document.querySelector('#filter-quantity');
new Array(...quantities).sort().forEach(q => {
    fq.innerHTML += `<span><label> <input type="checkbox" name="quantity" value="${q}">${q}</label></span>`
});

// assign event listeners to the checkboxes
fq.querySelectorAll('input[name="quantity"]').forEach(checkbox => {
    checkbox.addEventListener('change', e => {
        console.log(e.target);
        console.log(e.target.checked);
        console.log(e.target.value);
        if (e.target.checked)
            filters.quantity.add(e.target.value);
        else
            filters.quantity.delete(e.target.value);

        updateVisibleRows();
    });
});

// show the filtering options to the user
document.querySelector('#filters').style.removeProperty('display');


function updateVisibleRows() {
    rows.forEach(r => {
        if (!filters.quantity.size || filters.quantity.has(r.quantity))
            r.handle.style.removeProperty('display');
        else
            r.handle.style.setProperty('display', 'none');
    });
    // document.querySelector('#offers tbody').classList.toggle('filtered', filters.quantity.size > 0);
    console.log('Filters applied:', filters);
}