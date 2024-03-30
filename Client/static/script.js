document.getElementById('form-container').addEventListener('submit', async function(e) {
    e.preventDefault();
    const formData = new FormData();
    formData.append('csvFile', document.getElementById('csvFile').files[0]);
    formData.append('txttitle', document.getElementById('txttitle').value);
    formData.append('x_lbl', document.getElementById('x_lbl').value);
    formData.append('y_lbl', document.getElementById('y_lbl').value);
    
    const response = await fetch('/plot', {
        method: 'POST',
        body: formData,
    });
    
    const result = await response.text();
    document.getElementById('plotResult').innerHTML = result;
    
});
