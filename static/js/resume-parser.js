let isEditMode = false;

document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.querySelector('input[type="file"]');
    formData.append('resume', fileInput.files[0]);

    try {
        const response = await fetch('/upload-resume', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('result').style.display = 'block';
            const parsedText = document.getElementById('parsedText');
            parsedText.textContent = data.parsed_text;
            formatParsedText(parsedText);
            document.getElementById('error').textContent = '';
            initializeEditableElements();
        } else {
            document.getElementById('error').textContent = data.error || 'Upload failed';
            document.getElementById('result').style.display = 'none';
        }
    } catch (error) {
        document.getElementById('error').textContent = 'Error uploading file';
        document.getElementById('result').style.display = 'none';
    }
});

function formatParsedText(element) {
    let text = element.textContent;
    
    // Format section titles
    text = text.replace(/^(.+)\n={3,}$/gm, '<div class="resume-section"><h2 class="section-title">$1</h2><div class="section-content">');
    
    // Format bullet points
    text = text.replace(/^[•]\s*(.*)/gm, '<div class="bullet-point" data-original="$1">• $1</div>');
    
    // Add spacing between sections
    text = text.replace(/\n\n/g, '</div></div>');
    
    element.innerHTML = text;
}

function initializeEditableElements() {
    const editModeBtn = document.getElementById('editMode');
    const saveChangesBtn = document.getElementById('saveChanges');
    
    editModeBtn.addEventListener('click', toggleEditMode);
    saveChangesBtn.addEventListener('click', saveChanges);
    
    const bulletPoints = document.querySelectorAll('.bullet-point');
    bulletPoints.forEach(bullet => {
        bullet.addEventListener('click', function() {
            if (!isEditMode) return;
            
            if (!this.classList.contains('editing')) {
                makeEditable(this);
            }
        });
    });
}

function toggleEditMode() {
    isEditMode = !isEditMode;
    const editModeBtn = document.getElementById('editMode');
    const saveChangesBtn = document.getElementById('saveChanges');
    const bulletPoints = document.querySelectorAll('.bullet-point');
    
    if (isEditMode) {
        editModeBtn.textContent = 'Exit Edit Mode';
        saveChangesBtn.style.display = 'inline-block';
        bulletPoints.forEach(bullet => bullet.classList.add('editable'));
    } else {
        editModeBtn.textContent = 'Toggle Edit Mode';
        saveChangesBtn.style.display = 'none';
        bulletPoints.forEach(bullet => {
            bullet.classList.remove('editable', 'editing');
            const controls = bullet.querySelector('.edit-controls');
            if (controls) controls.remove();
        });
    }
}

function makeEditable(element) {
    element.classList.add('editing');
    const originalText = element.getAttribute('data-original');
    
    const controls = document.createElement('div');
    controls.className = 'edit-controls';
    controls.innerHTML = `
        <textarea class="editable-field">${originalText}</textarea>
        <button onclick="saveEdit(this.parentElement.parentElement)">Save</button>
        <button onclick="cancelEdit(this.parentElement.parentElement)">Cancel</button>
    `;
    
    element.appendChild(controls);
}

function saveEdit(element) {
    const textarea = element.querySelector('textarea');
    const newText = textarea.value;
    element.setAttribute('data-original', newText);
    element.innerHTML = `• ${newText}`;
    element.classList.remove('editing');
}

function cancelEdit(element) {
    const originalText = element.getAttribute('data-original');
    element.innerHTML = `• ${originalText}`;
    element.classList.remove('editing');
}

function saveChanges() {
    // Here you can add functionality to save all changes
    const bulletPoints = document.querySelectorAll('.bullet-point');
    const updatedContent = Array.from(bulletPoints).map(bullet => ({
        original: bullet.getAttribute('data-original'),
        current: bullet.textContent.replace('• ', '')
    }));
    
    console.log('Saved changes:', updatedContent);
    // You can send this data to the backend if needed
} 