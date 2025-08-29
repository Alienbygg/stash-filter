// Fix Want button functionality
function addToWant(sceneTitle, sceneYear) {
    // Show loading state
    const button = event.target;
    const originalText = button.innerHTML;
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    button.disabled = true;
    
    fetch('/api/add-to-whisparr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: sceneTitle,
            year: sceneYear
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.className = button.className.replace('btn-outline-success', 'btn-success');
            setTimeout(() => {
                button.innerHTML = originalText;
                button.disabled = false;
                button.className = button.className.replace('btn-success', 'btn-outline-success');
            }, 2000);
        } else {
            throw new Error(data.error || 'Failed to add to Whisparr');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.innerHTML = '<i class="fas fa-exclamation-triangle"></i> Error';
        button.className = button.className.replace('btn-outline-success', 'btn-danger');
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.className = button.className.replace('btn-danger', 'btn-outline-success');
        }, 2000);
    });
}
