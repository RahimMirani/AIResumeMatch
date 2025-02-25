document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let sectionCounter = 0;
    let entryCounter = 0;
    let pointCounter = 0;
    
    // DOM elements
    const sectionsContainer = document.getElementById('sections-container');
    const addSectionBtn = document.getElementById('addSectionBtn');
    const sectionTemplate = document.getElementById('section-template').innerHTML;
    const entryTemplate = document.getElementById('entry-template').innerHTML;
    const pointTemplate = document.getElementById('point-template').innerHTML;
    
    // Personal info fields
    const nameField = document.getElementById('name');
    const emailField = document.getElementById('email');
    const phoneField = document.getElementById('phone');
    const locationField = document.getElementById('location');
    
    // Add event listeners for personal info fields
    [nameField, emailField, phoneField, locationField].forEach(field => {
        field.addEventListener('input', updatePreview);
    });
    
    // Add section button
    addSectionBtn.addEventListener('click', function() {
        addSection();
    });
    
    // Handle form submission
    document.getElementById('uploadForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        const formData = new FormData();
        const fileInput = document.querySelector('input[type="file"]');
        formData.append('resume', fileInput.files[0]);
        
        try {
            const response = await fetch('/upload-resume', {
                method: 'POST',
                body: formData
            });
            
            if (!response.ok) {
                throw new Error('Upload failed');
            }
            
            const data = await response.json();
            if (data.parsed_data) {
                populateEditor(data.parsed_data);
                updatePreview();
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Error uploading resume: ' + error.message);
        }
    });
    
    // Function to add a new section
    function addSection() {
        const sectionId = 'section-' + sectionCounter++;
        const sectionHtml = sectionTemplate.replace(/{id}/g, sectionId);
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = sectionHtml;
        const sectionElement = tempDiv.firstElementChild;
        
        sectionsContainer.appendChild(sectionElement);
        
        // Add event listeners
        const deleteBtn = sectionElement.querySelector('.delete-section-btn');
        deleteBtn.addEventListener('click', function() {
            sectionElement.remove();
            updatePreview();
        });
        
        const addEntryBtn = sectionElement.querySelector('.add-entry-btn');
        addEntryBtn.addEventListener('click', function() {
            addEntry(sectionElement.querySelector('.entries-container'));
        });
        
        const titleInput = sectionElement.querySelector('.section-title');
        titleInput.addEventListener('input', updatePreview);
        
        // Add first entry
        addEntry(sectionElement.querySelector('.entries-container'));
        
        updatePreview();
        return sectionElement;
    }
    
    // Function to add a new entry
    function addEntry(container) {
        const entryId = 'entry-' + entryCounter++;
        const entryHtml = entryTemplate.replace(/{id}/g, entryId);
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = entryHtml;
        const entryElement = tempDiv.firstElementChild;
        
        container.appendChild(entryElement);
        
        // Add event listeners
        const deleteBtn = entryElement.querySelector('.delete-entry-btn');
        deleteBtn.addEventListener('click', function() {
            entryElement.remove();
            updatePreview();
        });
        
        const addPointBtn = entryElement.querySelector('.add-point-btn');
        addPointBtn.addEventListener('click', function() {
            addPoint(entryElement.querySelector('.points-container'));
        });
        
        // Add input event listeners
        const inputs = entryElement.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', updatePreview);
        });
        
        // Add first point
        addPoint(entryElement.querySelector('.points-container'));
        
        updatePreview();
        return entryElement;
    }
    
    // Function to add a new bullet point
    function addPoint(container) {
        const pointId = 'point-' + pointCounter++;
        const pointHtml = pointTemplate.replace(/{id}/g, pointId);
        
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = pointHtml;
        const pointElement = tempDiv.firstElementChild;
        
        container.appendChild(pointElement);
        
        // Add event listeners
        const deleteBtn = pointElement.querySelector('.delete-point-btn');
        deleteBtn.addEventListener('click', function() {
            pointElement.remove();
            updatePreview();
        });
        
        const textarea = pointElement.querySelector('textarea');
        textarea.addEventListener('input', updatePreview);
        
        updatePreview();
        return pointElement;
    }
    
    // Function to populate editor with parsed data
    function populateEditor(data) {
        // Clear existing sections
        sectionsContainer.innerHTML = '';
        
        // Set personal info
        const personalInfo = data.personal_info;
        nameField.value = personalInfo.name || '';
        emailField.value = personalInfo.contact.email || '';
        phoneField.value = personalInfo.contact.phone || '';
        locationField.value = personalInfo.contact.location || '';
        
        // Set LinkedIn and GitHub if they exist
        if (document.getElementById('linkedin')) {
            document.getElementById('linkedin').value = personalInfo.contact.linkedin || '';
        }
        if (document.getElementById('github')) {
            document.getElementById('github').value = personalInfo.contact.github || '';
        }
        
        // Add sections
        data.sections.forEach(section => {
            const sectionElement = addSection();
            sectionElement.querySelector('.section-title').value = section.title;
            
            // Clear default entry
            sectionElement.querySelector('.entries-container').innerHTML = '';
            
            // Add entries
            section.entries.forEach(entry => {
                const entryContainer = sectionElement.querySelector('.entries-container');
                const entryElement = addEntry(entryContainer);
                
                entryElement.querySelector('.company').value = entry.company || '';
                entryElement.querySelector('.location').value = entry.location || '';
                entryElement.querySelector('.duration').value = entry.duration || '';
                entryElement.querySelector('.position').value = entry.position || '';
                
                // Clear default point
                entryElement.querySelector('.points-container').innerHTML = '';
                
                // Add points
                if (entry.points && entry.points.length > 0) {
                    entry.points.forEach(point => {
                        const pointContainer = entryElement.querySelector('.points-container');
                        const pointElement = addPoint(pointContainer);
                        pointElement.querySelector('textarea').value = point;
                    });
                }
            });
        });
        
        // Update preview
        updatePreview();
    }
    
    // Function to update preview
    function updatePreview() {
        const previewContainer = document.getElementById('resume-preview');
        
        // Get personal info
        const name = nameField.value;
        const email = emailField.value;
        const phone = phoneField.value;
        const location = locationField.value;
        const linkedin = document.getElementById('linkedin') ? document.getElementById('linkedin').value : '';
        const github = document.getElementById('github') ? document.getElementById('github').value : '';
        
        // Start building HTML
        let html = `
            <h1>${name}</h1>
            <div class="contact-info">
                ${email ? email : ''} 
                ${email && phone ? ' | ' : ''} 
                ${phone ? phone : ''} 
                ${(email || phone) && location ? ' | ' : ''} 
                ${location ? location : ''}
                ${(email || phone || location) && (linkedin || github) ? '<br>' : ''}
                ${linkedin ? `<a href="https://${linkedin}">${linkedin}</a>` : ''}
                ${linkedin && github ? ' | ' : ''}
                ${github ? `<a href="https://${github}">${github}</a>` : ''}
            </div>
        `;
        
        // Get sections
        const sections = document.querySelectorAll('.editor-section[data-section-id]');
        sections.forEach(section => {
            const title = section.querySelector('.section-title').value;
            if (!title) return;
            
            html += `<h2>${title}</h2>`;
            
            // Get entries
            const entries = section.querySelectorAll('.entry[data-entry-id]');
            entries.forEach(entry => {
                const company = entry.querySelector('.company').value;
                const position = entry.querySelector('.position').value;
                const entryLocation = entry.querySelector('.location').value;
                const duration = entry.querySelector('.duration').value;
                
                if (!company && !position) return;
                
                html += `<div class="preview-entry">`;
                
                // Entry header with better formatting
                html += `<div class="entry-header">`;
                if (company) {
                    html += `<span class="company">${company}</span>`;
                }
                
                // Right-aligned location and duration
                if (entryLocation || duration) {
                    html += `<span style="text-align: right;">`;
                    if (entryLocation) {
                        html += `<span class="location">${entryLocation}</span>`;
                    }
                    if (entryLocation && duration) {
                        html += ` | `;
                    }
                    if (duration) {
                        html += `<span class="duration">${duration}</span>`;
                    }
                    html += `</span>`;
                }
                html += `</div>`;
                
                // Position
                if (position) {
                    html += `<div class="position">${position}</div>`;
                }
                
                // Points
                const points = entry.querySelectorAll('.point[data-point-id] textarea');
                if (points.length > 0) {
                    html += `<ul>`;
                    points.forEach(point => {
                        const pointText = point.value.trim();
                        if (pointText) {
                            html += `<li>${pointText}</li>`;
                        }
                    });
                    html += `</ul>`;
                }
                
                html += `</div>`;
            });
        });
        
        previewContainer.innerHTML = html;
    }
    
    // Initialize with empty sections
    addSection();
}); 