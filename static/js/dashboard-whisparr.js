function addSceneToWant(sceneTitle, sceneId) {
    const button = event.target;
    const originalText = button.innerHTML;
    
    button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
    button.disabled = true;
    
    fetch('/api/add-scene-to-whisparr', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            title: sceneTitle,
            scene_id: sceneId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            button.innerHTML = '<i class="fas fa-check"></i> Added!';
            button.className = button.className.replace('btn-outline-success', 'btn-success');
        } else {
            throw new Error(data.error || 'Failed to add to Whisparr');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        button.innerHTML = '<i class="fas fa-times"></i> Failed';
        button.className = button.className.replace('btn-outline-success', 'btn-danger');
    })
    .finally(() => {
        setTimeout(() => {
            button.innerHTML = originalText;
            button.disabled = false;
            button.className = 'btn btn-sm btn-outline-success';
        }, 2000);
    });
}
