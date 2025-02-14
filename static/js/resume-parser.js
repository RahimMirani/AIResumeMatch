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
    
    // Format section titles (lines followed by ===)
    text = text.replace(/^(.+)\n={3,}$/gm, '<h2 class="section-title">$1</h2><div class="section-content">');
    
    // Format bullet points
    text = text.replace(/^[•]\s*(.*)/gm, '<div class="bullet-point">• $1</div>');
    
    // Add spacing between sections
    text = text.replace(/\n\n/g, '</div><br>');
    
    // Ensure all sections are closed
    text += '</div>';
    
    element.innerHTML = text;
} 