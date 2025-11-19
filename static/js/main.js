const uploadArea = document.getElementById('uploadArea');
const videoInput = document.getElementById('videoInput');
const videoPreview = document.getElementById('videoPreview');
const previewVideo = document.getElementById('previewVideo');
const uploadSection = document.getElementById('uploadSection');
const loadingSection = document.getElementById('loadingSection');
const resultSection = document.getElementById('resultSection');
const analyzeBtn = document.getElementById('analyzeBtn');
const changeVideoBtn = document.getElementById('changeVideoBtn');
const analyzeAnotherBtn = document.getElementById('analyzeAnotherBtn');
const fileName = document.getElementById('fileName');
const progressFill = document.getElementById('progressFill');

let selectedFile = null;

// Upload area click
uploadArea.addEventListener('click', () => {
    videoInput.click();
});

// File input change
videoInput.addEventListener('change', (e) => {
    handleFile(e.target.files[0]);
});

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('video/')) {
        handleFile(file);
    } else {
        alert('Please drop a valid video file');
    }
});

function handleFile(file) {
    if (!file) return;
    
    selectedFile = file;
    fileName.textContent = file.name;
    
    // Create video preview
    const url = URL.createObjectURL(file);
    previewVideo.src = url;
    
    // Show preview, hide upload area
    uploadArea.style.display = 'none';
    videoPreview.style.display = 'block';
}

// Change video button
changeVideoBtn.addEventListener('click', () => {
    selectedFile = null;
    previewVideo.src = '';
    videoPreview.style.display = 'none';
    uploadArea.style.display = 'block';
    videoInput.value = '';
});

// Analyze button
analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) {
        alert('Please select a video file first');
        return;
    }
    
    // Show loading, hide other sections
    uploadSection.style.display = 'none';
    resultSection.style.display = 'none';
    loadingSection.style.display = 'block';
    
    // Simulate progress
    let progress = 0;
    const progressInterval = setInterval(() => {
        progress += 10;
        if (progress <= 90) {
            progressFill.style.width = progress + '%';
        }
    }, 200);
    
    try {
        const formData = new FormData();
        formData.append('video', selectedFile);
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        clearInterval(progressInterval);
        progressFill.style.width = '100%';
        
        const result = await response.json();
        
        if (result.error) {
            throw new Error(result.error);
        }
        
        // Show results
        displayResults(result);
        
    } catch (error) {
        clearInterval(progressInterval);
        loadingSection.style.display = 'none';
        alert('Error analyzing video: ' + error.message);
        uploadSection.style.display = 'block';
    }
});

function displayResults(result) {
    const resultCard = document.getElementById('resultCard');
    const resultIcon = document.getElementById('resultIcon');
    const resultTitle = document.getElementById('resultTitle');
    const resultMessage = document.getElementById('resultMessage');
    const confidenceValue = document.getElementById('confidenceValue');
    const confidenceFill = document.getElementById('confidenceFill');
    const resultDetails = document.getElementById('resultDetails');
    
    const isDeepfake = result.is_deepfake;
    const confidence = Math.round(result.confidence * 100);
    
    // Set icon and colors
    if (isDeepfake) {
        resultIcon.textContent = '⚠️';
        resultTitle.textContent = 'Deepfake Detected';
        resultTitle.style.color = '#f44336';
        resultMessage.textContent = 'This video appears to be a deepfake with ' + confidence + '% confidence.';
        confidenceFill.className = 'confidence-fill deepfake';
    } else {
        resultIcon.textContent = '✅';
        resultTitle.textContent = 'Authentic Video';
        resultTitle.style.color = '#4caf50';
        resultMessage.textContent = 'This video appears to be authentic with ' + confidence + '% confidence.';
        confidenceFill.className = 'confidence-fill authentic';
    }
    
    confidenceValue.textContent = confidence;
    confidenceFill.style.width = confidence + '%';
    
    // Display details
    if (result.details) {
        let detailsHTML = '<h3>Analysis Details</h3>';
        detailsHTML += `<div class="detail-item"><span class="detail-label">Frames Analyzed:</span><span class="detail-value">${result.frames_analyzed || 'N/A'}</span></div>`;
        detailsHTML += `<div class="detail-item"><span class="detail-label">Deepfake Score:</span><span class="detail-value">${(result.score * 100).toFixed(1)}%</span></div>`;
        
        if (result.details.color_variance) {
            detailsHTML += `<div class="detail-item"><span class="detail-label">Color Variance:</span><span class="detail-value">${result.details.color_variance.toFixed(2)}</span></div>`;
        }
        if (result.details.edge_density) {
            detailsHTML += `<div class="detail-item"><span class="detail-label">Edge Density:</span><span class="detail-value">${result.details.edge_density.toFixed(3)}</span></div>`;
        }
        if (result.details.consistency !== undefined) {
            detailsHTML += `<div class="detail-item"><span class="detail-label">Frame Consistency:</span><span class="detail-value">${result.details.consistency.toFixed(2)}</span></div>`;
        }
        
        resultDetails.innerHTML = detailsHTML;
    } else {
        resultDetails.innerHTML = '';
    }
    
    // Show result section
    loadingSection.style.display = 'none';
    resultSection.style.display = 'block';
}

// Analyze another button
analyzeAnotherBtn.addEventListener('click', () => {
    selectedFile = null;
    previewVideo.src = '';
    videoPreview.style.display = 'none';
    uploadArea.style.display = 'block';
    resultSection.style.display = 'none';
    uploadSection.style.display = 'block';
    videoInput.value = '';
    progressFill.style.width = '0%';
});
