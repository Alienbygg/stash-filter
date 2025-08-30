function addToWant(sceneId, sceneTitle) {
    const button = event.target;
    const originalHtml = button.innerHTML;
    
    // Show loading state
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    button.disabled = true;
    
    fetch('/api/add-to-whisparr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        },
        body: JSON.stringify({
            scene_id: sceneId,
            title: sceneTitle
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.className = button.className.replace('btn-outline-success', 'btn-success');
        } else {
            throw new Error(data.error || 'Failed to add to Whisparr');
        }
    })
    .catch(error => {
        console.error('Whisparr error:', error);
        button.innerHTML = '<i class="fas fa-times"></i> Failed';
        button.className = button.className.replace('btn-outline-success', 'btn-danger');
    })
    .finally(() => {
        setTimeout(() => {
            button.innerHTML = originalHtml;
            button.disabled = false;
            button.className = button.className.replace('btn-success btn-danger', 'btn-outline-success');
        }, 2000);
    });
}
