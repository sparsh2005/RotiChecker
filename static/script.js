document.addEventListener('DOMContentLoaded', () => {
    // Initialize Lucide icons
    lucide.createIcons();
  
    // DOM Elements
    const fileInput = document.getElementById('fileInput');
    const uploadArea = document.getElementById('uploadArea');
    const uploadPlaceholder = document.getElementById('uploadPlaceholder');
    const imagePreview = document.getElementById('imagePreview');
    const uploadedImage = document.getElementById('uploadedImage');
    const newImageBtn = document.getElementById('newImageBtn');
    const analysisResults = document.getElementById('analysisResults');
    const roundnessScore = document.getElementById('roundnessScore');
    const colorScore = document.getElementById('colorScore');
    const totalScore = document.getElementById('totalScore');
    const feedbackText = document.getElementById('feedbackText');
  
    // Event Listeners
    uploadPlaceholder.addEventListener('click', () => fileInput.click());
    newImageBtn.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffb74d';
    });
  
    uploadArea.addEventListener('dragleave', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffe0b2';
    });
  
    uploadArea.addEventListener('drop', (e) => {
      e.preventDefault();
      uploadPlaceholder.style.borderColor = '#ffe0b2';
      const file = e.dataTransfer.files[0];
      if (file && file.type.startsWith('image/')) {
        handleImageUpload(file);
      }
    });
  
    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        handleImageUpload(file);
      }
    });
  
    // Handle image upload
    function handleImageUpload(file) {
      // Show a preview in the UI
      const reader = new FileReader();
      reader.onloadend = () => {
        uploadedImage.src = reader.result;
        uploadPlaceholder.classList.add('hidden');
        imagePreview.classList.remove('hidden');
        // We'll reveal the analysis section after we get server results
        // but for a smooth user experience, let's keep the analysis visible:
        analysisResults.classList.remove('hidden');
  
        // Actually send the file to the server for real analysis
        sendImageToServer(file);
      };
      reader.readAsDataURL(file);
    }
  
    function sendImageToServer(file) {
      const formData = new FormData();
      formData.append('roti_image', file);
  
      fetch('/upload', {
        method: 'POST',
        body: formData
      })
      .then(async (response) => {
        if (!response.ok) {
          let errMsg = 'Error uploading image';
          try {
            const errorData = await response.json();
            if (errorData.error) errMsg = errorData.error;
          } catch (err) {}
          throw new Error(errMsg);
        }
        return response.json();
      })
      .then(data => {
        // data: { roundness: ..., color: ..., overall: ... }
        const { roundness, color, overall } = data;
        // Animate scores
        animateScore(roundnessScore, roundness);
        animateScore(colorScore, color);
        animateScore(totalScore, overall);
        // Color them
        updateScoreColor(roundnessScore, roundness);
        updateScoreColor(colorScore, color);
        updateScoreColor(totalScore, overall);
        // Feedback
        updateFeedback(overall);
      })
      .catch(error => {
        console.error('Upload error:', error);
        feedbackText.textContent = 'Oops! ' + error.message;
        analysisResults.classList.remove('hidden');
      });
    }
  
    // Animate score counting up
    function animateScore(element, target) {
      let current = 0;
      const increment = target / 50; 
      const animation = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(animation);
        }
        element.textContent = Math.floor(current) + '%';
      }, 20);
    }
  
    // Update score color based on value
    function updateScoreColor(element, score) {
      element.classList.remove('good', 'medium', 'poor');
      if (score >= 90) {
        element.classList.add('good');
      } else if (score >= 70) {
        element.classList.add('medium');
      } else {
        element.classList.add('poor');
      }
    }
  
    // Update feedback message
    function updateFeedback(score) {
      let message;
      if (score >= 90) {
        message = "Perfect roti! You're a master chef! 👨‍🍳";
      } else if (score >= 70) {
        message = "Good effort! Keep practicing for perfection. 👍";
      } else {
        message = "Needs improvement. Try rolling more evenly. 💪";
      }
      feedbackText.textContent = message;
    }
  });